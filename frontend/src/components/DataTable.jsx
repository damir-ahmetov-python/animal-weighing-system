// Общая таблица для всех 4 сущностей (animal type, breed, animal, weighting).
// Страница передаёт: какие колонки показывать (columns), сами строки (rows),
// по какому полю строить key (rowKey), и что делать по кнопкам "Изменить"/"Удалить".
// Если onEdit/onDelete не передали - соответствующей кнопки просто не будет.
export default function DataTable({ columns, rows, rowKey, onEdit, onDelete }) {
  if (rows.length === 0) {
    return <p>Записей пока нет.</p>;
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column.key}>{column.label}</th>
          ))}
          {(onEdit || onDelete) && <th>Действия</th>}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row[rowKey]}>
            {columns.map((column) => (
              <td key={column.key}>
                {column.render ? column.render(row) : row[column.key]}
              </td>
            ))}
            {(onEdit || onDelete) && (
              <td className="table-actions">
                {onEdit && (
                  <button type="button" onClick={() => onEdit(row)}>
                    Изменить
                  </button>
                )}
                {onDelete && (
                  <button
                    type="button"
                    className="danger"
                    onClick={() => onDelete(row)}
                  >
                    Удалить
                  </button>
                )}
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
