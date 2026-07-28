import { useEffect, useState } from 'react';
import { setUnauthorizedHandler, getMe } from '../api/client';
import { AuthContext } from './authContext';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = (newToken) => setToken(newToken);
  const logout = () => {
    setToken(null);
    setUser(null);
  };

  // При 401 от любого запроса client.js вызовет logout - токен обнулится,
  // и ProtectedRoute сам перекинет на /login.
  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, []);

  // Как только появился токен - сразу подтягиваем данные юзера (включая роль),
  // чтобы Layout и страницы знали её без отдельного запроса в каждом месте.
  // user и так null по умолчанию и при логауте (см. logout выше), отдельно
  // обнулять его тут при отсутствии токена не нужно.
  useEffect(() => {
    if (!token) return;

    getMe(token)
      .then(setUser)
      .catch(() => {
        // 401 здесь же дёрнет unauthorizedHandler и разлогинит - отдельно ловить не нужно
      });
  }, [token]);

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
