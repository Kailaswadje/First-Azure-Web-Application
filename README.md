# 🤖 First Microsoft Azure Web Application — RAG Assistant with Azure OpenAI & Azure AI Search

A live, deployed **Retrieval-Augmented Generation (RAG)** web app built entirely on Microsoft Azure's own AI stack: **Azure AI Search** for keyword retrieval, **Azure OpenAI (GPT-4.1-mini)** for grounded answer generation, a **Streamlit** front end, and a fully automated **CI/CD pipeline via GitHub Actions** that deploys straight to **Azure App Service** on every push to `main`.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit&logoColor=white)
![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4.1--mini-0078D4?logo=microsoftazure&logoColor=white)
![Azure AI Search](https://img.shields.io/badge/Azure%20AI%20Search-Keyword%20Retrieval-0078D4?logo=microsoftazure&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)

### 🔗 [**Live Demo → firstazurewebapp.azurewebsites.net**](https://firstazurewebapp-g0b6bsh7g3f6apg7.spaincentral-01.azurewebsites.net/)

---

## 📌 Overview

This project answers questions **strictly from a private document knowledge base** — no answer is generated from the model's own training data. A user's question is first sent to **Azure AI Search** to retrieve the most relevant document chunks (keyword search), and only that retrieved context is handed to **Azure OpenAI** to generate a grounded response. If nothing relevant is found, the assistant says so explicitly instead of guessing.

This is my first end-to-end deployment on Microsoft's cloud platform — combining Azure's managed AI services with a real CI/CD pipeline, rather than running everything locally.

---

## 🏗️ Architecture

```
User Question (Streamlit UI)
        │
        ▼
Azure AI Search  ──►  top 3 matching chunks (keyword search)
        │
        ▼
   No match? ──► "I could not find the answer in the knowledge base."
        │
        ▼ (match found)
Grounded Prompt  ──►  Azure OpenAI (gpt-4.1-mini)
        │
        ▼
     Answer  +  Retrieved Context (shown for transparency)
```

---

## ✨ Features

- 🔍 **Keyword-based retrieval** via Azure AI Search over a pre-indexed document set
- 🤖 **Grounded generation** with Azure OpenAI — the model is explicitly instructed to answer *only* from retrieved context, never from its own knowledge
- 🚫 **Honest refusal** — if no relevant document is found, the app says so instead of hallucinating an answer
- 📄 **Transparency** — the exact retrieved context is displayed alongside every successful answer, so the user can verify the source
- 🔐 **Secrets kept out of source control** — all credentials load from environment variables via `python-dotenv`, never hardcoded
- 🚀 **Fully automated deployment** — every push to `main` triggers a GitHub Actions build-and-deploy pipeline to Azure App Service

---

## 🔍 The Code, Section by Section

### 1️⃣ Environment-Based Configuration
```python
load_dotenv()
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
```
Every credential and endpoint is read from environment variables — locally from a `.env` file (never committed), and in Azure App Service from **Application Settings**, which inject the same variables at runtime without any file ever touching the deployed code.

### 2️⃣ Retrieval — Azure AI Search
```python
results = search_client.search(search_text=question, top=3)
context = "".join(doc["chunk"] + "\n\n" for doc in results)
```
A **keyword search** (not yet vector/semantic search) against the configured index returns the top 3 matching chunks. If nothing comes back, the app stops immediately with a clear message — no wasted LLM call on empty context.

### 3️⃣ Grounded Prompt Construction
```python
prompt = f"""You are a RAG assistant. Use ONLY the information provided in the context...
If the answer is NOT present in the context, reply ONLY with:
I could not find the answer in the knowledge base.
Do not use your own knowledge. Do not guess. Do not make up information.
Context: {context}
Question: {question}"""
```
The prompt does the heavy lifting of hallucination control — explicit negative instructions ("do not guess," "do not use your own knowledge") paired with an exact required refusal phrase, which the app checks against programmatically to decide whether to show the retrieved context.

### 4️⃣ Generation — Azure OpenAI
```python
response = client.chat.completions.create(model=DEPLOYMENT_NAME, messages=[...])
```
The `gpt-4.1-mini` deployment generates the final answer, called through the `AzureOpenAI` client rather than the standard OpenAI client — the small but important distinction of using **Azure's managed OpenAI service** with its own endpoint and API versioning.

---

## 🗂️ Repository Structure

```
First-Microsoft-Azure-Web-Application/
├── azure_app.py                          # Main Streamlit application
├── requirements.txt                      # Python dependencies
├── .env.example                          # Template for required environment variables
├── .gitignore                            # Excludes .env, venv, and build artifacts
├── pyvenv.cfg                            # Local virtual environment config
└── .github/
    └── workflows/
        └── main_firstazurewebapp.yml     # CI/CD pipeline definition
```

---

## 🚀 CI/CD Pipeline — GitHub Actions → Azure App Service

Every push to `main` triggers an automated two-job pipeline:

**Build job:**
1. Checks out the repo and sets up **Python 3.13**
2. Creates a virtual environment and installs `requirements.txt` — a local sanity check that catches dependency issues before deployment
3. Uploads the app as a build artifact (excluding the local `antenv/` virtual environment to keep the payload small)

**Deploy job:**
1. Downloads the build artifact
2. Deploys it to the **`firstazurewebapp`** Azure Web App's Production slot via `azure/webapps-deploy@v3`, authenticating with a **publish profile stored as a GitHub secret** — never exposed in the workflow file itself

> Azure's Oryx build engine then runs `pip install` server-side during deployment, driven by the `SCM_DO_BUILD_DURING_DEPLOYMENT` app setting — which is why the workflow's own local build step is optional and mainly useful for early failure detection.

---

## 🛠️ Local Development

### Prerequisites
- Python 3.13
- An [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) resource with a deployed model
- An [Azure AI Search](https://azure.microsoft.com/en-us/products/ai-services/ai-search) service with a populated index

### Setup

```bash
git clone https://github.com/Kailaswadje/First-Microsoft-Azure-Web-Application.git
cd First-Microsoft-Azure-Web-Application

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# open .env and fill in your own Azure OpenAI + Azure AI Search credentials

streamlit run azure_app.py
```

---

## 🔐 Security Notes

- **`.env` is git-ignored** — all real credentials stay local or live in Azure App Service's Application Settings, never in source control
- **`.env.example` contains placeholders only** — copy it to `.env` and fill in your own values
- The Azure Web App publish profile used by the GitHub Actions workflow is stored as an encrypted **repository secret**, referenced as `${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE_... }}` — it never appears in plain text anywhere in this repo
- If credentials were ever hardcoded in a previous commit, treat them as compromised: **regenerate the keys in the Azure Portal** even after removing them from the code, since git history can retain old commits

---

## 🧠 Key Takeaways

- **RAG grounding is a prompt-engineering problem as much as a retrieval one** — explicit refusal instructions are what actually prevent hallucination, not the retrieval step alone
- **Azure's managed AI services compose cleanly** — Azure AI Search and Azure OpenAI integrate through their own SDKs with minimal glue code
- **CI/CD removes manual deployment entirely** — `git push` to `main` is the only action needed to ship a change to production
- **Environment-based configuration is what makes a codebase shareable** — the same code runs locally and in Azure App Service purely by changing where the environment variables come from

---

## 🔮 Possible Extensions

- [ ] Upgrade from keyword search to **vector/semantic search** in Azure AI Search for better retrieval on paraphrased questions
- [ ] Add source document citations (page/file name) alongside retrieved context
- [ ] Add conversation memory for multi-turn Q&A
- [ ] Add a staging deployment slot for testing before promoting to Production

---

## 👤 Author

**Kailas Wadje**
MSc Data Science & AI, University of Liverpool

- GitHub: [@Kailaswadje](https://github.com/Kailaswadje)
- LinkedIn: [linkedin.com/in/kwadaje](https://www.linkedin.com/in/kwadaje/)

---

⭐ If this Azure RAG deployment was helpful, consider giving it a star!
