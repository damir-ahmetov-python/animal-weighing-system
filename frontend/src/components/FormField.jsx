// Общая пара label+input (или label+select, если передали options) для всех форм
// проекта. Всё, что не id/label/type/options, просто прокидывается в поле как есть
// (value, onChange, required, minLength...).
export default function FormField({ id, label, type = 'text', options, ...fieldProps }) {
  return (
    <div className="form-row">
      <label htmlFor={id}>{label}</label>
      {options ? (
        <select id={id} {...fieldProps}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input id={id} type={type} {...fieldProps} />
      )}
    </div>
  );
}
