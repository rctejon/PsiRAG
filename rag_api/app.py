from flask import Flask, request, render_template
from llm import generate_chain
from chunking import query_embeddings, download_and_chunk_s3_individual_file, store_embeddings_in_pg

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def ask_llm():
    return render_template('chatbot.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    results = query_embeddings(question)
    docs = list(map(lambda x: f"{x.page_content}", results))
    chain = generate_chain()
    inputs = {
        "query": question,
        "context": "\n".join(docs)
    }
    ai_msg = chain.invoke(inputs)
    return {"answer": ai_msg.content}

@app.route('/add-document', methods=['POST'])
def add_document():
    file_key = request.form['file_key']
    chunks = download_and_chunk_s3_individual_file(file_key)
    store_embeddings_in_pg(chunks)

    return {"answer": "Document added"}

if __name__ == '__main__':
    app.run(debug=True)
