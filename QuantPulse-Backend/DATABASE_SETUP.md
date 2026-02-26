# Database Integration Guide 🗄️

## Overview

QuantPulse India now includes a complete user authentication system with database integration. This guide explains how to set up and use the database features.

## Features

✅ **User Registration & Authentication**
✅ **JWT Token-Based Security**
✅ **Password Hashing with Bcrypt**
✅ **PostgreSQL for Production**
✅ **SQLite for Local Development**
✅ **Automatic Database Migrations**
✅ **User Profile Management**

---

## Quick Start

### 1. Install Dependencies

```bash
cd QuantPulse-Backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your SECRET_KEY
# Generate a secure key using:
openssl rand -hex 32
```

### 3. Run the Application

```bash
# The database will be created automatically on first run
python run.py
```

For local development, a SQLite database (`quantpulse.db`) will be created automatically.

---

## Database Configuration

### Local Development (SQLite)

No configuration needed! SQLite database is created automatically in the project root.

```
QuantPulse-Backend/
├── quantpulse.db  ← SQLite database (auto-created)
├── app/
└── ...
```

### Production (PostgreSQL)

Set the `DATABASE_URL` environment variable:

```bash
# Railway/Render automatically provides this
DATABASE_URL=postgresql://user:password@host:port/database
```

**Note**: The system automatically converts `postgres://` to `postgresql://` for SQLAlchemy compatibility.

---

## API Endpoints

### Authentication Endpoints

#### 1. Register New User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00",
  "last_login": null
}
```

#### 2. Login (Get Access Token)

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123
```

**Or use JSON:**
```http
POST /api/auth/login/json
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00",
    "last_login": "2024-01-15T11:00:00"
  }
}
```

#### 3. Get Current User Info

```http
GET /api/auth/me
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-15T11:00:00"
}
```

#### 4. Update Profile

```http
PUT /api/auth/me
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "email": "newmail@example.com"
}
```

#### 5. Change Password

```http
POST /api/auth/change-password
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "current_password": "SecurePass123",
  "new_password": "NewSecurePass456"
}
```

#### 6. Delete Account

```http
DELETE /api/auth/me
Authorization: Bearer <your_access_token>
```

---

## Frontend Integration

### Update AuthContext to Use Real API

Replace the current localStorage-based auth with API calls:

```typescript
// QuantPulse-Frontend/src/app/services/auth.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Register new user
export async function register(data: RegisterData): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Registration failed");
  }

  return response.json();
}

// Login user
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login/json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Login failed");
  }

  return response.json();
}

// Get current user
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: { "Authorization": `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to get user info");
  }

  return response.json();
}

// Update profile
export async function updateProfile(
  token: string,
  data: Partial<User>
): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Update failed");
  }

  return response.json();
}
```

### Update AuthContext

```typescript
// QuantPulse-Frontend/src/app/context/AuthContext.tsx

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import * as authAPI from '@/app/services/auth';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check localStorage for token on mount
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      // Verify token and get user info
      authAPI.getCurrentUser(storedToken)
        .then(userData => {
          setUser(userData);
          setToken(storedToken);
        })
        .catch(() => {
          // Token invalid, clear it
          localStorage.removeItem('access_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authAPI.login({ email, password });
    setUser(response.user);
    setToken(response.access_token);
    localStorage.setItem('access_token', response.access_token);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const userData = await authAPI.register({
      email,
      password,
      full_name: fullName,
    });
    // After registration, automatically login
    await login(email, password);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

---

## Password Requirements

Passwords must meet the following criteria:
- ✅ Minimum 8 characters
- ✅ At least one digit (0-9)
- ✅ At least one uppercase letter (A-Z)
- ✅ Maximum 100 characters

---

## Security Features

### 1. Password Hashing
- Uses **bcrypt** algorithm
- Automatic salt generation
- Secure password verification

### 2. JWT Tokens
- **Algorithm**: HS256
- **Expiration**: 7 days
- **Payload**: User email and ID

### 3. Protected Routes
Use the `get_current_user` dependency to protect routes:

```python
from fastapi import Depends
from app.services.auth_service import get_current_user
from app.models.user import User

@app.get("/protected-route")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}
```

---

## Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| email | String(255) | Unique email address |
| hashed_password | String(255) | Bcrypt hashed password |
| full_name | String(255) | User's full name (optional) |
| is_active | Boolean | Account active status |
| is_verified | Boolean | Email verification status |
| is_admin | Boolean | Admin privileges |
| preferences | Text | JSON string for user preferences |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |
| last_login | DateTime | Last login timestamp |

---

## Testing the API

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'

# Get user info (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### Using Swagger UI

Visit `http://localhost:8000/docs` for interactive API documentation.

---

## Troubleshooting

### Database Connection Issues

**Problem**: `sqlalchemy.exc.OperationalError`

**Solution**: 
- Check DATABASE_URL format
- Ensure PostgreSQL is running
- Verify credentials

### Token Errors

**Problem**: `Could not validate credentials`

**Solution**:
- Check if token is expired (7 days)
- Verify SECRET_KEY is set correctly
- Ensure Authorization header format: `Bearer <token>`

### Password Validation Errors

**Problem**: `Password must contain at least one digit`

**Solution**: Ensure password meets all requirements (8+ chars, 1 digit, 1 uppercase)

---

## Production Deployment

### Railway

1. Add PostgreSQL database addon
2. Set environment variables in Railway dashboard
3. DATABASE_URL is automatically provided
4. Deploy your application

### Render

1. Create PostgreSQL database
2. Copy DATABASE_URL from database dashboard
3. Set environment variables in web service
4. Deploy your application

---

## Next Steps

- [ ] Add email verification
- [ ] Implement password reset
- [ ] Add OAuth2 providers (Google, GitHub)
- [ ] Implement rate limiting
- [ ] Add user roles and permissions
- [ ] Create admin dashboard

---

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review error messages in logs
3. Ensure all environment variables are set correctly

**Happy coding! 🚀**
