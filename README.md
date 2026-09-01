🤖 First Microsoft Azure Web Application — RAG Assistant with Azure OpenAI & Azure AI Search

A live, deployed Retrieval-Augmented Generation (RAG) web app built entirely on Microsoft Azure's own AI stack: Azure AI Search for keyword retrieval, Azure OpenAI (GPT-4.1-mini) for grounded answer generation, a Streamlit front end, and a fully automated CI/CD pipeline via GitHub Actions that deploys straight to Azure App Service on every push to main.

Show Image Show Image Show Image Show Image Show Image

🔗 Live Demo → firstazurewebapp.azurewebsites.net
📌 Overview

This project answers questions strictly from a private document knowledge base — no answer is generated from the model's own training data. A user's question is first sent to Azure AI Search to retrieve the most relevant document chunks (keyword search), and only that retrieved context is handed to Azure OpenAI to generate a grounded response. If nothing relevant is found, the assistant says so explicitly instead of guessing.

This is my first end-to-end deployment on Microsoft's cloud platform — combining Azure's managed AI services with a real CI/CD pipeline, rather than running everything locally.

🏗️ Architecture
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
⚙️ Azure Resources Used
Resource	Endpoint	Purpose
Azure OpenAI	https://ssopenai.services.ai.azure.com/	Hosts the gpt-4.1-mini deployment used for answer generation
Azure AI Search	https://kssragservice.search.windows.net	Hosts the sstextembedding index used for document retrieval

API keys for both resources are never stored in this repository. They are supplied at runtime as environment variables.

✨ Features
🔍 Keyword-based retrieval via Azure AI Search over a pre-indexed document set
🤖 Grounded generation with Azure OpenAI — the model is explicitly instructed to answer only from retrieved context, never from its own knowledge
🚫 Honest refusal — if no relevant document is found, the app says so instead of hallucinating an answer
📄 Transparency — the exact retrieved context is displayed alongside every successful answer, so the user can verify the source
🔐 Secrets kept out of source control — all credentials are read as environment variables, never hardcoded
🚀 Fully automated deployment — every push to main triggers a GitHub Actions build-and-deploy pipeline to Azure App Service
🔍 The Code, Section by Section
1️⃣ Configuration — Endpoints Fixed, Keys from the Environment
python
AZURE_OPENAI_ENDPOINT = "https://ssopenai.services.ai.azure.com/"
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

SEARCH_ENDPOINT = "https://kssragservice.search.windows.net"
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")

INDEX_NAME = "sstextembedding"

The endpoints and index name identify which Azure resources to talk to — not sensitive on their own, so they can live directly in code. The keys are what actually authenticate and bill your account, so they are read from environment variables at runtime rather than hardcoded.

2️⃣ Retrieval — Azure AI Search
python
results = search_client.search(search_text=question, top=3)
context = "".join(doc["chunk"] + "\n\n" for doc in results)

A keyword search against the sstextembedding index returns the top 3 matching chunks. If nothing comes back, the app stops immediately with a clear message — no wasted LLM call on empty context.

3️⃣ Grounded Prompt Construction
python
prompt = f"""You are a RAG assistant. Use ONLY the information provided in the context...
If the answer is NOT present in the context, reply ONLY with:
I could not find the answer in the knowledge base.
Do not use your own knowledge. Do not guess. Do not make up information.
Context: {context}
Question: {question}"""

The prompt does the heavy lifting of hallucination control — explicit negative instructions paired with an exact required refusal phrase, which the app checks against programmatically to decide whether to show the retrieved context.

4️⃣ Generation — Azure OpenAI
python
response = client.chat.completions.create(model=DEPLOYMENT_NAME, messages=[...])

The gpt-4.1-mini deployment generates the final answer, called through the AzureOpenAI client — the small but important distinction of using Azure's managed OpenAI service with its own endpoint and API versioning.

🗂️ Repository Structure
First-Microsoft-Azure-Web-Application/
├── azure_app.py                          # Main Streamlit application
├── requirements.txt                      # Python dependencies
├── .gitignore                            # Excludes venv and build artifacts
├── pyvenv.cfg                            # Local virtual environment config
└── .github/
    └── workflows/
        └── main_firstazurewebapp.yml     # CI/CD pipeline definition
🚀 CI/CD Pipeline — GitHub Actions → Azure App Service

Every push to main triggers an automated two-job pipeline:

Build job:

Checks out the repo and sets up Python 3.13
Creates a virtual environment and installs requirements.txt — a local sanity check that catches dependency issues before deployment
Uploads the app as a build artifact (excluding the local antenv/ virtual environment to keep the payload small)

Deploy job:

Downloads the build artifact
Deploys it to the firstazurewebapp Azure Web App's Production slot via azure/webapps-deploy@v3, authenticating with a publish profile stored as a GitHub secret — never exposed in the workflow file itself

Azure's Oryx build engine then runs pip install server-side during deployment, driven by the SCM_DO_BUILD_DURING_DEPLOYMENT app setting — which is why the workflow's own local build step is optional and mainly useful for early failure detection.

🛠️ Local Development
Prerequisites
Python 3.13
Access to the Azure OpenAI and Azure AI Search resources listed above (or your own equivalents)
AZURE_OPENAI_KEY and AZURE_SEARCH_KEY set as environment variables in your shell/session
Setup
bash
git clone https://github.com/Kailaswadje/First-Microsoft-Azure-Web-Application.git
cd First-Microsoft-Azure-Web-Application

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run azure_app.py
🔐 Security Notes
Only the API keys are kept out of source control — endpoints and index names are visible above since they identify resources, not credentials
Credentials are supplied as environment variables, locally in your shell/session and in Azure App Service via Application Settings — never committed to the repository
The Azure Web App publish profile used by the GitHub Actions workflow is stored as an encrypted repository secret — it never appears in plain text anywhere in this repo
If a key is ever accidentally exposed (e.g. committed, pasted, or shared), regenerate it in the Azure Portal immediately — removing it from code alone does not revoke an exposed key
🧠 Key Takeaways
RAG grounding is a prompt-engineering problem as much as a retrieval one — explicit refusal instructions are what actually prevent hallucination, not the retrieval step alone
Azure's managed AI services compose cleanly — Azure AI Search and Azure OpenAI integrate through their own SDKs with minimal glue code
CI/CD removes manual deployment entirely — git push to main is the only action needed to ship a change to production
Not every configuration value needs the same protection — endpoints identify resources and can live in code; keys authenticate and bill, and belong in environment variables only
🔮 Possible Extensions
 Upgrade from keyword search to vector/semantic search in Azure AI Search for better retrieval on paraphrased questions
 Add source document citations (page/file name) alongside retrieved context
 Add conversation memory for multi-turn Q&A
 Add a staging deployment slot for testing before promoting to Production
👤 Author

Kailas Wadje MSc Data Science & AI, University of Liverpool

GitHub: @Kailaswadje
LinkedIn: linkedin.com/in/kwadaje

⭐ If this Azure RAG deployment was helpful, consider giving it a star!
