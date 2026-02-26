/**
 * Authentication API Service
 * Connects to QuantPulse Backend Database
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

/**
 * Register a new user
 */
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

/**
 * Login user and get JWT token
 */
export async function login(data: LoginData): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login/json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Login failed");
  }

  return response.json();
}

/**
 * Get current user profile
 */
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: { 
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
  });

  if (!response.ok) {
    throw new Error("Failed to get user profile");
  }

  return response.json();
}

/**
 * Update user profile
 */
export async function updateProfile(token: string, data: Partial<User>): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: "PUT",
    headers: { 
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update profile");
  }

  return response.json();
}

/**
 * Logout (client-side only - clear token)
 */
export function logout(): void {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("user_data");
}
