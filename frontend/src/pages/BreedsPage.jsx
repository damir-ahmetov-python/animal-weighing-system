import { useCallback, useEffect, useState } from 'react';
import { animalTypesApi, breedsApi } from '../api/client';
import { useAuth } from '../context/useAuth';
import FormField from '../components/FormField';
import DataTable from '../components/DataTable';

const emptyForm = { name: '', type_id: '' };

export default function BreedsPage() {
  const { token } = useAuth();
  const [breeds, setBreeds] = useState([]);
  const [types, setTypes] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(() => {
    Promise.all([breedsApi.list(token), animalTypesApi.list(token)])
      .then(([breedsData, typesData]) => {
        setBreeds(breedsData);
        setTypes(typesData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Название типа для колонки "Тип" - тянем из уже загруженного списка типов,
  // а не отдельным запросом на каждую строку.
  const typeName = (typeId) =>
    types.find((type) => type.type_id === typeId)?.name_type ?? typeId;

  const resetForm = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    const payload = { name: form.name, type_id: Number(form.type_id) };

    try {
      if (editingId) {
        await breedsApi.update(token, editingId, payload);
      } else {
        await breedsApi.create(token, payload);
      }
      resetForm();
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (breed) => {
    setEditingId(breed.breed_id);
    setForm({ name: breed.name, type_id: String(breed.type_id) });
  };

  const handleDelete = async (breed) => {
    setError('');
    try {
      await breedsApi.remove(token, breed.breed_id);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Загрузка...</p>;

  const typeOptions = [
    { value: '', label: '— выберите тип —' },
    ...types.map((type) => ({ value: type.type_id, label: type.name_type })),
  ];

  return (
    <div>
      <h1>Породы</h1>

      <form onSubmit={handleSubmit} className="entity-form">
        <FormField
          id="name"
          label="Название"
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
          required
        />

        <FormField
          id="type_id"
          label="Тип животного"
          options={typeOptions}
          value={form.type_id}
          onChange={(event) => setForm({ ...form, type_id: event.target.value })}
          required
        />

        {error && <p className="form-error">{error}</p>}

        <div className="form-actions">
          <button type="submit">{editingId ? 'Сохранить' : 'Добавить'}</button>
          {editingId && (
            <button type="button" onClick={resetForm}>
              Отмена
            </button>
          )}
        </div>
      </form>

      <DataTable
        columns={[
          { key: 'breed_id', label: 'ID' },
          { key: 'name', label: 'Название' },
          { key: 'type_id', label: 'Тип', render: (row) => typeName(row.type_id) },
        ]}
        rows={breeds}
        rowKey="breed_id"
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
