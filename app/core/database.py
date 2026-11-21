from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
db_user = os.environ["POSTGRES_ADMIN_USER"]
db_pass = os.environ["POSTGRES_ADMIN_PASS"]
db_host = os.getenv("POSTGRES_HOST", "localhost")

db_url = URL.create(
    "postgresql+psycopg",
    username=db_user,
    password=db_pass,
    host=db_host,
    database=db_user,
    # Limit search_path to public, so the tiger and topology tables from the PostGIS image stay hidden.
    # Otherwise autogenerate would drop them.
    query={"options": "-csearch_path=public"},
)

engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(engine)

def get_session():
    with SessionLocal() as session:
        yield session
