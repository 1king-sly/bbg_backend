import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
import httpx


from app.src.models.schemas import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
@router.post("/")
async def chat(request:ChatRequest):
    try:

        context = (
            "You are an AI trained to answer questions specifically about  sexual health, social,economical and political being of female gender especially in Kenya and Africa "
            "Your responses should focus solely on political, law , economical, career development, social and sexual being of the female and the children"
        )

        # Combine the user input with the context
        full_message = f"{context}\nUser: {request.message}\nAI:"

        # Call Gemini API to generate the response
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_message)

        # Return the generated response text

        return {"response": response.text}
    except Exception as e:
        print(e)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/openai")
async def chat_with_openai(request: ChatRequest):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": request.message}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        bot_response = response_data["choices"][0]["message"]["content"]
        return {"response": bot_response}
    else:
        raise HTTPException(status_code=response.status_code, detail="Error with OpenAI API")
