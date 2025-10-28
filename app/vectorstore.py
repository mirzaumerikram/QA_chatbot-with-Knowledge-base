import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.v2.vectorstores import PGVectorStore, AsyncPGVectorStore
from langchain_postgres import PGEngine

# Load env variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DATABASE_URL or not OPENAI_API_KEY:
    raise RuntimeError("Missing DATABASE_URL or OPENAI_API_KEY in .env")

# Create async SQLAlchemy engine
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Wrap in PGEngine for Postgres vectorstore
pg_engine = PGEngine.from_engine(engine=async_engine)


async def get_vectorstore():
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Create async PGVectorStore instance with factory method
    vs = await AsyncPGVectorStore.create(
        embedding_service=embeddings,
        engine=pg_engine,
        table_name="langchain_documents"
    )

    # Create synchronous PGVectorStore wrapper
    vectorstore = PGVectorStore.__new__(PGVectorStore)
    PGVectorStore.__init__(
        vectorstore,
        key=PGVectorStore._PGVectorStore__create_key,
        engine=pg_engine,
        vs=vs
    )
    return vectorstore
