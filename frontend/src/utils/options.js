// Общий хелпер для select-опций формы: список сущностей -> [{value, label}],
// с необязательным первым пунктом-плейсхолдером ("— выберите ... —").
// Используется в BreedsPage/AnimalsPage/WeightingsPage вместо копирования
// одного и того же .map() в каждой странице.
export function toOptions(items, valueKey, labelKey, placeholder) {
  const options = items.map((item) => ({ value: item[valueKey], label: item[labelKey] }));
  return placeholder ? [{ value: '', label: placeholder }, ...options] : options;
}

// Общий хелпер для колонок таблицы/подписей: находит label сущности по id в
// уже загруженном списке (без отдельного запроса на каждую строку).
export function findLabel(items, idKey, id, labelKey) {
  return items.find((item) => item[idKey] === id)?.[labelKey] ?? id;
}
