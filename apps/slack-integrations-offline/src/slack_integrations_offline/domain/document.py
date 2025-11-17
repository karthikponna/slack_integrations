import json

from pathlib import Path
from pydantic import BaseModel, Field

from src.slack_integrations_offline.utils import generate_random_hex


class DocumentMetadata(BaseModel):
    """Metadata container for document information.
    
    Attributes:
        id: Unique identifier for the document.
        url: Source URL of the document.
        title: Title of the document.
        properties: Additional metadata properties as key-value pairs.
    """

    id: str
    url: str
    title: str
    properties: dict


class Document(BaseModel):
    """Core document model containing content, metadata, and optional analysis results.
    
    Represents a crawled or extracted document with its content, metadata, summary, and relationships.
    
    Attributes:
        id: Unique identifier for the document, auto-generated as 32-character hex string.
        metadata: DocumentMetadata object containing document information.
        content: Main text content of the document.
        summary: Optional generated summary of the document content.
        content_quality_score: Optional quality score for the content.
        child_urls: List of child URLs discovered within the document.
    """

    id: str = Field(default_factory=lambda: generate_random_hex(length=32))
    metadata: DocumentMetadata
    content: str
    summary: str | None = None
    content_quality_score: float | None = None
    child_urls: list[str] = Field(default_factory=list)


    @classmethod
    def from_file(cls, file_path: Path) -> "Document":
        """Load a Document instance from a JSON file.
    
        Args:
            file_path: Path to the JSON file containing document data.
        
        Returns:
            Document: Document instance loaded from the file.
        """

        json_data = file_path.read_text(encoding="utf-8")

        return cls.model_validate_json(json_data)


    def write(
        self, output_dir: Path, also_save_as_txt: bool = False,
    ) -> None:
        """Write the document to disk as JSON and optionally as plain text.
    
        Args:
            output_dir: Directory path where files will be written.
            also_save_as_txt: Whether to also save content as a separate text file. Defaults to False.
        
        Returns:
            None
        """
        
        json_page = self.model_dump()

        output_file = output_dir/f"{self.id}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                json_page,
                f,
                indent=4,
                ensure_ascii=False,
            )

        if also_save_as_txt:
            txt_path = output_file.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self.content)

        
    def add_summary(self, summary: str) -> "Document":
        """Add a summary to the document and return the updated instance.
    
        Args:
            summary: Summary text to add to the document.
        
        Returns:
            Document: The document instance with the added summary.
        """

        self.summary = summary

        return self

    def __eq__(self, other: object) -> bool:
        """Check equality based on document ID.
    
        Args:
            other: Object to compare with.
        
        Returns:
            bool: True if both documents have the same ID, False otherwise.
        """
        
        if not isinstance(other, Document):
            return False
        return self.id == other.id
    

    def __hash__(self) -> int:
        """Generate hash based on document ID for use in sets and dictionaries.
    
        Returns:
            int: Hash value of the document ID.
        """
        return hash(self.id)