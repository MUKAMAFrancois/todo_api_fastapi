todoapp/
│
├── api/                          # API-related code
│   ├── routers/                  # FastAPI routers for endpoints
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints (signup, login, forgot password)
│   │   └── tasks.py             # Task CRUD endpoints
│   ├── dependencies/             # Dependency injection (e.g., auth, database)
│   │   ├── __init__.py
│   │   ├── auth.py              # JWT validation, get current user
│   │   └── database.py          # MongoDB client injection
│   ├── schemas/                  # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py              # User schemas (create, update, response)
│   │   ├── task.py              # Task schemas (create, update, response)
│   │   └── token.py             # Token schemas (JWT, password reset)
│   ├── models/                   # MongoDB document models (if using ODM)
│   │   ├── __init__.py
│   │   ├── user.py              # User document structure
│   │   └── task.py              # Task document structure
│   └── exceptions.py             # Custom HTTP exceptions
│
├── core/                         # Core configuration and utilities
│   ├── __init__.py
│   ├── config.py                # Load .env, app settings (JWT secret, MongoDB URI)
│   ├── security.py              # Password hashing, JWT creation/verification
│   └── email.py                 # Email sending for password reset
│
├── tests/                        # Unit and integration tests
│   ├── __init__.py
│   ├── test_auth.py             # Tests for auth endpoints
│   ├── test_tasks.py            # Tests for task endpoints
│   └── test_utils.py            # Tests for utilities (e.g., security, email)
│
├── .env                          # Environment variables (MongoDB URI, JWT secret)
├── requirements.txt              # Project dependencies
├── main.py                       # FastAPI app entry point
├── README.md                     # Project documentation
└── pytest.ini                    # Pytest configuration