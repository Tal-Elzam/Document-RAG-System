# RAG System - Retrieval-Augmented Generation

מערכת RAG (Retrieval-Augmented Generation) לעיבוד וחיפוש במסמכים באמצעות Google Gemini API ו-PostgreSQL.

## תיאור הפרויקט

הפרויקט מורכב משני סקריפטים עיקריים:

1. **`index_documents.py`** - עיבוד מסמכים (PDF/DOCX), חלוקה לקטעים, יצירת embeddings ושמירה במסד נתונים
2. **`search_documents.py`** - חיפוש במסמכים באמצעות embeddings וקוסינוס סימילריות



## התקנה

### 1. שכפול הפרויקט

```bash
git clone <repository-url>
cd test
```

### 2. התקנת תלויות

```bash
pip install -r requirements.txt
```

### 3. הגדרת משתני סביבה

יצירת קובץ `.env` מהתבנית:

```bash
cp .env
```

עריכת קובץ `.env` והוספת הערכים שלך:

```
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_URL=postgresql://username:password@localhost:5432/rag_database
```



# צור מסד נתונים
CREATE DATABASE rag_db;

# צא מהקונסולה
\q
```



### עיבוד מסמך (`index_documents.py`)

עיבוד מסמך PDF או DOCX ליצירת embeddings ושמירה במסד הנתונים.

**פורמט בסיסי:**
```bash
python index_documents.py <path_to_file> [options]
```

**דוגמאות:**

```bash
# עיבוד מסמך PDF עם חלוקה בגודל קבוע (ברירת מחדל)
python index_documents.py document.pdf

# עיבוד מסמך DOCX עם חלוקה לפי משפטים
python index_documents.py document.docx --strategy sentence

# עיבוד עם חלוקה לפי פסקאות
python index_documents.py document.pdf --strategy paragraph

# עיבוד עם הגדרות מותאמות אישית
python index_documents.py document.pdf --strategy fixed_size --chunk_size 1500 --overlap 300
```
to example -  document.pdf == "C:\Users\Talel\OneDrive\שולחן העבודה\Tal Elzam.pdf"

**אפשרויות:**

- `--strategy`: אסטרטגיית חלוקה (`fixed_size`, `sentence`, `paragraph`)
  - `fixed_size`: חלוקה לקטעים בגודל קבוע עם חפיפה (ברירת מחדל)
  - `sentence`: חלוקה לפי משפטים
  - `paragraph`: חלוקה לפי פסקאות
  
- `--chunk_size`: גודל קטע בחלוקה בגודל קבוע (ברירת מחדל: 1000 תווים)

- `--overlap`: חפיפה בין קטעים בחלוקה בגודל קבוע (ברירת מחדל: 200 תווים)

- `--sentences_per_chunk`: מספר משפטים לקטע בחלוקה לפי משפטים (ברירת מחדל: 5)

### חיפוש במסמכים (`search_documents.py`)

חיפוש במסמכים שהוטמעו במסד הנתונים לפי שאילתה טקסטואלית.

**פורמט בסיסי:**
```bash
python search_documents.py "<query>" [options]
```

**דוגמאות:**

```bash
# חיפוש בסיסי (מחזיר 5 תוצאות)
python search_documents.py "מהו הנושא המרכזי של המסמך?"

# חיפוש עם מספר תוצאות מותאם
python search_documents.py "מידע על בינה מלאכותית" --top_k 10
```

**אפשרויות:**

- `--top_k`: מספר התוצאות המוחזרות (ברירת מחדל: 5)

## מבנה מסד הנתונים

הטבלה `document_chunks` מכילה את העמודות הבאות:

| עמודה | סוג | תיאור |
|-------|-----|-------|
| `id` | SERIAL PRIMARY KEY | מזהה ייחודי |
| `chunk_text` | TEXT | טקסט הקטע |
| `embedding` | vector(768) | וקטור ההטבעה |
| `filename` | VARCHAR(255) | שם הקובץ המקורי |
| `split_strategy` | VARCHAR(50) | אסטרטגיית החלוקה שנבחרה |
| `created_at` | TIMESTAMP | תאריך ההוספה (נוצר אוטומטית) |

## אסטרטגיות חלוקה

### 1. Fixed Size (גודל קבוע)
- חלוקה לקטעים בגודל קבוע עם חפיפה
- מתאים למסמכים ארוכים
- מאפשר שליטה על גודל הקטעים

### 2. Sentence-Based (לפי משפטים)
- חלוקה לפי משפטים
- שומר על הגיון טקסטואלי
- מתאים למסמכים בעלי מבנה ברור

### 3. Paragraph-Based (לפי פסקאות)
- חלוקה לפי פסקאות
- שומר על הקשר מלא
- מתאים למסמכים מובנים היטב




## מבנה הפרויקט

```
jeenai-test/
│
├── index_documents.py      # סקריפט לעיבוד מסמכים
├── search_documents.py     # סקריפט לחיפוש
├── requirements.txt        # תלויות Python
├── .env.                   # דוגמה לקובץ משתני סביבה
├── .gitignore              # קבצים להתעלמות מ-Git
└── README.md               # קובץ זה
```

