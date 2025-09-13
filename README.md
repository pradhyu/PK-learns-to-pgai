# pgai Example Setup

This guide will help you run pgai, pgvector, pgvectorscale, and Jupyter Notebook using Docker Compose.

## Prerequisites
- Docker and Docker Compose installed

## 1. Start the Services

```fish
# In your project directory
docker compose up -d
```

- Postgres (with pgvector) runs on port 5432
docker compose up -d
- Jupyter Notebook runs on port 8888 (token: pgai)


This will start:
- PostgreSQL (pgvector)
- Jupyter Notebook
- Vectorizer Worker (`timescale/pgai-vectorizer-worker`)
```fish
docker compose exec postgres psql -U pgai -d pgai_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker compose exec postgres psql -U pgai -d pgai_db -c "CREATE EXTENSION IF NOT EXISTS pgvectorscale;"
```

## 3. Create Vectors Table and Insert Embeddings

Example SQL:

```sql
CREATE TABLE IF NOT EXISTS items (
  id SERIAL PRIMARY KEY,
  embedding vector(3),
  description TEXT
);

INSERT INTO items (embedding, description) VALUES
  ('[0.1, 0.2, 0.3]', 'First item'),
  ('[0.4, 0.5, 0.6]', 'Second item');
```

Run in the Postgres container:

```fish
docker compose exec postgres psql -U pgai -d pgai_db
# Then paste the SQL above
```


## 4. Python Environment Setup with uv

Create and activate a virtual environment, then install dependencies using uv:

```fish
python3 -m venv .venv
source .venv/bin/activate
# If uv is not installed, run:
pip install uv
# Then install all requirements:
uv pip install -r requirements.txt
```

## 5. Interact with pgai from Jupyter

Open Jupyter Notebook at http://localhost:8888 (token: pgai)

See the provided notebook for Python code to interact with pgai.
