import os
import uuid
import logging
from openai import AzureOpenAI
from azure.cosmos import CosmosClient

# Setting up basic configuration for logging
logging.basicConfig(level=logging.INFO)

def main(user_message, chat_id):  # Accept user_message and chat_id as arguments
    try:
        # Azure OpenAI credentials
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_api_key = os.getenv('AZURE_OPENAI_KEY')
        api_version = '2023-07-01-preview'

        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version
        )

        # System message for the chatbot
        system_message = "Sei un chatbot presente nel sito di X-Applied AI..."

        # Prepare messages for chat completion (excluding chatId)
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        # Log the message being sent to the OpenAI API
        logging.info(f"Sending messages to OpenAI: {messages}")

        # Get response from Azure OpenAI
        response = client.chat.completions.create(
            model="vittohalfon",
            messages=messages
        )

        ai_response = response.choices[0].message.content

    except Exception as e:
        logging.error(f"Error in interacting with Azure OpenAI: {e}")
        ai_response = "Sorry, there was an error in processing your request."

    try:
        # Cosmos DB credentials and initialization
        cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
        cosmos_key = os.getenv('COSMOS_KEY')
        database_name = 'ChatDB'
        container_name = 'Messages'

        cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = cosmos_client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        # Store chat data in Cosmos DB with the provided chatId
        chat_data = {
            "id": str(uuid.uuid4()),  # Generate a unique ID for each chat record
            "chatId": chat_id,  # Use the provided chatId
            "userMessage": user_message,
            "aiResponse": ai_response
        }
        container.upsert_item(chat_data)

    except Exception as e:
        logging.error(f"Error in interacting with Cosmos DB: {e}")
    
    return ai_response  # Return the AI response