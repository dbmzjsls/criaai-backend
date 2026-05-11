import axios from './axios'

/**
 * 获取仪表板统计数据
 */
export const getDashboardStats = () => {
  return axios.get('/v1/dashboard/stats')
}

/**
 * 获取最近生成的资产
 * @param {number} limit - 限制数量
 */
export const getRecentAssets = (limit = 5) => {
  return axios.get('/v1/dashboard/recent-assets', {
    params: { limit }
  })
}

/**
 * 获取系统状态
 */
export const getSystemStatus = () => {
  return axios.get('/v1/dashboard/system-status')
}
