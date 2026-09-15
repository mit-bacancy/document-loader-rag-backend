import os
import shutil
import tempfile
import logging
from fastapi import FastAPI,UploadFile,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field
# from langchain_community.document_loaders import TextLoader,PyPDFLoader,Docx2txtLoader,CSVLoader
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.vectorstores import InMemoryVectorStore
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

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
# llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite",google_api_key=GEIMIN_API_KEY,temperature=0.1)

#Document Loaders
# LOADERS = {
#     ".pdf": PyPDFLoader,
#     ".docx": Docx2txtLoader,
#     ".csv": CSVLoader,
#     ".txt": TextLoader,
#     ".md": TextLoader,
# }


# #Config embeddings
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# #Init vectorstore
# vectorstore = InMemoryVectorStore(embeddings)

# #Config for chunking
# splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150)

class chatMessge(BaseModel):
    role:str
    content:str

class chatRequest(BaseModel):
    message:str
    history:list[chatMessge] = []
    temperature:float = Field(default=0.1, ge=0, le=1)

# ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt", ".md"}

# database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greetUser():
    return 'hello user'

# @app.post("/upload")
# def uploadFile(file: UploadFile):
#     ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt", ".md"}
#     ext = os.path.splitext(file.filename)[1].lower()

#     if ext not in ALLOWED_EXTENSIONS:
#             raise HTTPException(400,f"Unsupported file format {ext}")

#     with tempfile.NamedTemporaryFile(delete=False,suffix=ext) as tmp:
#         shutil.copyfileobj(file.file,tmp)
#         tmp_path = tmp.name
#         # logger.info(tmp_path)

#     try:
#         loader = LOADERS[ext](tmp_path)
#         file_data = loader.load()
#         # logger.info(f"filedata:{file_data}")
#     finally:
#         os.remove(tmp_path)

#     #attach the original filename so chunks/vectors can be traced back to their source doc
#     for doc in file_data:
#         doc.metadata["filename"] = file.filename

#     #chunking
#     chunks = splitter.split_documents(file_data)
#     # for i, chunk in enumerate(chunks):
#     #     logger.info(f"chunk[{i}] len={len(chunk.page_content)} meta={chunk.metadata} preview={chunk.page_content[:80]!r}")

#     #Load in memory vector store
#     vectorstore.add_documents(chunks)

#     # for doc_id, record in vectorstore.store.items():
#     #     vec = record["vector"]
#         # logger.info(f"id={doc_id} dim={len(vec)} vector_preview={vec[:5]} text_preview={record['text'][:60]!r}")

#     return {
#         "filename": file.filename,
#         "content_type": file.content_type
#     }

# @app.post('/chat')
# def chat(req:chatRequest):

#     #Search in vector store
#     results = vectorstore.similarity_search(req.message,k=4)
#     context = "\n\n".join(r.page_content for r in results)
#     # logger.info(f"context:{context}")
#     messages = [
#         SystemMessage(content=(
#             "You are a helpful assistant answering questions about an uploaded document. "
#             "Use the context below to answer naturally and conversationally, like a normal chatbot "
#             "would — rephrase, summarize, and format the information (lists, short paragraphs, bold "
#             "for key terms, etc.) so it's easy to understand, rather than copy-pasting raw excerpts "
#             "from the document. "
#         "If the context does not contain information relevant to the question, politely say you "
#             "don't have that information in the uploaded document — do not answer from outside "
#             "knowledge and do not make anything up.\n\n"
#             f"Context:\n{context}"
#         ))
#     ]

#     for m in req.history:
#         messages.append(HumanMessage(m.content) if m.role=='user' else AIMessage(m.content))
#     messages.append(HumanMessage(req.message))
#     logger.info(f"req.temperature={req.temperature}")
#     response = llm.bind(temperature=req.temperature).invoke(messages)

#     return {"answer":response.content[0]['text']}


# @app.get('/demo-practice')
# def demoPractice():
#     return 'true'
# io.StringIO

# Loaders = {
#     '.md': "read()",
#     '.txt':""
# }

ALLOWED_EXTENSIONS = {".txt", ".md"}

@app.post('/upload')
async def uploadFile(file:UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    # logger.info({ext})
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400,f'The extension {ext} is not allowed, upload files with this extensions {ALLOWED_EXTENSIONS}')

    # extracting the file content
    content = await file.read()
    text_data = content.decode('utf-8')
    logger.info({text_data})
    overlap = 10
    chunk_size = 100-overlap
    saperators = ["\n\n","\n","."," "]
    # loop over saperators -> split the texts -> any text that goes over chunk size saperate it with another saporater
    # for sap in saperators:

    #Chunking   
    chunks = chunking(text_data,saperators,chunk_size,0)
    chunks = merge_chunks(chunks,chunk_size)
    chunks = overlap_chunks(chunks,overlap)
    # for c in chunks:
    #     logger.info({c})
        

    # if(len(chunks.remaining_chunks)>0):
    #     chunks = chunking(text_data,saperators,chunk_size)

        # chunks = text_data.split(sap)
        # remaining_chunk = []
        # final_chunks = []
        # for chunk in chunks:
        #     if len(chunk)>chunk_size:
        #         remaining_chunk.push(chunk)
        #     else:
        #         final_chunks.push(chunk)
        # remaining_chunk.split()

        # logger.info(chunks)

    
    # for start in range(0,len(text_data),stride):
    #     logger.info(text_data[start:start-chunk_size])
    #     # logger.info({text})
    #     logger.info("")



    # with open(file,'r',encoding='utf-8') as file:
    #     content = file.read()

    return chunks

def chunking(text,saperators,chunk_size,i):
    sap = saperators[i]
    chunks = text.split(sap)
    remaining_chunks = []
    final_chunks = []
    for chunk in chunks:
        if len(chunk)>chunk_size:
            remaining_chunks.append(chunk)
        else:
            final_chunks.append(chunk)
    # chunks = chunking(text,sap,chunk_size)
    i+=1
    saperator_unavailable = True if i>=len(saperators) else False
    semi_final_chunk = []
    if len(remaining_chunks)>0 and not saperator_unavailable:
        for c in remaining_chunks:
            semi_final_chunk += chunking(c,saperators,chunk_size,i)
    else: 
        semi_final_chunk = remaining_chunks

    return final_chunks+semi_final_chunk

def merge_chunks(chunks,chunk_size):
    merged = []
    buffer = ""
    for c in chunks:
        if len(buffer)+len(c)<chunk_size:
            buffer = (buffer +" "+ c).strip() if buffer else c
        else:
            if buffer:
                merged.append(buffer)
            buffer = c
    if buffer:
        merged.append(buffer)
    return merged

def overlap_chunks(chunks,overlap):
    chunk_to_overlap = ""
    for i,c in enumerate(chunks):
        chunk_to_overlap = c[-(overlap):]
        if(i==0):
            logger.info({"c":c})
            logger.info({"overlap":overlap})
            logger.info({"overlap_chunk":c[-1:-(overlap)]})
            logger.info({"current_chunk":chunks[i]})
            logger.info({chunk_to_overlap})
            logger.info({'next chunk':chunks[i+1]})
            logger.info({'cut':chunk_to_overlap+" "+chunks[i+1]})
        # if(i>0):
        #     chunks[i] = chunks[i][0:(len(chunks[i])-overlap)]

        if((i+1)<len(chunks)):
            # chunks[i+1] = chunks[i+1][0:len(chunks[i+1])-overlap]
            chunks[i+1] = chunk_to_overlap+" "+chunks[i+1]
    return chunks












    # def recursive_split(text, seps):
    #     if len(text) <= chunk_size or not seps:
    #         return [text]
    #     sap, rest = seps[0], seps[1:]
    #     pieces = list(text) if sap == "" else text.split(sap)
    #     result = []
    #     for piece in pieces:
    #         if len(piece) > chunk_size:
    #             result.extend(recursive_split(piece, rest))
    #         elif piece:
    #             result.append(piece)
    #     return result