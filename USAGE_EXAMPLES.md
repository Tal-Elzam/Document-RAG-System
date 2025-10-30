# דוגמאות שימוש - RAG System

מדריך מעשי להרצת הסקריפטים של מערכת RAG.

## הכנה ראשונית

### 1. התקנת התלויות
```bash
pip install -r requirements.txt
```

### 2. יצירת קובץ .env
יצר קובץ `.env` בתיקיית הפרויקט עם התוכן הבא:
```
GEMINI_API_KEY=your_api_key_here
POSTGRES_URL=postgresql://username:password@localhost:5432/rag_database
```

### 3. יצירת מסד נתונים (אם עוד לא קיים)
```bash
# התחבר ל-PostgreSQL
psql -U postgres

# צור מסד נתונים
CREATE DATABASE rag_database;

# צא
\q
```

---

## שימוש ב-index_documents.py

### עיבוד מסמך PDF בסיסי
```bash
python index_documents.py document.pdf
```

### עיבוד מסמך DOCX
```bash
python index_documents.py report.docx
```

### עיבוד עם נתיב מלא
```bash
python index_documents.py "C:\Users\Talel\Documents\my_file.pdf"
```

### עיבוד עם חלוקה לפי משפטים
```bash
python index_documents.py document.pdf --strategy sentence
```

### עיבוד עם חלוקה לפי פסקאות
```bash
python index_documents.py document.pdf --strategy paragraph
```

### עיבוד עם הגדרות מותאמות אישית (גודל קבוע)
```bash
# קטעים של 1500 תווים עם חפיפה של 300
python index_documents.py document.pdf --strategy fixed_size --chunk_size 1500 --overlap 300
```

### עיבוד עם חלוקה לפי משפטים מותאמת
```bash
# 10 משפטים בכל קטע
python index_documents.py document.pdf --strategy sentence --sentences_per_chunk 10
```

---

## שימוש ב-search_documents.py

### חיפוש בסיסי (5 תוצאות)
```bash
python search_documents.py "מהו הנושא המרכזי של המסמך?"
```

### חיפוש באנגלית
```bash
python search_documents.py "What is artificial intelligence?"
```

### חיפוש עם מספר תוצאות מותאם
```bash
# קבלת 10 תוצאות
python search_documents.py "מידע על בינה מלאכותית" --top_k 10
```

### דוגמאות שאילתות נוספות
```bash
# חיפוש ספציפי
python search_documents.py "מה המחיר של המוצר?"

# חיפוש מושג
python search_documents.py "הסבר על אלגוריתם"

# חיפוש תאריכים
python search_documents.py "מתי התקיים המפגש?"

# חיפוש שמות
python search_documents.py "מי המנהל של הפרויקט?"
```

---

## סדר עבודה מומלץ

### שלב 1: עיבוד המסמך הראשון
```bash
# עיבוד המסמך שלך
python index_documents.py my_document.pdf
```

**פלט צפוי:**
```
מעבד קובץ: my_document.pdf
מחלץ טקסט מהקובץ...
נחלץ טקסט באורך 15432 תווים
מחלק לקטעים לפי אסטרטגיה: fixed_size...
נוצרו 15 קטעים
יוצר embeddings...
מעבד קטע 15/15...
מכניס 15 קטעים למסד הנתונים...
✓ הטמעת המסמך הושלמה בהצלחה!
  קובץ: my_document.pdf
  מספר קטעים: 15
  אסטרטגיית חלוקה: fixed_size
```

### שלב 2: חיפוש במסמך
```bash
python search_documents.py "מה הנושא המרכזי?"
```

**פלט צפוי:**
```
מחפש: 'מה הנושאentralי?'
------------------------------------------------------------
יוצר embedding לשאילתה...
מחפש במסד הנתונים...

נמצאו 5 קטעים דומים:

============================================================
תוצאה #1 (דמיון: 0.8542)
קובץ: my_document.pdf
אסטרטגיית חלוקה: fixed_size
מזהה: 7

קטע:
[טקסט הקטע הרלוונטי...]
```

### שלב 3: עיבוד מסמכים נוספים
```bash
# ניתן לעבד כמה מסמכים שאתה רוצה
python index_documents.py document1.pdf
python index_documents.py document2.docx
python index_documents.py report.pdf --strategy paragraph
```

כל המסמכים יישמרו באותה טבלה, ותוכל לחפש בכולם יחד!

---

## פתרון בעיות נפוצות

### שגיאה: "קובץ לא נמצא"
```bash
# ודא שאתה בתיקייה הנכונה או השתמש בנתיב מלא
cd "C:\Users\Talel\OneDrive\שולחן העבודה\jeenai test"
python index_documents.py my_file.pdf
```

### שגיאה: "חיבור למסד נתונים נכשל"
```bash
# בדוק את POSTGRES_URL בקובץ .env
# ודא ש-PostgreSQL פועל
```

### שגיאה: "API Key לא תקין"
```bash
# ודא שה-GEMINI_API_KEY נכון בקובץ .env
# ודא שיש חיבור לאינטרנט
```

---

## טיפים

1. **עיבוד קבצים גדולים**: אם המסמך גדול מאוד, השתמש ב-`--chunk_size` גדול יותר כדי להפחית את מספר ה-calls ל-API.

2. **חיפוש מהיר**: אם יש לך הרבה מסמכים, השתמש ב-`--top_k` קטן יותר לחיפוש מהיר יותר.

3. **אסטרטגיית חלוקה**:
   - `fixed_size` - טוב למסמכים ארוכים ומבנה לא ברור
   - `sentence` - טוב למסמכים עם מבנה ברור
   - `paragraph` - טוב למסמכים מובנים היטב

4. **עיבוד מספר קבצים**: ניתן לעבד כמה מסמכים ברצף - הם יישמרו כולם באותה טבלה!

---

## דוגמה מלאה: עיבוד וחיפוש

```bash
# 1. עיבוד מסמך
python index_documents.py technical_report.pdf --strategy sentence

# 2. חיפוש מידע ספציפי
python search_documents.py "מה הטכנולוגיה הראשית בפרויקט?"

# 3. חיפוש עם יותר תוצאות
python search_documents.py "בינה מלאכותית" --top_k 10

# 4. עיבוד מסמך נוסף
python index_documents.py meeting_notes.docx --strategy paragraph

# 5. חיפוש בכל המסמכים יחד
python search_documents.py "מה הוחלט בפגישה?"
```

