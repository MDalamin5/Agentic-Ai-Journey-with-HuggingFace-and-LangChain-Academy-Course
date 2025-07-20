
import asyncio



from browser_use.llm import ChatGroq
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()
import os

import asyncio
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
planner_llm = ChatGroq(model='meta-llama/llama-4-scout-17b-16e-instruct')

async def main():
    
    
    agent = Agent(
        task="go to linkedin.com and click on Sign in button and close the task.",
        # message_context="when you get the job list. Collect 10 job title and company name only.",
        llm=llm,
        planner_llm=planner_llm,
        planner_interval=3
    )
    result = await agent.run()
    print("="*20)
    print(result)

asyncio.run(main())