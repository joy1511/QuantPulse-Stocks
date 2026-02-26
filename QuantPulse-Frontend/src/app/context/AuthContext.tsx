import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import * as authService from '../services/auth';

interface User {
    id: number;
    email: string;
    full_name: string;
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
    error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Check for existing token on mount
        const storedToken = localStorage.getItem('auth_token');
        const storedUser = localStorage.getItem('user_data');
        
        if (storedToken && storedUser) {
            try {
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
                
                // Verify token is still valid by fetching current user
                authService.getCurrentUser(storedToken)
                    .then(userData => {
                        setUser(userData);
                        localStorage.setItem('user_data', JSON.stringify(userData));
                    })
                    .catch(() => {
                        // Token invalid, clear everything
                        localStorage.removeItem('auth_token');
                        localStorage.removeItem('user_data');
                        setToken(null);
                        setUser(null);
                    });
            } catch (e) {
                console.error('Failed to restore session', e);
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_data');
            }
        }
        setIsLoading(false);
    }, []);

    const login = async (email: string, password: string) => {
        try {
            setError(null);
            setIsLoading(true);
            
            // Login and get token
            const loginResponse = await authService.login({ email, password });
            const authToken = loginResponse.access_token;
            
            // Get user data
            const userData = await authService.getCurrentUser(authToken);
            
            // Store in state and localStorage
            setToken(authToken);
            setUser(userData);
            localStorage.setItem('auth_token', authToken);
            localStorage.setItem('user_data', JSON.stringify(userData));
            
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Login failed';
            setError(errorMessage);
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (email: string, password: string, fullName?: string) => {
        try {
            setError(null);
            setIsLoading(true);
            
            // Register user
            await authService.register({ email, password, full_name: fullName });
            
            // Auto-login after registration
            await login(email, password);
            
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Registration failed';
            setError(errorMessage);
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        setError(null);
        authService.logout();
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, isLoading, error }}>
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
