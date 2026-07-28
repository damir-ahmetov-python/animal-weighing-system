const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Кастомная ошибка с HTTP-статусом, чтобы вызывающий код мог при желании
// различать 404/409/401 и т.д., а не просто ловить "какую-то" ошибку.
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// На 401 сюда прилетает вызов извне (см. AuthContext) - так логаут можно
// сделать в одном месте, а не проверять 401 в каждой странице отдельно.
let unauthorizedHandler = () => {};

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

function extractErrorMessage(data) {
  if (!data) return 'Something went wrong. Please try again.';

  // Обычная ошибка FastAPI: {"detail": "текст"}
  if (typeof data.detail === 'string') return data.detail;

  // Ошибка валидации Pydantic: {"detail": [{"msg": "текст"}, ...]}
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item.msg).join(', ');
  }

  return 'Something went wrong. Please try again.';
}

async function request(path, options = {}) {
  let res;

  try {
    res = await fetch(`${BASE_URL}${path}`, options);
  } catch {
    throw new ApiError('Cannot reach the server. Is the backend running?', 0);
  }

  if (res.status === 401) {
    unauthorizedHandler();
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    // тело пустое или не JSON - оставляем data пустым
  }

  if (!res.ok) {
    throw new ApiError(extractErrorMessage(data), res.status);
  }

  return data;
}

function authHeader(token) {
  return { Authorization: `Bearer ${token}` };
}

export function registerUser({ login, email, password }) {
  return request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, email, password }),
  });
}

export function loginUser(login, password) {
  // /auth/login ждёт form-urlencoded (OAuth2PasswordRequestForm), а не JSON,
  // и поле называется "username", хотя у нас в системе это login.
  return request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: login, password }),
  });
}

export function getMe(token) {
  return request('/users/me', {
    headers: authHeader(token),
  });
}

function authedJson(token) {
  return { 'Content-Type': 'application/json', ...authHeader(token) };
}

// Список/создание/редактирование/удаление у animal_types, breeds, animals и
// weightings устроены одинаково на backend - list/create/update/remove через
// одну и ту же фабрику, вместо того чтобы 4 раза копировать одни и те же 4 функции.
function crudApi(basePath) {
  return {
    list: (token) => request(basePath, { headers: authHeader(token) }),

    create: (token, data) =>
      request(basePath, {
        method: 'POST',
        headers: authedJson(token),
        body: JSON.stringify(data),
      }),

    update: (token, id, data) =>
      request(`${basePath}/${id}`, {
        method: 'PATCH',
        headers: authedJson(token),
        body: JSON.stringify(data),
      }),

    remove: (token, id) =>
      request(`${basePath}/${id}`, {
        method: 'DELETE',
        headers: authHeader(token),
      }),
  };
}

export const animalTypesApi = crudApi('/animal_types');
export const breedsApi = crudApi('/breeds');
export const animalsApi = crudApi('/animals');
export const weightingsApi = crudApi('/weightings');

// Admin-эндпоинты не укладываются в тот же CRUD-паттерн (нет create,
// вместо update - конкретное действие toggle-active), поэтому отдельно.
export function getUsers(token) {
  return request('/admin/users', { headers: authHeader(token) });
}

export function toggleUserActive(token, userId) {
  return request(`/admin/users/${userId}/toggle-active`, {
    method: 'PATCH',
    headers: authHeader(token),
  });
}
