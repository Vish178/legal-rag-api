# ⚖️ Legal RAG API

A high-performance Retrieval-Augmented Generation (RAG) API designed to answer queries related to **Indian Constitutional, Criminal, and Labour Law**.

Built with **FastAPI**, containerized with **Docker**, and powered by **LangChain** and **ChromaDB**.

---

## 🚀 Key Features

- **Smart Routing**  
  Automatically classifies user questions into domains (Constitutional, Criminal, Labour) to query the correct legal database.

- **RAG Architecture**  
  Retrieves specific legal sections (Articles, Sections, Acts) to ground the LLM's answers in reality, minimizing hallucinations.

- **Production Ready**  
  Fully containerized with Docker for easy deployment on Render, Hugging Face, or AWS.

- **Source Citations**  
  Returns the specific legal text chunks used to generate the answer.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn  
- **AI Orchestration:** LangChain  
- **Vector Database:** ChromaDB (Persistent storage)  
- **LLM Provider:** OpenRouter (GPT-OSS-20B / GPT-4o)  
- **Embeddings:** HuggingFace (`sentence-transformers/all-mpnet-base-v2`)  
- **Deployment:** Docker  

---

## 🔌 API Documentation

### Base URL
```
https://deadpool17-legal-rag-api.hf.space
```

### 1. Health Check
```
GET /
```
Returns a simple status message.

### 2. Chat Endpoint
```
GET /chat/{question}
```

**Parameters**
- `question` (string): The legal question you want to ask.

**Example Request**
```bash
curl "https://deadpool17-legal-rag-api.hf.space/chat/What%20is%20article%20370%20?"
```

**Example Response**
```json
{
  "answer": "Article 370 is a provision in the Constitution of India that lays out temporary provisions with respect to the State of Jammu and Kashmir.",
  "context": [
    {
      "id": "bd136938-98ea-48fd-a39f-524395c825c7",
      "metadata": {
        "domain": "constitutional",
        "type": "article_clause",
        "source": "Constitution of India",
        "title": "Temporary provisions with respect to the State of Jammu and Kashmir",
        "chunk_id": "article_370_4",
        "article": 370
      }
```

---

## 📦 Local Setup & Installation

Follow these steps to run the API on your local machine.

### Prerequisites
- Docker installed  
- Git installed  
- An API Key from OpenRouter  

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/legal-rag-api.git
cd legal-rag-api
```

### 2. Setup Environment Variables
Create a `.env` file in the root directory:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
MODEL_NAME=openai/gpt-oss-20b
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

### 3. Run with Docker (Recommended)
This command builds the container and downloads the necessary AI models (approx. 2GB).

```bash
# Build the image
docker build -t legal-api .

# Run the container (Port 7860 is default for Hugging Face)
docker run -p 7860:7860 --env-file .env legal-api
```

### 4. Access the API
Open your browser at:
```
http://localhost:7860/docs
```

---

## 📂 Project Structure

```plaintext
/legal-rag-api
│
├── main.py              # FastAPI Application & RAG Logic
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
├── .dockerignore        # Build optimization
│
└── Databases/           # Pre-indexed Vector Stores
    ├── chroma_constitution
    ├── chroma_criminal
    └── chroma_labour
```

---

## 🤝 Contributing

1. Fork the repository  
2. Create your feature branch  
   ```bash
   git checkout -b feature/NewFeature
   ```
3. Commit your changes  
   ```bash
   git commit -m "Add some NewFeature"
   ```
4. Push to the branch  
   ```bash
   git push origin feature/NewFeature
   ```
5. Open a Pull Request  

---

## 📄 License

This project is licensed under the **MIT License**.
