import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CheckEmailPage from './pages/CheckEmailPage';
import DashboardPage from './pages/DashboardPage';
import AnimalTypesPage from './pages/AnimalTypesPage';
import BreedsPage from './pages/BreedsPage';
import AnimalsPage from './pages/AnimalsPage';
import WeightingsPage from './pages/WeightingsPage';
import AdminUsersPage from './pages/AdminUsersPage';

// Все защищённые страницы оборачиваются в ProtectedRoute + Layout одинаково -
// вместо повторения этой пары 6 раз, один раз описываем здесь.
function withLayout(element) {
  return (
    <ProtectedRoute>
      <Layout>{element}</Layout>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          <Route path="/check-email" element={<CheckEmailPage />} />

          <Route path="/dashboard" element={withLayout(<DashboardPage />)} />
          <Route path="/animal-types" element={withLayout(<AnimalTypesPage />)} />
          <Route path="/breeds" element={withLayout(<BreedsPage />)} />
          <Route path="/animals" element={withLayout(<AnimalsPage />)} />
          <Route path="/weightings" element={withLayout(<WeightingsPage />)} />
          <Route path="/admin/users" element={withLayout(<AdminUsersPage />)} />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
