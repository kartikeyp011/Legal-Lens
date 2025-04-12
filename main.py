from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
import google.generativeai as genai
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Configure AI and DB
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.contract_guardian


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")

    # AI analysis
    prompt = """Analyze this contract for:
    - Unfair termination clauses
    - Hidden auto-renewals
    - Excessive liability
    Return concise bullet points."""

    response = model.generate_content(prompt + text)

    # Store in DB
    db.contracts.insert_one({
        "original_text": text[:500] + "...",  # Store first 500 chars to avoid huge files
        "analysis": response.text
    })

    return PlainTextResponse(response.text)


@app.get("/")
async def test():
    return PlainTextResponse("Send a POST request with a contract file to /analyze")