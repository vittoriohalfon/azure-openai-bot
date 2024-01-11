import os
import uuid
import logging
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
import time

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

        # Cosmos DB credentials and initialization
        cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
        cosmos_key = os.getenv('COSMOS_KEY')
        database_name = 'ChatDB'
        container_name = 'Messages'

        cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = cosmos_client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        # Check if the conversation already exists
        existing_conversation = None
        try:
            existing_conversation = container.read_item(item=str(chat_id), partition_key=str(chat_id))
        except Exception as e:
            logging.info("No existing conversation found, starting a new one.")

        messages = []

        # If no existing conversation, add system message
        if not existing_conversation:
            system_message = {
                "role": "system",
                "content": "RISPONDI NELLA LINGUA IN CUI TI VIENE CHIESTA UNA DOMANDA. Sei un chatbot presente nel sito di X-Applied AI. X-Applied AI è una società di consulenza che aiuta le aziende a sfruttare il potere dell'Intelligenza Artificiale (specialmente generativa) per risolvere i loro problemi di business. Se ti viene chiesta una domanda da parte di un potenziale cliente (visitatore del sito), rispondi in modo da aiutarlo a capire meglio cosa facciamo e come possiamo aiutarlo. Cerca di convincerlo a contattarci per una prima consulenza gratuita. Assicurati che la risposta sia CONCISA e chiara. Se ti chiedono come contattarci, digli di compilare il form di contatto presente sotto."
            }
            messages.append(system_message)
        else:
            messages.extend(existing_conversation['messages'])

        # Append user's message
        user_message = {
            "role": "user",
            "content": user_message
        }
        messages.append(user_message)

        # Log the message being sent to the OpenAI API
        logging.info(f"Sending messages to OpenAI: {messages}")

        start_api_call_time = time.time()

        # Get response from Azure OpenAI
        response = client.chat.completions.create(
            model="landingBot",
            messages=messages
        )

        end_api_call_time = time.time()
        logging.info(f"Azure OpenAI API call took {end_api_call_time - start_api_call_time} seconds")

        ai_response = response.choices[0].message.content

        # Append bot response to the messages list
        messages.append(
            {
                "role": "assistant",
                "content": ai_response
            }
        )

        # Store or update chat data in Cosmos DB
        chat_data = {
            "id": str(chat_id),  # Use the provided chatId as unique ID
            "chatId": chat_id,
            "messages": messages
        }
        container.upsert_item(chat_data)

    except Exception as e:
        logging.error(f"Error in main function: {e}")
        ai_response = "Sorry, there was an error in processing your request."

    return ai_response  # Return the AI response
