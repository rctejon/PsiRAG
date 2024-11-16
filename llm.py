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

# Format the prompt with the retrieved context and user query
# formatted_prompt = rag_prompt.format_prompt(**inputs).to_messages()

# print(formatted_prompt)

from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

# System message sets the assistant's role and behavior
system_message = SystemMessagePromptTemplate.from_template(
    "INSTRUCTIONS"
    "Answer the users as detailed as possible QUESTION using the DOCUMENT text above. Keep your answer ground in the facts of the DOCUMENT. If the DOCUMENT doesn’t contain the facts to answer the QUESTION return NONE'"
)

# Human message takes the user's query
human_message = HumanMessagePromptTemplate.from_template(
    "QUESTION: {query}\n\nDOCUMENT: {context}"
)

# Combine into a chat prompt
rag_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

# Example of input data
inputs = {
    "query": "What is the SCL-90-R?",
    "context": "The SCL-S-9 serves to assess a wide range of psychopathologic symptoms with each item belonging to one dimension of the original SCL-90-R (i.e., somatization, obsessive-compulsive, interpersonal sensitivity, depression, anxiety, hostility, phobic anxiety, paranoid ideation, and psychoticism). Each of the nine items of the measure are presented with a 5-point response scale (0 = “none at all” to 4 = “very severe”). Good internal consistency was found for the SCL-S-9 in the investigated sample (α was 0.81 at each measurement point)."
}

chain = rag_prompt | llm
ai_msg = chain.invoke(inputs)
# print(ai_msg)
print(ai_msg.content)
