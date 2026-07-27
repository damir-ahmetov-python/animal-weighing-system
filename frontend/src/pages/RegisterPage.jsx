import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../api/client';
import FormField from '../components/FormField';

export default function RegisterPage() {
  const [login, setLogin] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      await registerUser({ login, email, password });
      navigate('/check-email');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <h1>Регистрация</h1>

      <form onSubmit={handleSubmit}>
        <FormField
          id="login"
          label="Логин"
          value={login}
          onChange={(event) => setLogin(event.target.value)}
          required
        />

        <FormField
          id="email"
          label="Email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <FormField
          id="password"
          label="Пароль"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          minLength={8}
          maxLength={72}
          required
        />

        {error && <p className="form-error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Отправка...' : 'Зарегистрироваться'}
        </button>
      </form>

      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
}
