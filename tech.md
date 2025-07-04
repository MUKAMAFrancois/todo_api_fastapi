## 1. TechStack
1. **FastAPI**: For building the REST API with async endpoints, Pydantic for data validation, and dependency injection for authentication.
2. **MongoDB**: For storing users and tasks, using pymongo or motor (async driver).
**Authentication**: JWT (JSON Web Tokens) for secure user sessions, passlib for password hashing, and python-jose for JWT handling.
3. **Email**: Integration with an email service (e.g., SMTP via emails) for forgot password functionality.
4. **Environment**: Managed with .env for sensitive data (MongoDB URI, JWT secret, email credentials).

## 2. Features
1. **User management:** Signup, login, password reset, and user profile.
2. **Task management:** Create, read, update, delete tasks, with filtering by completion status.
3. **Security:** Role-based access (only users can access their own tasks), input validation, and secure password storage.
4. **Optional:** Task categories or due dates for extensibility.

## 3. Components and Their Elements

### 3.1. User (`users`)
- [_id, email, hashedpassword, username, joined_at, is_active, reset_token(str, temporary token for password reset, with expory toime.)]

### 3.2. Task (`tasks`)
- [_id, title, description (optional), is_completed, created_at, updated_at, user_id (links to 'users'), due_date, category (optional)]
  
### 3.3. Authentication token (not stored in MongoDB)

This represents a JWT for user sessions, generated during login. It is stored in brower's localStorage or cookies.
- `sub` (string): subject, typically the user's `id` or `email`.
- `exp` (datetime): expiry time of the token (e.g. 1 hr from issuance).
- `iat` (datetime): issued-at timestamp.

### 3.4. Password Reset Request (`password_resets`)

[id, user_id, token, expires_at, used (boolean, default = False)]
