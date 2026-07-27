import { Link } from 'react-router-dom';

export default function CheckEmailPage() {
  return (
    <div className="auth-page">
      <h1>Проверьте почту</h1>
      <p>
        Мы отправили ссылку для активации на указанный email. Перейдите по
        ней, чтобы активировать аккаунт, а затем вернитесь и войдите.
      </p>
      <p>
        <Link to="/login">Назад ко входу</Link>
      </p>
    </div>
  );
}
