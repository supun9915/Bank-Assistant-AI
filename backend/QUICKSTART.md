# Quick Start Guide - Smart Banking Assistant

## ⚡ Quick Setup (5 minutes)

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Git (optional)

---

## 🚀 Steps

### 1. Install Dependencies

**Windows:**

```bash
# Run the setup script
setup.bat
```

**Linux/Mac:**

```bash
# Make script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

**Or manually:**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install packages
python -m pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

---

### 2. Setup Database

```sql
-- Login to MySQL
mysql -u root -p

-- Create database and tables
SOURCE schema.sql;

-- Or copy the SQL from schema.sql and paste it
```

---

### 3. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
# Windows: notepad .env
# Linux/Mac: nano .env
```

Update these values in `.env`:

```
DB_PASSWORD=your_mysql_password
```

---

### 4. Run the Server

```bash
python -m uvicorn main:app --reload
```

.\venv\Scripts\activate
uvicorn main:app --reload

Server will start at: http://localhost:8000

---

### 5. Test the API

**Option 1: Browser**

- Open http://localhost:8000/docs
- Try the `/api/chat` endpoint

**Option 2: Test Script**

```bash
python test_chatbot.py
```

**Option 3: cURL**

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is my balance?\"}"
```

---

## 🧪 Sample Queries

Try these in the API:

```json
{"message": "Hello"}
{"message": "What is my account balance?"}
{"message": "Show my recent transactions"}
{"message": "I need a loan"}
{"message": "What are your business hours?"}
```

---

## 🐛 Common Issues

### "Can't connect to MySQL"

- Make sure MySQL is running
- Check credentials in `.env`

### "spaCy model not found"

- Run: `python -m spacy download en_core_web_sm`

### "Port 8000 already in use"

- Use: `python -m uvicorn main:app --reload --port 8001`

---

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.

---

## 🎯 Success Checklist

- [ ] Python 3.8+ installed
- [ ] MySQL running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] spaCy model downloaded
- [ ] Database created (schema.sql imported)
- [ ] .env configured
- [ ] Server starts without errors
- [ ] API responds to test queries

---

**Need help?** Check the [README.md](README.md) for detailed instructions and troubleshooting.
