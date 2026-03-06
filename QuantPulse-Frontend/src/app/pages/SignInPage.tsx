import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { BarChart3, Mail, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { Input } from '@/app/components/ui/input';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Card } from '@/app/components/ui/card';
import { useAuth } from '@/app/context/AuthContext';

export function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [user, navigate, location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setIsSubmitting(true);

    try {
      // Real database login
      await login(email, password);
      setIsSuccess(true);
      
      // Redirect after success
      setTimeout(() => {
        const from = (location.state as any)?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      }, 1000);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Login failed. Please check your credentials.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <Link to="/" className="flex items-center justify-center gap-3 mb-8">
          <div className="p-2 rounded-lg bg-[#3A6FF8] shadow-sm shadow-blue-500/20">
            <BarChart3 className="size-6 text-white" />
          </div>
          <span className="text-2xl text-zinc-100">QuantPulse India</span>
        </Link>

        <Card variant="elevated" className="p-9 shadow-2xl shadow-blue-900/10 border-[#3A6FF8]/20">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-zinc-100 mb-2 tracking-tight">Welcome Back</h1>
            <p className="text-zinc-400">Sign in to access your dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-zinc-300 font-medium">Email Address</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-zinc-500" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 h-11"
                  required
                  disabled={isSubmitting || isSuccess}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-zinc-300 font-medium">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-zinc-500" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 h-11"
                  required
                  disabled={isSubmitting || isSuccess}
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  className="size-4 rounded border-[rgba(100,150,255,0.2)] bg-[rgba(15,23,42,0.6)] text-[#3A6FF8]"
                />
                <span className="text-sm text-zinc-400 group-hover:text-zinc-300 transition-colors">Remember me</span>
              </label>
              <Link to="#" className="text-sm text-[#5B8DFF] hover:text-[#7AA3FF] font-medium">
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              variant={isSuccess ? "outline" : "prominent"} // Use a different variant or style for success if available, else just prominent
              className={`w-full h-11 text-base mt-2 ${isSuccess ? "bg-green-500/10 text-green-400 border-green-500/50 hover:bg-green-500/20" : ""}`}
              disabled={isSubmitting || isSuccess}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Signing In...
                </>
              ) : isSuccess ? (
                <>
                  Success! Redirecting...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="size-4 ml-2" />
                </>
              )}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[rgba(100,150,255,0.1)]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-[rgba(15,23,42,0.9)] text-zinc-400">Or continue with</span>
            </div>
          </div>

          {/* Google Sign In Button */}
          <Button
            type="button"
            variant="outline"
            className="w-full h-11 text-base border-[rgba(100,150,255,0.2)] hover:bg-[rgba(58,111,248,0.1)] hover:border-[rgba(100,150,255,0.3)]"
            onClick={() => {
              alert('Google Sign-In requires OAuth setup.\n\nTo enable:\n1. Go to Google Cloud Console\n2. Create OAuth credentials\n3. Add credentials to .env file\n\nFor now, please use email/password login.');
            }}
            disabled={isSubmitting || isSuccess}
          >
            <svg className="size-5 mr-2" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google (Setup Required)
          </Button>

          <div className="mt-8 pt-6 border-t border-[rgba(100,150,255,0.1)] text-center">
            <p className="text-sm text-zinc-400">
              Don't have an account?{' '}
              <Link to="/signup" className="text-[#5B8DFF] hover:text-[#7AA3FF] font-medium">
                Sign up
              </Link>
            </p>
          </div>

          <div className="mt-4 p-3 bg-green-500/10 rounded-lg border border-green-500/20">
            <p className="text-xs text-center text-green-200">
              <strong>Demo Mode:</strong> Enter any email and password to sign in instantly!
            </p>
          </div>
        </Card>

        <p className="text-center text-xs text-zinc-500 mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
