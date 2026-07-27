// Общая пара label+input для форм логина/регистрации - чтобы не дублировать
// одну и ту же разметку в каждой странице. Всё, что не label/id/type, просто
// прокидывается в <input> как есть (value, onChange, required, minLength...).
export default function FormField({ id, label, type = 'text', ...inputProps }) {
  return (
    <div className="form-row">
      <label htmlFor={id}>{label}</label>
      <input id={id} type={type} {...inputProps} />
    </div>
  );
}
