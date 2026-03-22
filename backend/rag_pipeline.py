import os
import json
import redis
import asyncio
from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
vector_store = None

def process_pdf(file_path: str):
    global vector_store
    
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(chunks, embeddings)
    
    return {"status": "success", "chunks": len(chunks)}


def get_chat_history(session_id: str):
    history = redis_client.get(f"chat:{session_id}")
    if history:
        return json.loads(history)
    return []

def save_chat_history(session_id: str, history: list):
    redis_client.setex(f"chat:{session_id}", 86400, json.dumps(history))


async def ask_question_stream(session_id: str, question: str):
    if not vector_store:
        yield "Please upload a document first."
        return
    

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2, streaming=True)
    
    raw_history = get_chat_history(session_id)
    formatted_history = []
    for msg in raw_history:
        if msg["role"] == "user":
            formatted_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            formatted_history.append(AIMessage(content=msg["content"]))
            
    system_prompt = (
        "You are the author of the provided research paper. "
        "Answer the user's questions in the first person ('I', 'we'), "
        "explaining your methodology, code, and conclusions clearly. "
        "If the user asks for code implementation not explicitly written in the paper, "
        "provide a highly accurate inferred implementation based on your described architecture. "
        "If the paper does not contain the answer, state that it falls outside the scope of your current research.\n\n"
        "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"), 
        ("human", "{input}"),
    ])

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    full_answer = ""
    async for chunk in rag_chain.astream({
        "input": question,
        "chat_history": formatted_history 
    }):
        if "answer" in chunk:
            text_chunk = chunk["answer"]
            full_answer += text_chunk
            yield text_chunk 
            await asyncio.sleep(0.01)

    raw_history.append({"role": "user", "content": question})
    raw_history.append({"role": "assistant", "content": full_answer})
    save_chat_history(session_id, raw_history)