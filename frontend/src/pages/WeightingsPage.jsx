import { useCallback, useEffect, useState } from 'react';
import { animalsApi, weightingsApi } from '../api/client';
import { useAuth } from '../context/useAuth';
import FormField from '../components/FormField';
import DataTable from '../components/DataTable';

const emptyForm = { animal_id: '', date: '', weight_kg: '' };

export default function WeightingsPage() {
  const { token } = useAuth();
  const [weightings, setWeightings] = useState([]);
  const [animals, setAnimals] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // GET /weightings уже возвращает только свои записи для обычного юзера и все
  // для админа - фронт просто рендерит ответ, отдельную фильтрацию по роли не делаем.
  const loadData = useCallback(() => {
    Promise.all([weightingsApi.list(token), animalsApi.list(token)])
      .then(([weightingsData, animalsData]) => {
        setWeightings(weightingsData);
        setAnimals(animalsData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const animalLabel = (animalId) =>
    animals.find((animal) => animal.animal_id === animalId)?.inventory_number ??
    animalId;

  const resetForm = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    const payload = {
      animal_id: Number(form.animal_id),
      date: form.date,
      weight_kg: Number(form.weight_kg),
    };

    try {
      if (editingId) {
        await weightingsApi.update(token, editingId, payload);
      } else {
        await weightingsApi.create(token, payload);
      }
      resetForm();
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (weighting) => {
    setEditingId(weighting.weighting_id);
    setForm({
      animal_id: String(weighting.animal_id),
      date: weighting.date,
      weight_kg: String(weighting.weight_kg),
    });
  };

  const handleDelete = async (weighting) => {
    setError('');
    try {
      await weightingsApi.remove(token, weighting.weighting_id);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Загрузка...</p>;

  const animalOptions = [
    { value: '', label: '— выберите животное —' },
    ...animals.map((animal) => ({
      value: animal.animal_id,
      label: animal.inventory_number,
    })),
  ];

  return (
    <div>
      <h1>Взвешивания</h1>

      <form onSubmit={handleSubmit} className="entity-form">
        <FormField
          id="animal_id"
          label="Животное"
          options={animalOptions}
          value={form.animal_id}
          onChange={(event) => setForm({ ...form, animal_id: event.target.value })}
          required
        />

        <FormField
          id="date"
          label="Дата"
          type="date"
          value={form.date}
          onChange={(event) => setForm({ ...form, date: event.target.value })}
          required
        />

        <FormField
          id="weight_kg"
          label="Вес (кг)"
          type="number"
          step="0.1"
          min="0.1"
          value={form.weight_kg}
          onChange={(event) => setForm({ ...form, weight_kg: event.target.value })}
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
          { key: 'weighting_id', label: 'ID' },
          {
            key: 'animal_id',
            label: 'Животное',
            render: (row) => animalLabel(row.animal_id),
          },
          { key: 'date', label: 'Дата' },
          { key: 'weight_kg', label: 'Вес (кг)' },
          { key: 'created_by_user_id', label: 'Внёс (ID юзера)' },
        ]}
        rows={weightings}
        rowKey="weighting_id"
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
