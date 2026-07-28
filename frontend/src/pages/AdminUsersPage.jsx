import { useCallback, useEffect, useState } from 'react';
import { getUsers, toggleUserActive } from '../api/client';
import { useAuth } from '../context/useAuth';
import DataTable from '../components/DataTable';

export default function AdminUsersPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Backend сам возвращает 403, если сюда попадёт не-admin - отдельную проверку
  // роли на фронте не дублируем, просто показываем ошибку, если она придёт.
  const loadUsers = useCallback(() => {
    getUsers(token)
      .then(setUsers)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleToggle = async (user) => {
    setError('');
    try {
      await toggleUserActive(token, user.id);
      loadUsers();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (error) return <p className="form-error">{error}</p>;

  return (
    <div>
      <h1>Пользователи</h1>

      <DataTable
        columns={[
          { key: 'id', label: 'ID' },
          { key: 'login', label: 'Логин' },
          { key: 'email', label: 'Email' },
          { key: 'role', label: 'Роль' },
          {
            key: 'is_active',
            label: 'Активен',
            render: (row) => (row.is_active ? 'да' : 'нет'),
          },
          {
            key: 'toggle',
            label: 'Действия',
            render: (row) => (
              <button type="button" onClick={() => handleToggle(row)}>
                {row.is_active ? 'Отключить' : 'Включить'}
              </button>
            ),
          },
        ]}
        rows={users}
        rowKey="id"
      />
    </div>
  );
}
