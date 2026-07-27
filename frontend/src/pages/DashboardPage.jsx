import { useEffect, useState } from 'react';
import { getMe } from '../api/client';
import { useAuth } from '../context/useAuth';

export default function DashboardPage() {
  const { token } = useAuth();
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    getMe(token)
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  if (loading) return <p>Загрузка...</p>;
  if (error) return <p className="form-error">{error}</p>;

  return (
    <div>
      <h1>Личный кабинет</h1>
      <p>Логин: {user.login}</p>
      <p>Email: {user.email}</p>
      <p>Роль: {user.role}</p>
      <p>Активен: {user.is_active ? 'да' : 'нет'}</p>

      {/* Таблицы animal type / breed / animal / weighting - День 6 */}
    </div>
  );
}
