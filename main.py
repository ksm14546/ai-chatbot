from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import httpx
import os
import json
from dotenv import load_dotenv
from typing import List

load_dotenv()
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc.errors())}
    )

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
async def root():
    return {"status": "Chatbot API is running!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"📩 Received message: {request.message}")
        print(f"📜 History count: {len(request.history)}")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer all questions clearly and in detail."
            }
        ]

        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": request.message})

        payload = {
            "model": "llama3.2:3b",
            "messages": messages,
            "stream": True  # ✅ enable streaming
        }

        # ✅ Streaming generator function
        async def stream_response():
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{ollama_url}/v1/chat/completions", json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    yield token  # ✅ send token by token
                            except Exception:
                                continue

        return StreamingResponse(stream_response(), media_type="text/plain")

    except httpx.ConnectError:
        raise HTTPException(status_code=500, detail="Cannot connect to Ollama. Run: ollama serve")
    except httpx.TimeoutException:
        raise HTTPException(status_code=500, detail="Ollama took too long to respond.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")