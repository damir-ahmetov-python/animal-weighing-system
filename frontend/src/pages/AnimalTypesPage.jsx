import { useCallback, useEffect, useState } from 'react';
import { animalTypesApi } from '../api/client';
import { useAuth } from '../context/useAuth';
import FormField from '../components/FormField';
import DataTable from '../components/DataTable';

export default function AnimalTypesPage() {
  const { token } = useAuth();
  const [types, setTypes] = useState([]);
  const [nameType, setNameType] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // loading стартует как true и гаснет один раз после первой загрузки - при
  // повторных loadTypes() (после create/update/delete) страница уже не мигает
  // "Загрузка...", список просто обновляется на месте.
  const loadTypes = useCallback(() => {
    animalTypesApi
      .list(token)
      .then(setTypes)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    loadTypes();
  }, [loadTypes]);

  const resetForm = () => {
    setEditingId(null);
    setNameType('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    try {
      if (editingId) {
        await animalTypesApi.update(token, editingId, { name_type: nameType });
      } else {
        await animalTypesApi.create(token, { name_type: nameType });
      }
      resetForm();
      loadTypes();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (type) => {
    setEditingId(type.type_id);
    setNameType(type.name_type);
  };

  const handleDelete = async (type) => {
    setError('');
    try {
      await animalTypesApi.remove(token, type.type_id);
      loadTypes();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Загрузка...</p>;

  return (
    <div>
      <h1>Типы животных</h1>

      <form onSubmit={handleSubmit} className="entity-form">
        <FormField
          id="name_type"
          label="Название"
          value={nameType}
          onChange={(event) => setNameType(event.target.value)}
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
          { key: 'type_id', label: 'ID' },
          { key: 'name_type', label: 'Название' },
        ]}
        rows={types}
        rowKey="type_id"
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
