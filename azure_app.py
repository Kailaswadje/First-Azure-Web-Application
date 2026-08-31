import os
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
 
# ===========================
# Load environment variables from .env (local dev)
# On Streamlit Cloud / Azure App Service, set these as
# actual environment variables / secrets instead of a .env file.
# ===========================
load_dotenv()
 
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
 
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME")
 
# Fail fast with a clear message instead of a confusing SDK error later
required = {
    "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
    "AZURE_OPENAI_KEY": AZURE_OPENAI_KEY,
    "AZURE_SEARCH_ENDPOINT": SEARCH_ENDPOINT,
    "AZURE_SEARCH_KEY": SEARCH_KEY,
    "AZURE_SEARCH_INDEX_NAME": INDEX_NAME,
}
missing = [k for k, v in required.items() if not v]
if missing:
    st.error(f"Missing required environment variables: {', '.join(missing)}. "
             f"Create a .env file locally (see .env.example) or set them in your "
             f"deployment environment's secrets/configuration.")
    st.stop()
 
# ===========================
# Azure Clients
# ===========================
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=API_VERSION
)
 
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)
 
# ===========================
# Streamlit UI
# ===========================
st.set_page_config(page_title="Azure RAG Demo", page_icon="🤖")
st.title("🤖 Azure RAG Assistant — Keyword Search")
st.write("Ask questions from your uploaded documents.")
question = st.text_input("Ask your question")
 
if st.button("Ask"):
 
    # Search Azure AI Search
    results = search_client.search(
        search_text=question,
        top=3
    )
 
    context = ""
    for doc in results:
        context += doc["chunk"] + "\n\n"
 
    # -------------------------
    # No matching documents found
    # -------------------------
    if context.strip() == "":
        st.warning("No relevant documents found in the knowledge base for this question.")
        st.stop()
 
    # -------------------------
    # Build the grounded prompt
    # -------------------------
    prompt = f"""
You are a RAG assistant.
 
Use ONLY the information provided in the context.
 
If the answer is NOT present in the context, reply ONLY with:
 
I could not find the answer in the knowledge base.
 
Do not use your own knowledge.
Do not guess.
Do not make up information.
 
Context:
{context}
 
Question:
{question}
"""
 
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
 
    answer = response.choices[0].message.content
 
    st.subheader("Answer")
    st.write(answer)
 
    if answer != "I could not find the answer in the knowledge base.":
        st.subheader("Retrieved Context")
        st.write(context)