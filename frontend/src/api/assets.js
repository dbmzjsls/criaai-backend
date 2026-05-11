import axios from './axios'

/**
 * 获取资产列表
 * @param {Object} params - 查询参数
 * @param {string} params.asset_type - 资产类型 (copywriting/image/video)
 * @param {number} params.product_id - 产品ID
 * @param {string} params.search - 搜索关键词
 * @param {number} params.skip - 跳过数量
 * @param {number} params.limit - 限制数量
 */
export const getAssets = (params) => {
  return axios.get('/v1/assets', { params })
}

/**
 * 获取单个资产详情
 * @param {number} id - 资产ID
 */
export const getAsset = (id) => {
  return axios.get(`/v1/assets/${id}`)
}

/**
 * 删除资产
 * @param {number} id - 资产ID
 */
export const deleteAsset = (id) => {
  return axios.delete(`/v1/assets/${id}`)
}
