from flask import Flask, request, render_template
from llm import generate_chain

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
    chain = generate_chain()
    inputs = {
        "query": question,
        "context": "The SCL-S-9 serves to assess a wide range of psychopathologic symptoms with each item belonging to one dimension of the original SCL-90-R (i.e., somatization, obsessive-compulsive, interpersonal sensitivity, depression, anxiety, hostility, phobic anxiety, paranoid ideation, and psychoticism). Each of the nine items of the measure are presented with a 5-point response scale (0 = “none at all” to 4 = “very severe”). Good internal consistency was found for the SCL-S-9 in the investigated sample (α was 0.81 at each measurement point)."
    }
    ai_msg = chain.invoke(inputs)
    return {"answer": ai_msg.content}

if __name__ == '__main__':
    app.run(debug=True)