import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { BarChart3, Home, TrendingUp, Briefcase, Users, Mail, LogOut, User } from 'lucide-react';
import { useAuth } from '@/app/context/AuthContext';

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/dashboard', icon: TrendingUp, label: 'Dashboard' },
    { path: '/portfolio', icon: Briefcase, label: 'Portfolio' },
    { path: '/risk-map', icon: Users, label: 'Risk Map' },
    { path: '/contact', icon: Mail, label: 'Contact' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen text-[#F0F0F0]">
      {/* Navigation Bar */}
      <nav className="border-b border-[rgba(74, 158, 255, 0.15)] bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#1A6FD4] shadow-sm shadow-blue-500/20">
                <BarChart3 className="size-6 text-white" />
              </div>
              <span className="text-xl text-[#F0F0F0]">QuantPulse India</span>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${isActive
                      ? 'bg-[#1A6FD4] text-white shadow-sm shadow-blue-500/20'
                      : 'text-[#A0A0A0] hover:text-[#F0F0F0] hover:bg-[rgba(74,158,255,0.1)]'
                      }`}
                  >
                    <Icon className="size-4" />
                    <span className="hidden md:inline">{item.label}</span>
                  </Link>
                );
              })}
            </div>

            {/* Authentication Section */}
            <div className="flex items-center gap-3.5 pl-2">
              {user ? (
                // Logged in - show user info and logout
                <>
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-[rgba(74,158,255,0.1)] rounded-lg border border-[rgba(74, 158, 255, 0.12)]">
                    <User className="size-4 text-[#4A9EFF]" />
                    <span className="text-sm text-[#F0F0F0] font-medium">
                      {user.full_name || user.email}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 text-[#A0A0A0] hover:text-[#F0F0F0] hover:bg-[rgba(239,68,68,0.1)] rounded-lg transition-all font-medium"
                  >
                    <LogOut className="size-4" />
                    <span className="hidden md:inline">Logout</span>
                  </button>
                </>
              ) : (
                // Not logged in - show sign in/up buttons
                <>
                  <Link
                    to="/signin"
                    className="px-4 py-2 text-[#A0A0A0] hover:text-[#F0F0F0] transition-colors font-medium"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/signup"
                    className="px-5 py-2 bg-[#1A6FD4] hover:bg-[#2A7FE8] text-white rounded-lg transition-all shadow-sm shadow-blue-500/20 hover:shadow-blue-500/30 font-medium"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}
