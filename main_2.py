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

# Existing routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

from fastapi.responses import HTMLResponse

def format_analysis(raw_text: str) -> str:
    # Convert raw analysis to structured HTML
    sections = {
        "Unfair Termination Clauses": [],
        "Hidden Auto-Renewals": [],
        "Excessive Liability": [],
        "Other Concerns": []
    }
    
    current_section = None
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('* '):
            if ':' in line:  # Section header
                section_name = line[2:].split(':')[0]
                if section_name in sections:
                    current_section = section_name
            elif current_section:  # Bullet point
                point = line[2:].replace('"', '')
                sections[current_section].append(point)
    
    # Generate HTML
    html_output = []
    for section, points in sections.items():
        if points:
            html_output.append(f'<div class="analysis-section">')
            html_output.append(f'<h3 class="section-title">{section}</h3>')
            html_output.append('<ul class="risk-points">')
            html_output.extend(f'<li>{point}</li>' for point in points)
            html_output.append('</ul></div>')
    
    return '\n'.join(html_output)

# NEW: Add this endpoint
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_contract(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")
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
    """
    raw_analysis = model.generate_content(prompt + text).text
    formatted_html = format_analysis(raw_analysis)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contract Analysis</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .report-container {{ max-width: 800px; margin: 2rem auto; }}
            .analysis-section {{ margin-bottom: 2rem; }}
            .section-title {{
                color: #dc3545;
                border-bottom: 2px solid #dc3545;
                padding-bottom: 0.5rem;
            }}
            .risk-points {{ margin-top: 1rem; }}
            .risk-points li {{
                margin-bottom: 0.5rem;
                position: relative;
                padding-left: 1.5rem;
            }}
            .risk-points li:before {{
                content: "•";
                color: #dc3545;
                font-weight: bold;
                position: absolute;
                left: 0;
            }}
            .risk-level {{
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-weight: bold;
                margin-left: 0.5rem;
            }}
            .high-risk {{ background-color: #ffc107; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <h1 class="text-center mb-4">Contract Analysis Report</h1>
            <div class="alert alert-info">
                <strong>Filename:</strong> {file.filename}<br>
                <strong>Analyzed at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
            
            {formatted_html}
            
            <div class="mt-4">
                <a href="/upload" class="btn btn-primary">Analyze Another</a>
            </div>
        </div>
    </body>
    </html>
    """)