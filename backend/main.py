from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import openai
from dotenv import load_dotenv
import os
import logging

# Load environment variables and set up logging
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO)

if not openai.api_key:
    raise ValueError("No OpenAI API key found in .env")

app = FastAPI()

# Set up CORS
origins = [
    "http://localhost:3000",  # Assuming your frontend runs on localhost:3000
    "https://yourfrontenddomain.com",  # Replace with your actual frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to handle chatbot functionality
@app.post("/chat")
async def chat_with_openai(prompt: str = Body(..., embed=True)):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        return {"response": response.choices[0].text.strip()}
    except Exception as e:
        logging.error(f"Error in OpenAI API call: {e}")
        raise HTTPException(status_code=500, detail="Error in processing the request")

# Optional: Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "running"}

