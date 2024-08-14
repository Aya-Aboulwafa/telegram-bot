from flask import Flask, jsonify, render_template, request, json
from Telegram_bot_model import llm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this_is_bad_secret_key'
limit_input_tokens=4096
model_path = 'model-q4_K.gguf'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
	# recieve message from the user
	data = request.get_json()

	# ensure message is converted to json if it was recieved as str
	if isinstance(data, str):
		data = json.loads(data)
	
	# extract text of the message
	query = data['message']

	# invoke beluga llm
	llm_answer = llm(query, top_k=40, top_p=0.4, temperature=0.5)
	response = {'message': llm_answer}
	
	return jsonify(response)


if __name__ == "__main__":
	# initialize llm model
	llm = llm
	app.run()
