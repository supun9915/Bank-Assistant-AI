# Quick Start Guide - Smart Banking Assistant

## ⚡ Quick Setup

### Prerequisites

- Python 3.8+
- MySQL 8.0+

---

## 🚀 Steps

### 1. Install Dependencies

**Windows (automated):**

```bat
setup.bat
```

**Or manually:**

```bat
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Linux/Mac (automated):**

```bash
chmod +x setup.sh
./setup.sh
```

**Or manually:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 2. Setup Database

Apply all versioned migrations to create the database and tables:

```bat
# Windows
.\venv\Scripts\activate
python migrate.py up
```

```bash
# Linux/Mac
source venv/bin/activate
python migrate.py up
```

This auto-creates the `banking_chatbot` database and applies all migrations in order.

**Check migration status at any time:**

```bash
python migrate.py status
```

---

### 3. Configure Environment

```bat
# Windows
copy .env.example .env
notepad .env
```

```bash
# Linux/Mac
cp .env.example .env
nano .env
```

Update `.env` with your MySQL credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=banking_chatbot
DB_PORT=3306
```

---

### 4. Train the AI Model

Run this **once** before starting the server (or whenever `intents/training_data.json` changes):

```bat
# Windows
.\venv\Scripts\activate
python train_model.py
```

```bash
# Linux/Mac
source venv/bin/activate
python train_model.py
```

This generates `models/chatbot_model.keras`, `models/words.pkl`, and `models/classes.pkl`.

---

### 5. Start the Server

```bat
# Windows
.\venv\Scripts\activate
uvicorn main:app --reload
```

```bash
# Linux/Mac
source venv/bin/activate
uvicorn main:app --reload
```

Server starts at: **http://localhost:8000**

---

### 6. Test the API

**Option 1: Interactive Docs**

Open http://localhost:8000/docs and try the `/api/chat` endpoint.

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

- Make sure MySQL service is running
- Verify credentials in `.env` match your MySQL setup

### "Model file not found" / chatbot not responding correctly

- Run `python train_model.py` to generate the model files

### "Port 8000 already in use"

```bash
uvicorn main:app --reload --port 8001
```

---

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.

---

## 🎯 Success Checklist

- [ ] Python 3.8+ installed
- [ ] MySQL running
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations applied (`python migrate.py up`)
- [ ] `.env` configured with correct DB credentials
- [ ] Model trained (`python train_model.py`)
- [ ] Server starts without errors (`uvicorn main:app --reload`)
- [ ] API responds to test queries

---

**Need help?** Check the [README.md](README.md) for detailed instructions and troubleshooting.
