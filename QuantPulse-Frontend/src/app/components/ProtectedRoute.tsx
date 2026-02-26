import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/app/context/AuthContext';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { user, isLoading } = useAuth();
    const location = useLocation();

    if (isLoading) {
        return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
    }

    if (!user) {
        // Redirect to signin content, saving the current location they were trying to go to
        return <Navigate to="/signin" state={{ from: location }} replace />;
    }

    return <>{children}</>;
}
