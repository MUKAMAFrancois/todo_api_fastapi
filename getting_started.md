1. Creating virtual environment
    - `python3 -m venv .env`

2. Activate
    - `.venv\Scripts\activate`
  
3. Dependencies
        # Core FastAPI dependencies
        fastapi
        uvicorn

        # Async MongoDB driver
        motor

        # Authentication
        python-jose
        passlib[bcrypt]
        python-multipart

        # Environment variables
        python-dotenv

        # Email sending for password reset
        emails
        jinja2

        # Testing
        pytest
        pytest-asyncio
        httpx
        mongomock-motor

        # Optional: Rate limiting (for security)
        fastapi-limiter
4. Saving dependencies
   - `pip freeze > requirements.txt`
5. Incase you want to install all:
   - `pip install -r requirements.txt`