import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '@/app/components/Layout';
import { HomePage } from '@/app/pages/HomePage';
import { DashboardPage } from '@/app/pages/DashboardPage';
import { ContactPage } from '@/app/pages/ContactPage';
import { SignInPage } from '@/app/pages/SignInPage';
import { SignUpPage } from '@/app/pages/SignUpPage';
import { AuthCallbackPage } from '@/app/pages/AuthCallbackPage';
import { RiskMapPage } from '@/app/pages/RiskMapPage';
import { PortfolioPage } from '@/app/pages/PortfolioPage';
import { FintechBackground } from '@/app/components/FintechBackground';
import { AuthProvider } from '@/app/context/AuthContext';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';

export default function App() {
  return (
    <AuthProvider>
      <div className="relative min-h-screen text-zinc-100 font-sans antialiased selection:bg-blue-500/30">
        <FintechBackground />
        <div className="relative z-10">
          <BrowserRouter>
            <Routes>
              {/* Home page without navbar */}
              <Route path="/" element={<HomePage />} />

              {/* Routes with Layout (includes navigation) */}
              <Route element={<Layout />}>
                <Route path="dashboard" element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                } />
                <Route path="portfolio" element={
                  <ProtectedRoute>
                    <PortfolioPage />
                  </ProtectedRoute>
                } />
                <Route path="risk-map" element={
                  <ProtectedRoute>
                    <RiskMapPage />
                  </ProtectedRoute>
                } />
                <Route path="contact" element={<ContactPage />} />
              </Route>

              {/* Auth routes without main layout */}
              <Route path="/signin" element={<SignInPage />} />
              <Route path="/signup" element={<SignUpPage />} />
              <Route path="/auth/callback" element={<AuthCallbackPage />} />
            </Routes>
          </BrowserRouter>
        </div>
      </div>
    </AuthProvider>
  );
}
