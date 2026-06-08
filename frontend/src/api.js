import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
});

// Attach Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData);
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const poApi = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    // Boundary is automatically set by the browser
    const response = await api.post('/po/upload', formData);
    return response.data;
  },
  list: async (params = {}) => {
    const response = await api.get('/po/list', { params });
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/po/${id}`);
    return response.data;
  },
  downloadFile: async (id, filename) => {
    const response = await api.get(`/po/file/${id}`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || `document_${id}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
  exportCsv: async () => {
    const response = await api.get('/po/export/csv', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'purchase_orders.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
  exportExcel: async () => {
    const response = await api.get('/po/export/excel', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'purchase_orders.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
};

export default api;
