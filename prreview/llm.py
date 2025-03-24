from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAI

def llm_gemini():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    return llm

llm = OpenAI()