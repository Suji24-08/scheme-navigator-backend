from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
response = llm.invoke("Reply with exactly: setup working")

print("Response:", response.content)