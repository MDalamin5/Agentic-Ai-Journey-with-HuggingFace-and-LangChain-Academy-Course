from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",	  },
)
import asyncio

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
from langgraph.prebuilt import create_react_agent

llm = ChatGroq(
    model=os.getenv("QWEN_MODEL"),
    temperature=0.2
)

async_browser = create_async_playwright_browser()
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()
# print(tools)
# print(llm.invoke("Test line"))

agent_chain = create_react_agent(model=llm, tools=tools)
print("==I'm Hare==")

async def main():
    print("==Start to execuation agent==")
    result = await agent_chain.ainvoke(
    {"messages": [("user", "What are the headers on langchain.com?")]}
    )
    print(result)
    
asyncio.run(main())