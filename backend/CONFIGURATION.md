# Project Configuration Documentation

## Environment Variables

### Required Variables

| Variable      | Description           | Default           | Example                    |
| ------------- | --------------------- | ----------------- | -------------------------- |
| `DB_HOST`     | MySQL server hostname | `localhost`       | `localhost` or `127.0.0.1` |
| `DB_USER`     | MySQL username        | `root`            | `root` or `banking_user`   |
| `DB_PASSWORD` | MySQL password        | `""`              | `your_secure_password`     |
| `DB_NAME`     | Database name         | `banking_chatbot` | `banking_chatbot`          |
| `DB_PORT`     | MySQL port            | `3306`            | `3306`                     |

### Optional Variables

| Variable   | Description      | Default   |
| ---------- | ---------------- | --------- |
| `APP_HOST` | Application host | `0.0.0.0` |
| `APP_PORT` | Application port | `8000`    |
| `DEBUG`    | Debug mode       | `True`    |

## Database Configuration

### Connection String Format

```
mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
```

### Example Configurations

#### Local Development

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password123
DB_NAME=banking_chatbot
DB_PORT=3306
```

#### Docker MySQL

```env
DB_HOST=mysql-container
DB_USER=banking_user
DB_PASSWORD=secure_password
DB_NAME=banking_chatbot
DB_PORT=3306
```

#### Remote MySQL

```env
DB_HOST=db.example.com
DB_USER=remote_user
DB_PASSWORD=remote_password
DB_NAME=banking_chatbot
DB_PORT=3306
```

## Application Settings

### Server Configuration

Default server runs on:

- Host: `0.0.0.0` (all interfaces)
- Port: `8000`
- Reload: `True` (development)

To run on different port:

```bash
uvicorn main:app --reload --port 8001
```

To run on specific host:

```bash
uvicorn main:app --reload --host 127.0.0.1
```

### CORS Configuration

Currently allows all origins (`"*"`). For production, update [main.py](main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## NLP Configuration

### spaCy Model

- Model: `en_core_web_sm`
- Language: English
- Size: ~12 MB

To use different model:

```python
# In nlp.py
nlp = spacy.load("en_core_web_md")  # Medium model
# or
nlp = spacy.load("en_core_web_lg")  # Large model
```

### Intent Detection

Modify intents in [nlp.py](nlp.py):

```python
INTENT_KEYWORDS = {
    'YOUR_INTENT': ['keyword1', 'keyword2', 'keyword3'],
    # Add more intents...
}
```

## Database Schema

### Default User ID

The system uses `user_id = 1` by default for demo purposes.

To support multiple users, update endpoints to accept and use `user_id` parameter.

### Sample Data

The `schema.sql` includes sample data:

- 3 users
- 4 accounts
- 7 transactions
- 8 knowledge base entries

## Logging Configuration

### Log Levels

Current: `INFO`

To change, update [main.py](main.py):

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Output

Currently logs to console. To log to file:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Performance Tuning

### Database Connection Pool

For production, consider using connection pooling:

```python
# In db.py
from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(
    pool_name="banking_pool",
    pool_size=5,
    **DB_CONFIG
)
```

### Caching

Consider caching for:

- Knowledge base queries
- Static responses
- User account data

Example with `functools.lru_cache`:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_knowledge(question: str):
    return get_answer_from_knowledge(question)
```

## Security Recommendations

### Production Checklist

- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for database connections
- [ ] Implement rate limiting
- [ ] Add request authentication
- [ ] Sanitize all user inputs
- [ ] Use environment-specific configuration
- [ ] Enable HTTPS
- [ ] Update CORS to specific origins
- [ ] Implement logging and monitoring
- [ ] Use prepared statements (already done)
- [ ] Add input validation (already done with Pydantic)

### Password Security

Never commit `.env` file to version control. It's already in `.gitignore`.

## Deployment

### Production Server

Use production ASGI server:

```bash
# With Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment-Specific Settings

Create separate config files:

- `.env.development`
- `.env.staging`
- `.env.production`

## Monitoring

### Health Check Endpoints

- `/` - Basic health
- `/health` - Detailed health
- `/api/chat/health` - Chat service health

### Metrics to Monitor

- Response time
- Error rate
- Database connection status
- API call frequency
- Intent detection accuracy
- Unknown questions count

## Troubleshooting

### Enable Debug Mode

Set in `.env`:

```env
DEBUG=True
```

### Verbose Logging

```python
logging.basicConfig(level=logging.DEBUG)
```

### Database Debug

```python
# In db.py, add:
logger.debug(f"Executing query: {query}")
logger.debug(f"With params: {params}")
```

---

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
