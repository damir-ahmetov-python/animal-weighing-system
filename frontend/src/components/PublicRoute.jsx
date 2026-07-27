import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

// Обратный ProtectedRoute: уже залогиненного не пускает обратно на /login и /register.
export default function PublicRoute({ children }) {
  const { token } = useAuth();
  return token ? <Navigate to="/dashboard" replace /> : children;
}
