# JWT Authentication System

This document describes the JWT-based authentication system implemented for the Legal-RAG application.

## Features

- User registration with email and password
- User login with JWT token generation
- Password hashing using bcrypt
- Protected API endpoints
- User profile retrieval

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user information

### Protected Endpoints

- `POST /api/upload` - Upload documents (requires authentication)
- `POST /api/query` - Query documents (requires authentication)

## Usage

### 1. Register a new user

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use protected endpoints

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@document.pdf"
```

## Configuration

Set the following environment variables:

- `SECRET_KEY`: JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes by default
- All API endpoints (except auth) require authentication
- User documents are isolated by user email

## Database Schema

The system adds a `users` table with the following fields:
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `is_active`: User status flag
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
