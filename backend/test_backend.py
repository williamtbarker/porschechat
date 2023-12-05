import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variable
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def test_openai_chat():
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly omniscient Porsche expert. Engage in rich conversations about all things relating to the brand with precise knowledge and interesting stories."
                },
                {
                    "role": "user",
                    "content": "Explain the history and significance of the Porsche 911 Turbo."
                }
            ],
            model="gpt-3.5-turbo",
        )
        print("Response:", chat_completion.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_openai_chat()



