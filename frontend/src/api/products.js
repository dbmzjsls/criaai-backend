import axios from './axios'

/**
 * 获取产品列表
 */
export const getProducts = () => {
  return axios.get('/v1/products')
}

/**
 * 获取单个产品详情
 * @param {number} id - 产品ID
 */
export const getProduct = (id) => {
  return axios.get(`/v1/products/${id}`)
}

/**
 * 创建产品
 * @param {Object} data - 产品数据
 */
export const createProduct = (data) => {
  return axios.post('/v1/products', data)
}

/**
 * 更新产品
 * @param {number} id - 产品ID
 * @param {Object} data - 产品数据
 */
export const updateProduct = (id, data) => {
  return axios.put(`/v1/products/${id}`, data)
}

/**
 * 删除产品
 * @param {number} id - 产品ID
 */
export const deleteProduct = (id) => {
  return axios.delete(`/v1/products/${id}`)
}
