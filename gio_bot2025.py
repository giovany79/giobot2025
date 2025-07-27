from openai import OpenAI
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_updates(offset):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        json_response = response.json()
        if "result" in json_response:
            return json_response["result"]
        else:
            print(f"Unexpected response format from Telegram API: {json_response}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Telegram API: {str(e)}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON response: {str(e)}")
        return []

def send_messages(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(url, params=params)
    return response

def get_openai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return "Sorry, I encountered an error processing your request. Please try again later."

def main():
    print("Starting bot...  ")
    offset = 0
    while True:
        updates = get_updates(offset)
        if updates:
            for update in updates:
                offset = update["update_id"] + 1
                chat_id = update["message"]["chat"]["id"]
                user_message = update["message"]["text"]
                print(f"User: {chat_id}")
                print(f"Received Message: {user_message}")
                GPT = get_openai_response(user_message)
                send_messages(chat_id, GPT)
        time.sleep(1)

if __name__ == "__main__":
    main()
