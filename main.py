import os
import shutil
import tempfile
import logging
from fastapi import FastAPI,UploadFile,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.document_loaders import TextLoader,PyPDFLoader,Docx2txtLoader,CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# load env
load_dotenv()

#init fastapi
app = FastAPI()

#cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#config logger
logger = logging.getLogger("uvicorn.error")

#Ai model api key
GEIMIN_API_KEY = os.getenv("GOOGLE_API_KEY")

#Init llm modal
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite",google_api_key=GEIMIN_API_KEY,temperature=0.1)

#Document Loaders
LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
}


#Config embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#Init vectorstore
vectorstore = InMemoryVectorStore(embeddings)

#Config for chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150)

class chatMessge(BaseModel):
    role:str
    content:str

class chatRequest(BaseModel):
    message:str
    history:list[chatMessge] = []
    temperature:float = Field(default=0.1, ge=0, le=1)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt", ".md"}

@app.get("/")
def greetUser():
    return 'hello user'

@app.post("/upload")
def uploadFile(file: UploadFile):
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt", ".md"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400,f"Unsupported file format {ext}")

    with tempfile.NamedTemporaryFile(delete=False,suffix=ext) as tmp:
        shutil.copyfileobj(file.file,tmp)
        tmp_path = tmp.name

    try:
        loader = LOADERS[ext](tmp_path)
        file_data = loader.load()
    finally:
        os.remove(tmp_path)

    #attach the original filename so chunks/vectors can be traced back to their source doc
    for doc in file_data:
        doc.metadata["filename"] = file.filename

    #chunking
    chunks = splitter.split_documents(file_data)

    #Load in memory vector store
    vectorstore.add_documents(chunks)

    return {
        "filename": file.filename,
        "content_type": file.content_type
    }

@app.post('/chat')
def chat(req:chatRequest):

    #Search in vector store
    results = vectorstore.similarity_search(req.message,k=4)
    context = "\n\n".join(r.page_content for r in results)
    # logger.info(f"context:{context}")
    messages = [
        SystemMessage(content=(
            "You are a helpful assistant answering questions about an uploaded document. "
            "Use the context below to answer naturally and conversationally, like a normal chatbot "
            "would — rephrase, summarize, and format the information (lists, short paragraphs, bold "
            "for key terms, etc.) so it's easy to understand, rather than copy-pasting raw excerpts "
            "from the document. "
        "If the context does not contain information relevant to the question, politely say you "
            "don't have that information in the uploaded document — do not answer from outside "
            "knowledge and do not make anything up.\n\n"
            f"Context:\n{context}"
        ))
    ]

    for m in req.history:
        messages.append(HumanMessage(m.content) if m.role=='user' else AIMessage(m.content))
    messages.append(HumanMessage(req.message))
    logger.info(f"req.temperature={req.temperature}")
    response = llm.bind(temperature=req.temperature).invoke(messages)

    return {"answer":response.content[0]['text']}

