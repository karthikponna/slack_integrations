import os
import asyncio
import psutil

from litellm import acompletion

from loguru import logger
from tqdm.asyncio import tqdm

from src.slack_integrations_offline.domain.document import Document


class SummarizationAgent:
    """Agent for generating concise summaries of technical documentation using language models.
    
    Processes documents asynchronously with configurable concurrency limits 
    and automatic retry logic for failed summarizations.
    
    Attributes:
        max_characters: Maximum character length for generated summaries.
        model_id: Identifier for the language model to use.
        max_concurrent_requests: Maximum number of concurrent API requests.
    """
    
    SYSTEM_PROMPT_TEMPLATE = """
    You are a helpful assistant specialized in summarizing technical documentation.

    Your task is to create a clear, concise TL;DR summary in markdown format.

    **Include:**
    - Titles of sections and sub-sections
    - Key concepts and explanations
    - Essential technical details
    - Main findings and insights

    **Exclude:**
    - Navigation elements and sidebars
    - Footer content and cookie policies
    - Privacy policies and HTTP errors
    - Any other irrelevant metadata

    **Format Requirements:**
    - Return clean markdown format
    - Use appropriate headers (##, ###)
    - Preserve the original writing style where relevant
    - Highlight the most significant insights and implications
    """

    USER_PROMPT_TEMPLATE = """
    Please summarize the following document content:

    Document:
    {content}

    Generate a concise TL;DR summary (maximum {characters} characters) following the guidelines provided.
    """

    def __init__(
        self,
        max_characters: int, 
        model_id: str = "gpt-4o-mini",
        max_concurrent_requests: int = 10,
    ) -> None:
        self.max_characters = max_characters
        self.model_id = model_id
        self.max_concurrent_requests = max_concurrent_requests


    def __call__(
        self,
        documents: Document | list[Document],
        temperature: float = 0.0,
    ) -> Document | list[Document]:
        
        is_single_document = isinstance(documents, Document)
        docs_list = [documents] if is_single_document else documents

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            results = asyncio.run(self.__summarize_batch(docs_list, temperature))
        else:
            results = loop.run_until_complete(self.__summarize_batch(docs_list, temperature))

        return results[0] if is_single_document else results

    

    async def __summarize_batch(
        self,
        documents: list[Document],
        temperature: float = 0.0,
    ) -> list[Document]:
        
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss
        total_docs = len(documents)

        logger.debug(
            f"Starting summarization batch with {self.max_concurrent_requests} concurrent requests. "
            f"Current process memory usage: {start_memory // (1024 * 1024)} MB"
        )

        summarized_documents = await self.__process_batch(
            documents, temperature, await_time_seconds=7
        )

        documents_with_summaries = [
            doc for doc in summarized_documents if doc.summary is not None
        ]

        documents_without_summaries = [
            doc for doc in documents if doc.summary is None
        ]

        if documents_without_summaries:
            logger.info(
                f"Retrying {len(documents_without_summaries)} failed documents with increased await time..."
            )

            retry_results = await self.__process_batch(
                documents_without_summaries, temperature, await_time_seconds=20
            )
            documents_with_summaries += retry_results

        end_memory = process.memory_info().rss
        memory_diff = end_memory - start_memory
        logger.debug(
            f"Summarization batch completed. "
            f"Final process memory usage: {end_memory // (1024 * 1024)} MB, "
            f"Memory diff: {memory_diff // (1024 * 1024)} MB"
        )

        success_count = len(documents_with_summaries)
        failed_count = total_docs - success_count
        logger.info(
            f"Summarization completed: "
            f"{success_count}/{total_docs} succeeded ✓ | "
            f"{failed_count}/{total_docs} failed ✗"
        )

        return documents_with_summaries



    async def __process_batch(
        self,
        documents: list[Document],
        temperature: float = 0.0,
        await_time_seconds: int = 7,
    ) -> list[Document]:
        
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        tasks = [
            self.__summarize(
                document=document, temperature=temperature, semaphore=semaphore, await_time_seconds=await_time_seconds
            )
            for document in documents
        ]

        results = []

        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(documents),
            desc="Processing documents",
            unit="docs",
        ):
            result = await coro
            results.append(result)

        return results



    async def __summarize(
        self,
        document: Document,
        temperature: float = 0.0,
        semaphore: asyncio.Semaphore | None = None,
        await_time_seconds: int = 7,
    ) -> Document:
        
        async def __process_documents():
            try:
                response = await acompletion(
                    model = self.model_id,
                    messages =[
                        {
                            "role": "system",
                            "content": self.SYSTEM_PROMPT_TEMPLATE
                        },
                        {
                            "role": "user",
                            "content": self.USER_PROMPT_TEMPLATE.format(
                                content=document.content, characters=self.max_characters
                            )
                        },
                    ],
                    stream = False,
                    temperature = temperature,
                )

                await asyncio.sleep(await_time_seconds)

                if not response.choices:
                    logger.warning(f"No summary generated for document {document.id}")
                    return document
                
                summary: str = response.choices[0].message.content

                return document.add_summary(summary)

            except Exception as e:
                logger.warning(f"Failed to summarize document {document.id}: {str(e)}")
                return document
            
        
        if semaphore:
            async with semaphore:
                return await __process_documents()
            
        return await __process_documents()