import { useAuth } from '../context/useAuth';

// Данные пользователя уже подтянуты в AuthProvider сразу после логина -
// здесь их просто читаем из контекста, повторный запрос не нужен.
export default function DashboardPage() {
  const { user } = useAuth();

  if (!user) return <p>Загрузка...</p>;

  return (
    <div>
      <h1>Личный кабинет</h1>
      <p>Логин: {user.login}</p>
      <p>Email: {user.email}</p>
      <p>Роль: {user.role}</p>
      <p>Активен: {user.is_active ? 'да' : 'нет'}</p>
    </div>
  );
}
