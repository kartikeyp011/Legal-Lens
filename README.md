
# LegalLens 🕵️‍♂️📜

**LegalLens** is an AI-powered legal assistant that helps users detect risky clauses in contracts and understand legal language in simple terms. It’s designed to democratize legal understanding using cutting-edge AI and blockchain privacy.

> “Never sign what you don’t understand — let LegalLens read the fine print for you.”

---

## 🚀 Features

- ⚖️ **Deep Clause Analysis** – Detects high-risk terms (e.g., unfair termination, auto-renewals, excessive liability)
- 💬 **Plain-Language Summaries** – Explains complex legal jargon in simple terms (20+ languages supported)
- 📂 **Multi-format Uploads** – Upload PDFs, DOCX, or images of contracts
- 💸 **Freemium Model** – Free basic analysis, premium features for advanced legal support

---

## 🛠️ Tech Stack

- **Frontend:** HTML/CSS, Vanilla JavaScript
- **Backend:** FastAPI (Python)
- **AI:** Google Gemini API (fine-tuned for legal analysis)
- **Database:** MongoDB Atlas

---

## 📦 Installation (Windows)

1. **Clone this repo**
   ```bash
   git clone https://github.com/yourusername/LegalLens.git
   cd LegalLens
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Copy `.env.example` to `.env`
   - Fill in your actual API keys

   ```bash
   copy .env.example .env
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

---

## 🔐 Environment Variables (`.env.example`)

```env
GEMINI_API_KEY=your-google-gemini-api-key
MONGODB_URI=your-mongodb-connection-uri
AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret
```

- Do **not** share your `.env` file or upload it to GitHub.

---

## 📄 Example Use Case

> "John, a freelancer, uploads a 10-page service agreement. LegalLens flags a hidden auto-renewal and an unfair liability clause, explains both in plain English, and suggests edits. The contract is secured via blockchain, ensuring legal verifiability without exposing private terms."

---

## 🌍 Roadmap

- 📱 Mobile contract scanner
- 🤝 Live AI negotiation assistant
- 🔌 Enterprise API access
- 🧠 Offline LLM fallback mode

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and open a pull request.

---

## 💡 Inspiration

> 83% of people sign contracts without fully understanding them.  
> $150 billion lost annually due to predatory clauses.

LegalLens empowers users to understand legal documents — one clause at a time.

---

## 👨‍💻 Author

Built at GNEC Hackathon 2025 by [Kartikey Narain Prajapati]([https://github.com/yourusername](https://github.com/kartikeyp011))
