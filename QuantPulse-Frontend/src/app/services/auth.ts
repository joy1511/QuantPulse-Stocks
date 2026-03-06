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
 * Register a new user (DUMMY MODE - accepts any credentials)
 */
export async function register(data: RegisterData): Promise<User> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Return dummy user data
  return {
    id: 1,
    email: data.email,
    full_name: data.full_name || "Demo User",
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
    last_login: null
  };
}

/**
 * Login user and get JWT token (DUMMY MODE - accepts any credentials)
 */
export async function login(data: LoginData): Promise<LoginResponse> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Return dummy token
  return {
    access_token: "dummy_token_" + Date.now(),
    token_type: "bearer"
  };
}

/**
 * Get current user profile (DUMMY MODE)
 */
export async function getCurrentUser(token: string): Promise<User> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Return dummy user data
  return {
    id: 1,
    email: "demo@user.com",
    full_name: "Demo User",
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
    last_login: new Date().toISOString()
  };
}

/**
 * Update user profile (DUMMY MODE)
 */
export async function updateProfile(token: string, data: Partial<User>): Promise<User> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Return dummy updated user data
  return {
    id: 1,
    email: data.email || "demo@user.com",
    full_name: data.full_name || "Demo User",
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
    last_login: new Date().toISOString()
  };
}

/**
 * Logout (client-side only - clear token)
 */
export function logout(): void {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("user_data");
}
