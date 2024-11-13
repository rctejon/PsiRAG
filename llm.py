import os
import dotenv

from langchain_groq import ChatGroq

dotenv.load_dotenv()

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
ai_msg = chain.invoke(
    {
        "input_language": "English",
        "output_language": "Spanish",
        "input": "I love programming.",
    }
)
print(ai_msg)
print(ai_msg.content)
