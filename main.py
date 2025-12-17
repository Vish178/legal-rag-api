from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import os
from pathlib import Path
from pydantic import SecretStr


# ... rest of your imports (os, logging, fastapi, etc.) ...
from typing import Dict, Any
from dotenv import load_dotenv
from operator import itemgetter
import logging

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --------------Logging--------------------

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI_RAG")

# -------------- Global Variable--------------------

BASE_DIR: Path = Path(__file__).resolve().parent
DB_DIR: Path = BASE_DIR / "Databases"
MODEL: str = os.getenv("MODEL_NAME", "")
OPENROUTER_API_KEY: SecretStr = SecretStr(os.getenv("OPENROUTER_API_KEY", ""))

EMBEDDING_MODEL:str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")

resource = {}

embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL)
DB_PATH = {
    "constitutional": str(DB_DIR / "chroma_constitution"),
    "criminal": str(DB_DIR / "chroma_criminal"),
    "labour": str(DB_DIR / "chroma_labour")
}

def database_loader():
    retrievers = {}
    for domain, path in DB_PATH.items():
        
        db_folder = Path(path)
        

        if not db_folder.exists() or not any(db_folder.iterdir()):
            logger.error(f"CRITICAL: Database not found or empty at {db_folder}")
            # We skip loading this one so we don't get silent errors later
            continue
            
        logger.info(f"Loading {domain} DB from {db_folder}...")
        
        # 3. Load Chroma
        try:
            vectorstore = Chroma(persist_directory=str(db_folder), embedding_function=embeddings)
            # Check if it actually has data!
            count = vectorstore._collection.count()
            if count == 0:
                logger.warning(f"Warning: {domain} DB exists but is EMPTY (0 documents).")
            else:
                logger.info(f"   - Loaded {count} documents.")
                
            retrievers[domain] = vectorstore.as_retriever(search_kwargs={"k": 5})
            
        except Exception as e:
            logger.error(f"Failed to load {domain}: {e}")

    return retrievers


def build_chain():

    router_prompt = ChatPromptTemplate.from_template(
        """ 
        Classify the legal question into constitutional, criminal, or labour. 
        Return only one word.\n
        {question} \n
        Domain:
        """
    )

    llm = ChatOpenAI(
        model = MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0
    )

    router = router_prompt | llm | StrOutputParser()

    retrievers = database_loader()

    def retrieve(x: Dict[str, Any]):

        raw_domain = x["Domain"]
        domain = raw_domain.split(":")[-1].strip().lower()
        
        logger.info(f"Router decided: {domain}")

        if domain not in retrievers:
            logger.warning(f"Domain '{domain}' not found in retrievers. Defaulting to Criminal.")
            domain = "criminal"
        

        docs = retrievers[domain].invoke(x["question"])
        

        if not docs:
            logger.warning(f"Retrieval returned 0 documents for query: '{x['question']}'")
            
        return docs

    
    ques_ans_prompt = ChatPromptTemplate.from_template(
        """ 
        Answer only using the context provided. 
        If context not enough to answer the question say "I dont know"\n
        Context: \n{context}\n
        Question: \n{question}\n
        Answer:  
        """
    )

    chain = (
        {"Domain": router, "question": itemgetter("question")}
        | RunnablePassthrough.assign(context = RunnableLambda(retrieve))
        |{
            "answer": ques_ans_prompt | llm | StrOutputParser(),
            "context": itemgetter("context"),
            "question": itemgetter("question")
        }
    )
    return chain

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAG system")
    try:
        resource["chain"] = build_chain()
        logger.info("System Ready")
    except Exception as e:
        logger.info("Failed to Intialize")
    yield
    resource.clear()

app = FastAPI(lifespan = lifespan)

@app.get("/")
def home():
    return {"This the Legal Assistant API"}

@app.get('/chat/{question}')
def chat(question: str):

    if "chain" not in resource:
        raise HTTPException(status_code=500, detail="Failed to Initialize")
    
    chain = resource["chain"]
    response = chain.invoke({"question": question})

    if response:
        return response
    raise HTTPException(status_code=500, detail="Unable to Generate Response")