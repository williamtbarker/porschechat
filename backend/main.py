from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, Text
import databases
import redis
from openai import OpenAI

# Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database Setup
metadata = MetaData()

chat_history_table = Table(
    "chat_history",
    metadata,
    Column("session_id", String, primary_key=True),
    Column("conversation", Text)
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

database = databases.Database(DATABASE_URL)

# Redis Setup
redis_client = redis.from_url(REDIS_URL)

# OpenAI Client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# FastAPI App
app = FastAPI()


# Pydantic Models
class ChatRequest(BaseModel):
    prompt: str
    session_id: str


class ChatResponse(BaseModel):
    response: str


# Endpoint to handle chat
@app.post("/chat", response_model=ChatResponse)
async def chat_with_openai(request: ChatRequest):
    session_id = request.session_id
    session = redis_client.get(session_id)

    if not session:
        async with database.transaction():
            query = chat_history_table.select().where(chat_history_table.c.session_id == session_id)
            result = await database.fetch_one(query)
            session = json.loads(result.conversation) if result else []

    session.append({"role": "user", "content": request.prompt})

    # OpenAI call
    response = openai_client.Completion.create(
        model="gpt-3.5-turbo",
        prompt=json.dumps(session),  # Ensure prompt format aligns with OpenAI's requirements
        max_tokens=150
    )
    answer = response.choices[0].text.strip()
    session.append({"role": "assistant", "content": answer})

    # Update Redis and Postgres
    redis_client.set(session_id, json.dumps(session))
    async with database.transaction():
        update_query = chat_history_table.update().where(chat_history_table.c.session_id == session_id).values(
            conversation=json.dumps(session))
        await database.execute(update_query)

    return ChatResponse(response=answer)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def read_root():
    return {"Hello": "World"}



