# Smart Banking Assistant - Backend API

A complete AI-powered banking chatbot backend built with FastAPI, NLTK, TensorFlow/Keras, and MySQL.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip package manager

### 🏃 Fast Setup (For Windows)

```bat
# 1. Run the automated setup script
setup.bat

# 2. Setup database (in MySQL)
mysql -u root -p < schema.sql

# 3. Configure credentials — copy .env.example to .env and set DB_PASSWORD
copy .env.example .env

# 4. Train the AI model (required once before first run)
.\venv\Scripts\activate
python train_model.py

# 5. Start the server
uvicorn main:app --reload
```

### 🏃 Fast Setup (For Linux/Mac)

```bash
# 1. Run the automated setup script
chmod +x setup.sh
./setup.sh

# 2. Setup database (in MySQL)
mysql -u root -p < schema.sql

# 3. Configure credentials — copy .env.example to .env and set DB_PASSWORD
cp .env.example .env

# 4. Train the AI model (required once before first run)
source venv/bin/activate
python train_model.py

# 5. Start the server
uvicorn main:app --reload
```

**🎉 Server running at:** http://localhost:8000

**📚 API Docs:** http://localhost:8000/docs

---

## 📋 Features

- **Natural Language Processing**: Intent classification using an NLTK + TensorFlow/Keras ANN (trained via `train_model.py`)
- **Smart Responses**: Context-aware replies based on user intent
- **Database Integration**: MySQL for user accounts, transactions, and knowledge base
- **Learning System**: Stores unknown questions for future improvements
- **RESTful API**: Clean, documented FastAPI endpoints
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Ready for frontend integration

---

## 🛠️ Detailed Installation

### 1. Clone and Navigate to Project

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the AI Model

```bash
python train_model.py
```

This generates `models/chatbot_model.keras`, `models/words.pkl`, and `models/classes.pkl`. Run this once before starting the server, and again whenever `intents/training_data.json` is updated.

### 5. Setup Database

**Option 1: Using MySQL Command Line**

```bash
mysql -u root -p < schema.sql
```

**Option 2: Manual Setup**

```sql
-- Login to MySQL
mysql -u root -p

-- Run the schema file
SOURCE schema.sql;

-- Or copy-paste the SQL commands from schema.sql
```

### 6. Configure Database Connection

Create a `.env` file from the template (recommended):

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Then edit `.env` with your MySQL credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=banking_chatbot
DB_PORT=3306
```

> The defaults in `.env.example` use password `mysql`. Update `DB_PASSWORD` to match your MySQL setup.

---

## 🚀 Starting the Application

### 1. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 2. Start the Server

```bash
uvicorn main:app --reload
```

**Options:**

- `--reload`: Auto-restart on code changes (development mode)
- `--host 0.0.0.0`: Allow external connections
- `--port 8000`: Specify port (default: 8000)

**Example with custom port:**

```bash
uvicorn main:app --reload --port 5000
```

### 3. Verify Server is Running

Open your browser and navigate to:

- **Health Check**: http://localhost:8000/
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

---

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Click on "POST /api/chat"
3. Click "Try it out"
4. Enter test data:
   ```json
   {
     "user_id": 1,
     "message": "What is my balance?"
   }
   ```
5. Click "Execute"

### Using Postman

Import the [Smart_Banking_Assistant.postman_collection.json](Smart_Banking_Assistant.postman_collection.json) file into Postman.

### Using curl

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "message": "What is my balance?"}'
```

### Using Python Test Script

```bash
python test_chatbot.py
```

---

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed file organization.

---

## 🔧 Troubleshooting

### Virtual environment not activating

**Windows:**

```bash
# If you get execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MySQL connection errors

- Verify MySQL is running: `mysql -u root -p`
- Check credentials in [db.py](db.py)
- Ensure database exists: `SHOW DATABASES;`

### Model files not found / chatbot not responding correctly

```bash
python train_model.py
```

This generates the required `models/chatbot_model.keras`, `models/words.pkl`, and `models/classes.pkl` files.

### Port already in use

```bash
# Use a different port
uvicorn main:app --reload --port 8001
```

### Module not found errors

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Additional Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [API_EXAMPLES.md](API_EXAMPLES.md) - API usage examples
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration options
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview

## 📡 API Endpoints

### 1. Health Check

```http
GET /
```

Response:

```json
{
  "status": "online",
  "message": "Smart Banking Assistant API is running",
  "version": "1.0.0"
}
```

### 2. Chat Endpoint

```http
POST /api/chat
```

Request Body:

```json
{
  "message": "What is my account balance?",
  "user_id": 1
}
```

Response:

```json
{
  "reply": "Your current account balance is $5,250.00.",
  "intent": "BALANCE",
  "confidence": 0.9,
  "data": {
    "balance": 5250.0
  }
}
```

## 🧪 Testing Examples

### Using cURL

```bash
# Greeting
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello\"}"

# Check Balance
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is my balance?\"}"

# Get Transactions
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Show my recent transactions\"}"

# Loan Inquiry
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"I need a loan\"}"
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/chat"
payload = {"message": "What is my account balance?"}

response = requests.post(url, json=payload)
print(response.json())
```

### Using Postman

1. Create a new POST request to `http://localhost:8000/api/chat`
2. Set Headers: `Content-Type: application/json`
3. Set Body (raw JSON):

```json
{
  "message": "Show my transactions",
  "user_id": 1
}
```

## 🧠 Supported Intents

| Intent           | Keywords                         | Example Queries                                    |
| ---------------- | -------------------------------- | -------------------------------------------------- |
| **GREETING**     | hello, hi, hey                   | "Hello", "Good morning"                            |
| **BALANCE**      | balance, money, account          | "What is my balance?", "How much money do I have?" |
| **TRANSACTIONS** | transactions, history, statement | "Show my transactions", "Recent purchases"         |
| **LOAN**         | loan, credit, borrow             | "I need a loan", "Apply for credit"                |
| **UNKNOWN**      | (fallback)                       | Any unrecognized query                             |

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── db.py                   # Database connection and queries
├── nlp.py                  # NLP processing with NLTK
├── train_model.py          # ANN training script
├── requirements.txt        # Python dependencies
├── schema.sql              # MySQL database schema
├── .env.example            # Environment variables template
├── README.md               # This file
├── intents/                # Training data and intent definitions
│   ├── training_data.json  # ANN training patterns
│   ├── intent_keywords.json # Keyword fallback lists
│   └── intent_info.json    # Intent metadata
├── models/                 # Pydantic models + trained ANN artefacts
│   ├── __init__.py
│   ├── chat_models.py      # Chat request/response models
│   ├── chatbot_model.keras # Trained Keras model (generated)
│   ├── words.pkl           # Stemmed vocabulary (generated)
│   └── classes.pkl         # Intent labels (generated)
├── routes/                 # API routes
│   ├── __init__.py
│   └── chat.py             # Chat endpoint
└── services/               # Business logic
    ├── __init__.py
    └── chat_service.py     # Chat processing service
```

## 🔍 How It Works

1. **User Input**: User sends a message via POST /api/chat
2. **Intent Detection**: NLTK preprocesses the text (tokenization, stemming) and the trained TensorFlow/Keras ANN classifies the intent; keyword matching is used as a fallback
3. **Request Routing**: Based on intent, the appropriate handler is called
4. **Data Retrieval**: If needed, data is fetched from MySQL database
5. **Response Generation**: A structured response is created and returned
6. **Learning**: Unknown questions are saved to the database

## 🗃️ Database Tables

### users

- Stores user information (id, name, email)

### accounts

- Stores account details and balances
- Links to users table

### transactions

- Stores transaction history
- Links to accounts table

### knowledge

- Pre-defined Q&A pairs
- Used for answering common questions

### unknown_questions

- Stores unrecognized queries
- Used for improving the bot

## 🔒 Security Notes

⚠️ **For Production Use**:

1. Use strong passwords and secure database credentials
2. Implement authentication and authorization
3. Use environment variables for sensitive data
4. Enable HTTPS/TLS
5. Implement rate limiting
6. Update CORS settings to allow only specific origins
7. Add input validation and sanitization
8. Use prepared statements (already implemented)

## 🐛 Troubleshooting

### Database Connection Error

```
Error: Can't connect to MySQL server
```

**Solution**: Check if MySQL is running and credentials in `.env` are correct

### spaCy Model Not Found

```
OSError: Can't find model 'en_core_web_sm'
```

**Solution**: Run `python -m spacy download en_core_web_sm`

### Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

### Port Already in Use

```
Error: Address already in use
```

**Solution**: Use a different port: `uvicorn main:app --reload --port 8001`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [spaCy Documentation](https://spacy.io/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🎓 Learning Objectives

This project demonstrates:

- RESTful API design with FastAPI
- Natural Language Processing with spaCy
- Database integration with MySQL
- Clean code architecture and separation of concerns
- Error handling and logging
- Request/response validation with Pydantic
- Environment configuration
- API documentation

## 📝 Future Enhancements

- [ ] User authentication and sessions
- [ ] Multi-language support
- [ ] Voice input integration
- [ ] Machine learning model for better intent detection
- [ ] Admin panel for managing knowledge base
- [ ] Analytics and usage tracking
- [ ] Integration with real banking APIs
- [ ] Sentiment analysis
- [ ] Chat history storage

## 👨‍💻 Development

### Adding New Intents

1. Add keywords to `nlp.py` in `INTENT_KEYWORDS`
2. Create handler in `services/chat_service.py`
3. Add routing logic in `process_chat_message()`

### Adding New Endpoints

1. Create new router in `routes/`
2. Import and include in `main.py`

## 📄 License

This project is created for educational purposes.

## 👥 Author

Student Project - Smart Banking Assistant

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- spaCy for NLP capabilities
- MySQL for reliable data storage

---

**Happy Coding! 🚀**
