import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/app/context/AuthContext';

export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setTokenAndUser } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (token) {
      // Store token and fetch user data
      localStorage.setItem('auth_token', token);
      
      // Fetch user data with the token
      fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
        .then(res => res.json())
        .then(userData => {
          localStorage.setItem('user_data', JSON.stringify(userData));
          // Redirect to dashboard
          window.location.href = '/dashboard';
        })
        .catch(error => {
          console.error('Failed to fetch user data:', error);
          navigate('/signin');
        });
    } else {
      // No token, redirect to sign in
      navigate('/signin');
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="size-12 animate-spin text-[#4A9EFF] mx-auto mb-4" />
        <p className="text-[#A0A0A0] text-lg">Completing sign in...</p>
      </div>
    </div>
  );
}
