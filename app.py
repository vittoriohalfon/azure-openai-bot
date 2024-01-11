from flask import Flask, request, jsonify
from flask_cors import CORS
from main import main
import logging
import time

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    chat_id = data.get('chatId')

    if not user_message or not chat_id:
        logging.error(f"Invalid request with data: {data}")
        return jsonify({"reply": "Invalid request"}), 400

    logging.info(f"Received chat request with chat_id {chat_id}")

    try:
        start_total_time = time.time()
        ai_response = main(user_message, chat_id)
        end_total_time = time.time()
        logging.info(f"Processed chat request for chat_id {chat_id} in {end_total_time - start_total_time} seconds")
        return jsonify({"reply": ai_response})

    except Exception as e:
        logging.error(f"Error processing request for chat_id {chat_id}: {e}", exc_info=True)
        return jsonify({"reply": "Error processing your request"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
