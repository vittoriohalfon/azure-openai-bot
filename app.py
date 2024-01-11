from flask import Flask, request, jsonify
from flask_cors import CORS
from main import main
import logging
import time

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    start_total_time = time.time()
    data = request.json
    user_message = data.get('message')
    chat_id = data.get('chatId')

    if not user_message or not chat_id:
        return jsonify({"reply": "Invalid request"}), 400

    ai_response = main(user_message, chat_id)
    end_total_time = time.time()
    logging.info(f"Total time taken: {end_total_time - start_total_time} seconds")
    return jsonify({"reply": ai_response})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
