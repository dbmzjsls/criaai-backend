import axios from 'axios'

// 开发环境: baseURL='/api', Vite proxy → localhost:8000
// 生产环境: baseURL='https://xxx.railway.app/api'
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const baseURL = API_BASE ? `${API_BASE}/api` : '/api'

const instance = axios.create({
  baseURL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error)
  }
)

export default instance
