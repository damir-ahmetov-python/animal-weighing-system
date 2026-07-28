import { useCallback, useEffect, useState } from 'react';
import { animalsApi, breedsApi } from '../api/client';
import { useAuth } from '../context/useAuth';
import FormField from '../components/FormField';
import DataTable from '../components/DataTable';

const emptyForm = {
  inventory_number: '',
  gender: 'male',
  name: '',
  arrival_date: '',
  arrival_age_months: '',
  breed_id: '',
  parent_id: '',
};

export default function AnimalsPage() {
  const { token } = useAuth();
  const [animals, setAnimals] = useState([]);
  const [breeds, setBreeds] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(() => {
    Promise.all([animalsApi.list(token), breedsApi.list(token)])
      .then(([animalsData, breedsData]) => {
        setAnimals(animalsData);
        setBreeds(breedsData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const breedName = (breedId) =>
    breeds.find((breed) => breed.breed_id === breedId)?.name ?? breedId;

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
      inventory_number: form.inventory_number,
      gender: form.gender,
      name: form.name || null,
      arrival_date: form.arrival_date,
      arrival_age_months:
        form.arrival_age_months === '' ? null : Number(form.arrival_age_months),
      breed_id: Number(form.breed_id),
      parent_id: form.parent_id === '' ? null : Number(form.parent_id),
    };

    try {
      if (editingId) {
        await animalsApi.update(token, editingId, payload);
      } else {
        await animalsApi.create(token, payload);
      }
      resetForm();
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (animal) => {
    setEditingId(animal.animal_id);
    setForm({
      inventory_number: animal.inventory_number,
      gender: animal.gender,
      name: animal.name ?? '',
      arrival_date: animal.arrival_date,
      arrival_age_months:
        animal.arrival_age_months === null ? '' : String(animal.arrival_age_months),
      breed_id: String(animal.breed_id),
      parent_id: animal.parent_id === null ? '' : String(animal.parent_id),
    });
  };

  const handleDelete = async (animal) => {
    setError('');
    try {
      await animalsApi.remove(token, animal.animal_id);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p>Загрузка...</p>;

  const breedOptions = [
    { value: '', label: '— выберите породу —' },
    ...breeds.map((breed) => ({ value: breed.breed_id, label: breed.name })),
  ];

  const parentOptions = [
    { value: '', label: '— нет —' },
    ...animals
      .filter((animal) => animal.animal_id !== editingId)
      .map((animal) => ({ value: animal.animal_id, label: animal.inventory_number })),
  ];

  return (
    <div>
      <h1>Животные</h1>

      <form onSubmit={handleSubmit} className="entity-form">
        <FormField
          id="inventory_number"
          label="Инвентарный номер"
          value={form.inventory_number}
          onChange={(event) =>
            setForm({ ...form, inventory_number: event.target.value })
          }
          required
        />

        <FormField
          id="gender"
          label="Пол"
          options={[
            { value: 'male', label: 'Самец' },
            { value: 'female', label: 'Самка' },
          ]}
          value={form.gender}
          onChange={(event) => setForm({ ...form, gender: event.target.value })}
          required
        />

        <FormField
          id="name"
          label="Кличка"
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
        />

        <FormField
          id="arrival_date"
          label="Дата прибытия"
          type="date"
          value={form.arrival_date}
          onChange={(event) => setForm({ ...form, arrival_date: event.target.value })}
          required
        />

        <FormField
          id="arrival_age_months"
          label="Возраст прибытия (мес.)"
          type="number"
          min="0"
          value={form.arrival_age_months}
          onChange={(event) =>
            setForm({ ...form, arrival_age_months: event.target.value })
          }
        />

        <FormField
          id="breed_id"
          label="Порода"
          options={breedOptions}
          value={form.breed_id}
          onChange={(event) => setForm({ ...form, breed_id: event.target.value })}
          required
        />

        <FormField
          id="parent_id"
          label="Родитель"
          options={parentOptions}
          value={form.parent_id}
          onChange={(event) => setForm({ ...form, parent_id: event.target.value })}
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
          { key: 'animal_id', label: 'ID' },
          { key: 'inventory_number', label: 'Инв. номер' },
          {
            key: 'gender',
            label: 'Пол',
            render: (row) => (row.gender === 'male' ? 'Самец' : 'Самка'),
          },
          { key: 'name', label: 'Кличка', render: (row) => row.name ?? '—' },
          { key: 'arrival_date', label: 'Дата прибытия' },
          { key: 'breed_id', label: 'Порода', render: (row) => breedName(row.breed_id) },
          {
            key: 'parent_id',
            label: 'Родитель',
            render: (row) => (row.parent_id === null ? '—' : animalLabel(row.parent_id)),
          },
        ]}
        rows={animals}
        rowKey="animal_id"
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
