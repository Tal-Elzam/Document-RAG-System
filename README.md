# RAG System - Retrieval-Augmented Generation

A RAG (Retrieval-Augmented Generation) system for processing and searching documents using Google Gemini API and PostgreSQL.

## Project Description

The project consists of two main scripts:

1. **`index_documents.py`** - Processes documents (PDF/DOCX), splits them into chunks, creates embeddings, and saves them to a database
2. **`search_documents.py`** - Searches documents using embeddings and cosine similarity

## System Requirements

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Gemini API Key (available from [Google AI Studio](https://makersuite.google.com/app/apikey))

---

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `python-dotenv` - Environment variable management
- `psycopg2-binary` - PostgreSQL connection
- `google-generativeai` - Gemini API integration
- `pdfplumber` - PDF file reading
- `python-docx` - DOCX file reading
- `numpy` - Mathematical calculations
- `scikit-learn` - Cosine similarity calculation

### Step 2: Create Database

**Connect to PostgreSQL:**
```bash
# Windows (run Command Prompt as administrator)
psql -U postgres

# macOS/Linux
sudo -u postgres psql
```

**Create database:**
```sql
CREATE DATABASE rag_database;
\q
```

**Note:** If PostgreSQL is not running, start it:
- **Windows:** Open "Services" and start "postgresql-x64-XX"
- **macOS:** `brew services start postgresql`
- **Linux:** `sudo systemctl start postgresql`

### Step 3: Create `.env` File

Create a file named `.env` in the project directory:

**Windows:**
```bash
notepad .env
```

**macOS/Linux:**
```bash
nano .env
```

**Enter the following content:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_URL=postgresql://username:password@localhost:5432/rag_database
```

**How to get Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in the `.env` file

**POSTGRES_URL Example:**
- If the username is `postgres` and password is `mypassword`:
  ```
  POSTGRES_URL=postgresql://postgres:mypassword@localhost:5432/rag_database
  ```
- If there is no password:
  ```
  POSTGRES_URL=postgresql://postgres@localhost:5432/rag_database
  ```

---

## Usage

### Indexing Documents (`index_documents.py`)

This script processes a document (PDF or DOCX), splits it into chunks, creates embeddings, and saves everything to the database.

**Basic format:**
```bash
python index_documents.py <path_to_file> [options]
```

**Options:**
- `--strategy` - Splitting strategy (`fixed_size`, `sentence`, `paragraph`) - Default: `fixed_size`
- `--chunk_size` - Chunk size for fixed_size strategy (characters) - Default: `1000`
- `--overlap` - Overlap between chunks for fixed_size strategy (characters) - Default: `200`
- `--sentences_per_chunk` - Number of sentences per chunk for sentence strategy - Default: `5`

**Examples:**

```bash
# Basic PDF processing
python index_documents.py document.pdf

# DOCX processing
python index_documents.py report.docx

# With full path
python index_documents.py "C:\Users\Talel\OneDrive\Desktop\document.pdf"

# Sentence-based splitting
python index_documents.py document.pdf --strategy sentence

# Paragraph-based splitting
python index_documents.py document.pdf --strategy paragraph

# Custom fixed_size
python index_documents.py document.pdf --strategy fixed_size --chunk_size 1500 --overlap 300

# Custom sentence-based
python index_documents.py document.pdf --strategy sentence --sentences_per_chunk 10
```

---

### Searching Documents (`search_documents.py`)

This script searches documents indexed in the database using a text query.

**Basic format:**
```bash
python search_documents.py "<query>" [options]
```

**Options:**
- `--top_k` - Number of results to return - Default: `5`

**Examples:**

```bash
# Basic search (5 results)
python search_documents.py "What is the main topic of the document?"

# Custom number of results
python search_documents.py "information about artificial intelligence" --top_k 10

# Additional examples
python search_documents.py "What is the product price?"
python search_documents.py "explanation of algorithm"
python search_documents.py "When did the meeting take place?"
```
