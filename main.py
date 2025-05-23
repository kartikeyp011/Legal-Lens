from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from jose import jwt
from urllib.request import urlopen
import json
import os

load_dotenv()

# MongoDB setup (renamed to LegalLink)
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.LegalLink  # Changed from contract_guardian
contracts_collection = db.contracts  # Optional: clearer variable name

# Gemini setup (uses API_KEY)
genai.configure(api_key=os.getenv("API_KEY"))  # Now reads from API_KEY
model = genai.GenerativeModel('gemini-2.0-flash')


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/auth/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

# Existing routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# NEW: Add this endpoint
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_contract(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")
    
    # Get raw analysis from Gemini
    prompt = """
    You are a legal analysis assistant. Your task is to review the following contract and identify potential risks, biased terms, or unfavorable clauses for the client.

    Return the findings using concise bullet points grouped under clearly labeled **bold headers**. Include clause references (e.g., "Section 4.3") wherever available. Avoid paragraph summaries. Do not include general explanations unless directly tied to a clause.

    ---

    ### 1. **Unfair or One-Sided Termination Clauses**
    - Identify any clauses allowing **termination without cause** or **for convenience**
    - Highlight **asymmetry** in termination rights between the Provider and Client
    - Note if either party is required to provide **advance notice**, and if so, how long
    - Indicate if a **cure period** is required before termination for breach
    - Specify any obligations that **survive termination**, like fee payments
    - Flag if termination leads to **loss of access**, services, or data

    ### 2. **Hidden or Problematic Auto-Renewal Provisions**
    - Identify if the contract **automatically renews**, and for how long
    - Assess if the **renewal period** is disproportionately long
    - Highlight the **notice period** and method required for cancellation
    - Evaluate whether renewal terms are **clearly disclosed** and **fair to both parties**
    - Check if renewal includes **automatic price or term changes**

    ### 3. **Excessive or Imbalanced Liability Clauses**
    - Flag any **caps on liability**, especially those tied to minimal amounts (e.g., last month's fees)
    - Identify exclusions of **indirect, incidental, consequential, or punitive damages**
    - Note any **warranty disclaimers** or "as-is" service clauses
    - Look for **disclaimers on high-risk or mission-critical activities**
    - Check if the contract **limits Provider accountability** for failures, delays, or data loss
    - Flag terms that place **unreasonable burden of risk on the Client**

    ### 4. **Unilateral or Unfair Financial Terms**
    - Identify any clauses that allow **unilateral fee increases**, adjustments, or hidden charges
    - Flag high or **compounding late payment penalties** or administrative fees
    - Look for payment terms that require fees **despite service interruptions or termination**
    - Note any **non-refundable fees**, prepaid commitments, or inflexible billing practices

    ### 5. **Problematic Intellectual Property (IP) & Deliverables Terms**
    - Check whether **Client receives ownership** of deliverables by default
    - Identify if the Provider **retains all IP rights** unless explicitly reassigned
    - Look for ambiguous or **restrictive use rights** for the Client
    - Highlight if deliverables are tied to ongoing service or subscription

    ### 6. **Unilateral Amendments and Policy Changes**
    - Flag if the Provider can **change the contract unilaterally**
    - Look for clauses allowing updates via a **website or portal** without Client consent
    - Identify if the Client has **any recourse** or opt-out option when terms change

    ### 7. **Restrictive or Biased Dispute Resolution Mechanisms**
    - Check for **mandatory arbitration** or waiver of court rights
    - Note if dispute resolution is restricted to a **specific jurisdiction or location**
    - Flag any imbalance in **legal remedies, attorney fees, or enforcement**

    ### 8. **Other Red Flags or Risky Provisions**
    - Identify **non-compete, exclusivity**, or **restrictions on competition**
    - Flag **broad indemnification clauses** requiring the Client to cover Provider's risks
    - Look for **data usage, privacy, or confidentiality terms** favoring the Provider
    - Identify if the Provider disclaims **SLAs**, uptime guarantees, or support obligations
    - Flag **ambiguities or undefined terms** that could be misused

    **For each issue identified, suggest practical legal or negotiation strategies that a client could use to resolve, mitigate, or clarify the risk.** These may include:
        - Requesting specific changes to the clause
        - Adding definitions, exceptions, or additional terms
        - Seeking legal clarification or additional protections
        - Negotiation tips or fallback options

        Use this format:
        - **Issue:** [Problem summary]
        - **Solution:** [Clear, actionable suggestion to address it]
    """

    raw_analysis = model.generate_content(prompt + text).text

    # Convert raw markdown-like output to styled HTML
    from markdown2 import markdown
    formatted_html = markdown(raw_analysis)

    # Full professional HTML page
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contract Analysis Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background-color: #f8f9fa;
            }}
            .card {{
                border-radius: 1rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            }}
            h1, h2, h3 {{
                color: #343a40;
            }}
            ul {{
                padding-left: 1.5rem;
            }}
            li {{
                margin-bottom: 0.5rem;
            }}
        </style>
    </head>
    <body class="container py-5">
        <h2 class="mb-4">📄 Contract Analysis Report</h2>
        <div class="card p-4 bg-white">
            {formatted_html}
        </div>
        <div class="mt-4">
            <a href="/upload" class="btn btn-outline-primary">🔁 Analyze Another Contract</a>
        </div>
    </body>
    </html>
    """

    # Store in DB
    contracts_collection.insert_one({
        "filename": file.filename,
        "analysis": raw_analysis,
        "timestamp": datetime.now()
    })

    return HTMLResponse(html_response)

@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


# Add these new endpoints
from fastapi import Request, Form, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

security = HTTPBasic()

# Mock user database (replace with MongoDB later)
fake_users_db = {
    "user@example.com": {
        "password": "securepassword123",
        "name": "John Doe"
    }
}

@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/auth/login")
async def handle_login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(email)
    if not user or user["password"] != password:
        return templates.TemplateResponse("auth/login.html", 
            {"request": request, "error": "Invalid credentials"})
    
    # Successful login → redirect to upload page
    response = RedirectResponse("/upload", status_code=303)
    response.set_cookie(key="session_token", value="fake_session_token") 
    return response

@app.get("/auth/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@app.post("/auth/signup")
async def handle_signup(request: Request, 
                      email: str = Form(...),
                      password: str = Form(...),
                      name: str = Form(...)):
    if email in fake_users_db:
        return templates.TemplateResponse("auth/signup.html", 
            {"request": request, "error": "Email already exists"})
    
    # Add to "database"
    fake_users_db[email] = {"password": password, "name": name}
    
    # Auto-login after signup
    response = RedirectResponse("/upload", status_code=303)
    response.set_cookie(key="session_token", value="fake_session_token")
    return response

from fastapi import HTTPException, status

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token or session_token != "fake_session_token":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/auth/login"}
        )
    return True

@app.get("/upload")
async def upload_page(request: Request, _ = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request})






# AUTH INTEGRATION
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
ALGORITHMS = ["RS256"]

def get_token_auth_header(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth.split(" ")[1]
    return token

def verify_jwt(token: str):
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        return jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=API_IDENTIFIER, issuer=f"https://{AUTH0_DOMAIN}/")
    raise HTTPException(status_code=401, detail="Token verification failed")