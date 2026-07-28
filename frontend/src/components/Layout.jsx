import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
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

      <nav className="app-nav">
        <NavLink to="/dashboard">Личный кабинет</NavLink>
        <NavLink to="/animal-types">Типы животных</NavLink>
        <NavLink to="/breeds">Породы</NavLink>
        <NavLink to="/animals">Животные</NavLink>
        <NavLink to="/weightings">Взвешивания</NavLink>
        {/* Пункт меню скрыт для не-admin - реальная защита всё равно на backend (403) */}
        {user?.role === 'admin' && <NavLink to="/admin/users">Пользователи</NavLink>}
      </nav>

      <main className="app-main">{children}</main>
    </div>
  );
}
