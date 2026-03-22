# 📄 Conversational Research Paper Agent

An end-to-end, containerized Retrieval-Augmented Generation (RAG) system that allows users to chat with complex academic research papers. The agent extracts document context, maintains conversational memory, and streams responses in real-time, effectively allowing users to "interact with the authors."

## 🚀 Key Features
* **Layout-Aware PDF Parsing:** Utilizes `PyMuPDF` to accurately extract text from complex academic layouts (two-column formats, tables, etc.) without scrambling the data.
* **Stateful Conversational Memory:** Integrates **Redis** to persist user chat sessions, allowing for deep, multi-turn technical interrogations of the paper.
* **Asynchronous Streaming (SSE):** Features a ChatGPT-style typing interface via Server-Sent Events, significantly reducing perceived latency.
* **Production-Ready Observability:** Instrumented with **Prometheus** and **Grafana** to monitor API latency, token usage, and endpoint health.
* **Fully Containerized:** The entire architecture (Frontend, Backend, Database, and Metrics) is orchestrated using Docker Compose for seamless deployment.

## 🛠️ Architecture & Tech Stack
* **Frontend:** Streamlit
* **Backend:** FastAPI, Python
* **LLM Orchestration:** LangChain, OpenAI (GPT-4o)
* **Vector Store:** ChromaDB
* **Session Memory:** Redis
* **Infrastructure:** Docker, Docker Compose
* **Observability:** Prometheus, Grafana

## ⚙️ How to Run Locally

### Prerequisites
* Docker and Docker Compose installed on your machine.
* An OpenAI API Key.

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/HARSVARDH/conversational-research-agent.git](https://github.com/HARSVARDH/conversational-research-agent.git)
   cd conversational-research-agent
