[Skip to main content](https://docs.runllm.com/sdk/#__docusaurus_skipToContent_fallback)
[ ![RunLLM Logo](https://docs.runllm.com/img/runllm-blue.png)![RunLLM Logo](https://docs.runllm.com/img/runllm-blue.png) **RunLLM**](https://docs.runllm.com/)[Documentation](https://docs.runllm.com/)
[Home](https://runllm.com)[Sign Up](https://app.runllm.com)[Log In](https://app.runllm.com)
  * [RunLLM Overview](https://docs.runllm.com/)
  * [Quickstart](https://docs.runllm.com/quickstart/)
  * [Data Sources](https://docs.runllm.com/data-sources/)
  * [Deployments](https://docs.runllm.com/deployments/)
  * [Python SDK](https://docs.runllm.com/sdk/)
    * [Use Cases](https://docs.runllm.com/sdk/recipes/)
    * [API Reference](https://docs.runllm.com/sdk/api/)
  * [Chat UX](https://docs.runllm.com/chat-ux/)
  * [Instant Learning](https://docs.runllm.com/instant-learning/)
  * [Documentation Issues](https://docs.runllm.com/issues/)
  * [RunLLM Dashboard](https://docs.runllm.com/dashboard/)
  * [AutoDocs](https://docs.runllm.com/autodocs/)
  * [Under the Hood](https://docs.runllm.com/how-it-works/)
  * [API](https://docs.runllm.com/api/)
  * [Frequently Asked Questions](https://docs.runllm.com/faqs/)
  * [Release Notes](https://docs.runllm.com/release-notes/)


  * [](https://docs.runllm.com/)
  * Python SDK


On this page
# Python SDK
Please reach out to us at support@runllm.com if you're interested in deploying with us.
Click the **"Ask AI"** button in the _bottom right corner_ of this page and ask our AI agent to validate your use case (and write the code for you)!
### Introduction[​](https://docs.runllm.com/sdk/#introduction "Direct link to Introduction")
Every support team works a little differently: different channels, different SLAs, different triage flows and tagging schemes, different classes of tickets. That’s not a bad thing! Every support workflow and strategy should reflect the shape of your business. That's why we built the **RunLLM Support Agent SDK** : to give teams full control over how AI fits into your support stack, without requiring you to rebuild everything from scratch.
The SDK gives you:
  * **Prebuilt support operations** powered by RunLLM’s reasoning engine — including answering questions, tagging and triaging, summarizing, escalating, and syncing across tools.
  * **Access to RunLLM’s integrations** — Slack, Zendesk, Salesforce, internal docs, and codebases — without dealing with custom APIs.
  * **Custom workflow logic** defined in lightweight Python code, so your agents behave the way you need them to.


With the SDK, you can fully customize your support workflows without rewriting core logic. Most importantly, you don’t need to rebuild the AI primitives we’ve already spent 20+ engineer-years perfecting.
### Installation[​](https://docs.runllm.com/sdk/#installation "Direct link to Installation")
Install the official RunLLM Python SDK:
```
pip install runllm  

```

Once installed, you’re ready to integrate AI-powered support into your app with just a few lines of code.
### Example[​](https://docs.runllm.com/sdk/#example "Direct link to Example")
Let's say you have our RunLLM bot deployed into your Slack workspace already. However, for cases where the agent cannot confidently answer the user's question, you would like to:
  1. Create a Zendesk ticket.
  2. Post a summary of the conversation into the new ticket, with a backlink to the slack thread for context.
  3. Keep the ticket and Slack threads in sync. When a support agent comments on the ticket, that comment will be posted back to the Slack thread, and vice versa.


This entire workflow is just a few lines of python:
```
from runllm import AnswerCategory, SlackListener  
from runllm.decorators import entrypoint  
  
@entrypoint(listeners=[SlackListener(team_id="T19IFLSF23V")])  
defcreate_zendesk_ticket_for_unanswered(agent, event):  
    convo = event.conversation  
    slack_thread = convo.surface  
  
# Answer the user's question directly in the Slack thread.  
    answer = agent.answer(convo)  
    agent.send_to_slack_thread(answer, to=answer)  
  
# If we were unable to answer the question, open a Zendesk ticket.  
if answer.category in[AnswerCategory.UNANSWERED, AnswerCategory.LOW_CONFIDENCE]:  
        summary = agent.summarize(convo)  
  
        ticket = agent.create_zendesk_ticket(  
            convo,  
            domain="myteam.zendesk.com",  
            tags=convo.tags,  
            description=(  
f"Slack thread {slack_thread.link()}\n\n"  
"Conversation Summary: \n\n{summary}"  
)  
)  
  
# The agent will not longer handle this conversation, except to keep  
# both surfaces in sync with each other.      
        agent.terminate(  
            keep_in_sync=[slack_thread, ticket]  
)  

```

Finally, just define a RunLLM client and publish the function. And you're done!
```
from runllm import Client  
  
# You can also set the RUNLLM_API_KEY env variable instead.  
client = Client(api_key="<Your RunLLM API Key>")  
client.publish("my_flow", create_zendesk_ticket_for_unanswered)  

```

[Previous Zendesk](https://docs.runllm.com/deployments/zendesk/)[Next Use Cases](https://docs.runllm.com/sdk/recipes/)
  * [Introduction](https://docs.runllm.com/sdk/#introduction)
  * [Installation](https://docs.runllm.com/sdk/#installation)
  * [Example](https://docs.runllm.com/sdk/#example)


Social Media
  * [X (Twitter)](https://x.com/runllm)
  * [LinkedIn](https://www.linkedin.com/company/runllm)
  * [YouTube](https://www.youtube.com/@RunLLM)


More
  * [Home](https://runllm.com)
  * [Case Studies (coming soon!)](https://docs.runllm.com/sdk/)
  * [Blog](https://runllm.com/blog)


Copyright © 2025 Aqueduct, Inc (d/b/a RunLLM).
