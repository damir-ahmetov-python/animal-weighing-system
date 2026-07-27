import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function Layout({ children }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <header className="app-header">
        <strong>Система учёта животных</strong>
        <button type="button" onClick={handleLogout}>
          Выйти
        </button>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}
