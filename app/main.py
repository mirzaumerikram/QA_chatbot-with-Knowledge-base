import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
from langchain_postgres import PGEngine
from starlette.concurrency import run_in_threadpool
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA

from app.db import async_engine, Base
from app.models import Document as DBDocument
from app.schemas import DocumentUploadResponse, AskRequest, AskResponse
from app.utils import extract_text_from_pdf
from app.vectorstore import get_vectorstore
from app.auth import auth_scheme

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("app")

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(f"Loaded .env from {os.path.abspath(dotenv_path)}")

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

AsyncSessionLocal = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    pg_engine = PGEngine.from_engine(engine=async_engine)
    try:
        await pg_engine.ainit_vectorstore_table(
            table_name="langchain_documents",
            vector_size=1536,
        )
    except Exception as e:
        if "relation \"langchain_documents\" already exists" not in str(e):
            raise
    logger.info("Database schema and vectorstore table initialized")
    yield
    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API for document upload and querying",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        raise
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Completed {request.method} {request.url} ({response.status_code}) in {duration_ms:.2f} ms")
    return response


@app.get("/secure-endpoint")
async def secure_route(token: str = Security(auth_scheme)):
    logger.info("Secure endpoint accessed")
    return {"message": "Access granted"}


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), token: str = Security(auth_scheme)):
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    logger.info(f"Uploading file: {filename}")

    result = await db.execute(select(DBDocument).where(DBDocument.filename == filename))
    existing_doc = result.scalar_one_or_none()
    if existing_doc:
        raise HTTPException(status_code=400, detail="Document already exists")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        with open(file_path, "wb") as f:
            f.write(contents)
        text = extract_text_from_pdf(file_path)
        chunks = chunk_text(text)
        docs = [Document(page_content=chunk, metadata={"filename": filename}) for chunk in chunks]

        doc = DBDocument(filename=filename, filepath=file_path)
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        vectorstore = await get_vectorstore()
        
        if hasattr(vectorstore, "aadd_documents"):
            await vectorstore.aadd_documents(docs)
            logger.info(f"Added {len(docs)} documents to vectorstore from {filename}")
        else:
             raise RuntimeError("Vectorstore missing aadd_documents async method")

        logger.info(f"File uploaded and indexed successfully: {filename}")
        return {"id": doc.id, "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db), token: str = Security(auth_scheme)):
    result = await db.execute(select(DBDocument))
    docs = result.scalars().all()
    return [{"id": d.id, "filename": d.filename} for d in docs]


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db), token: str = Security(auth_scheme)):
    result = await db.execute(select(DBDocument).where(DBDocument.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        if os.path.exists(doc.filepath):
            os.remove(doc.filepath)
        await db.delete(doc)
        await db.commit()
        return {"detail": "Document deleted"}
    except Exception as e:
        logger.error(f"Delete failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, token: str = Security(auth_scheme)):
    logger.info(f"Received question: {req.question}")
    try:
        vectorstore = await get_vectorstore()
        llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        retriever = vectorstore.as_retriever()
        retrieval_chain = RetrievalQA.from_llm(llm=llm, retriever=retriever)
        result = await retrieval_chain.ainvoke({"query": req.question})
        answer = result.get("result") or result.get("answer") or "No relevant answer found."

        docs = await vectorstore.asimilarity_search(req.question)
        if not docs:
            logger.warning("Vectorstore similarity search returned zero documents.")
        else:
            logger.info(f"Vectorstore returned {len(docs)} documents.")

        sources = []
        for doc in docs:
            if not doc.metadata:
                logger.warning(f"Document {doc} has no metadata.")
                sources.append("")
            elif "filename" not in doc.metadata:
                logger.warning(f"Document metadata keys: {list(doc.metadata.keys())} (missing 'filename').")
                sources.append("")
            else:
                sources.append(doc.metadata.get("filename"))

        logger.info(f"Returning sources: {sources}")
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logger.error(f"Ask endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process your query.")


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
