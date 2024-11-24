import os
import dotenv

from langchain_groq import ChatGroq
from chunking import query_embeddings

def generate_chain():
    dotenv.load_dotenv()

    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=1,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # other params...
    )

    # Format the prompt with the retrieved context and user query
    # formatted_prompt = rag_prompt.format_prompt(**inputs).to_messages()

    # print(formatted_prompt)

    from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

    # System message sets the assistant's role and behavior
    system_message = SystemMessagePromptTemplate.from_template(
        "INSTRUCTIONS"
        "Answer the users as detailed as possible QUESTION using the DOCUMENT text above. Keep your answer ground in the facts of the DOCUMENT. If the DOCUMENT doesn’t contain the facts to answer the QUESTION return NONE, leave the references at the end'"
    )

    # Human message takes the user's query
    human_message = HumanMessagePromptTemplate.from_template(
        "QUESTION: {query}\n\nDOCUMENT: {context}"
    )

    # Combine into a chat prompt
    rag_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    chain = rag_prompt | llm
    return chain

if __name__ == "__main__":
    # Example of input data
    results = query_embeddings("What is the SCL-90-R?")
    docs = list(map(lambda i: f"DOC{i[0]+1}: {i[1].page_content}", enumerate(results)))
    print("\n".join(docs))
    inputs = {
        "query": "What is the SCL-90-R?",
        "context": "\n".join(docs)
    }
    chain = generate_chain()
    ai_msg = chain.invoke(inputs)
    print('=======================================')
    print(ai_msg.content)
