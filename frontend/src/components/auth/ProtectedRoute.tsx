import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { LoadingState } from "@/components/shared/LoadingState";

interface ProtectedRouteProps {
    children: React.ReactNode;
    requiredRole?: "admin" | "analyst" | "viewer";
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
    const { isAuthenticated, isLoading, user } = useAuth();
    const location = useLocation();

    if (isLoading) {
        return <LoadingState message="Checking authentication..." />;
    }

    if (!isAuthenticated) {
        // Redirect to login, preserving the intended destination
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    // Check role if required
    if (requiredRole && user) {
        const roleHierarchy = { admin: 3, analyst: 2, viewer: 1 };
        const userLevel = roleHierarchy[user.role] || 0;
        const requiredLevel = roleHierarchy[requiredRole] || 0;

        if (userLevel < requiredLevel) {
            return <Navigate to="/unauthorized" replace />;
        }
    }

    return <>{children}</>;
}
