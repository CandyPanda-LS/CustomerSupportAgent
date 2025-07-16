# Customer Support Agent

This is a customer support agent that can help you with your queries.

## Setup

### 1. Install Packages

Install the required packages using the following command:

```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

Run a local PostgreSQL instance using Docker:

```bash
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```

### 3. Setup Pinecone

Run a local Pinecone instance using Docker:

```bash
docker run -it -p 8000:8000 --env-file .env pinecone/pinecone-emulator:latest
```

### 4. Create .env file

Create a `.env` file in the root of the project and add the following variables:

```
PINECONE_API_KEY=dummy-key
PINECONE_ENVIRONMENT=local
PINECONE_INDEX_NAME=customer-support
OPENAI_API_KEY=your_openai_api_key
MISTRAL_API_KEY=your_mistral_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=mysecretpassword
PG_DB=postgres
```
