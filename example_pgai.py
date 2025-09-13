import os
import pgai
import psycopg
from pgai.worker import Worker
import openai
import numpy as np

DB_URL = os.getenv("DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Install PGAI database components
pgai.install(DB_URL)

# Connect to DB and create a sample table
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wiki (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL
            )
        """)
        conn.commit()

# Create the vectorizer
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ai.create_vectorizer(
                'wiki'::regclass,
                if_not_exists => true,
                loading => ai.loading_column(column_name=>'text'),
                embedding => ai.embedding_openai(model=>'text-embedding-ada-002', dimensions=>'1536'),
                destination => ai.destination_table(view_name=>'wiki_embedding')
            )
        """)
        conn.commit()

# Insert sample data
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO wiki (url, title, text) VALUES
            ('https://en.wikipedia.org/wiki/pgai', 'pgai', 'pgai is a Python library that turns PostgreSQL into the retrieval engine behind robust, production-ready RAG and Agentic applications.')
        """)
        conn.commit()

# Run the vectorizer worker (once for demo)
worker = Worker(DB_URL, once=True)
worker.run()

# Semantic search example
client = openai.OpenAI(api_key=OPENAI_API_KEY)
query = "What is pgai?"
response = client.embeddings.create(
    model="text-embedding-ada-002",
    input=query,
    encoding_format="float",
)
embedding = np.array(response.data[0].embedding)

with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT w.id, w.url, w.title, w.text, w.embedding <=> %s AS distance
            FROM wiki_embedding w
            ORDER BY distance
            LIMIT 1
        """, (embedding.tolist(),))
        result = cur.fetchone()
        print(result)
