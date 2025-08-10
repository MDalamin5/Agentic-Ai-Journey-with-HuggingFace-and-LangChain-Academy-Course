from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import os
from autogen_agentchat.messages import TextMessage
from autogen_core.models import UserMessage
from dotenv import load_dotenv
import asyncio

load_dotenv()

model_client = OllamaChatCompletionClient(model="qwen2.5:14b")

async def main():
    response = await model_client.create(
        [UserMessage(content="Hi, Nice to meet you!", source="user")]
    )
    print(response)
    

if __name__ == "__main__":
    asyncio.run(main())
