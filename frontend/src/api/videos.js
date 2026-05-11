import axios from './axios'

/**
 * 生成视频
 * @param {Object} data - 视频生成参数
 * @param {number} data.product_id - 产品ID
 * @param {Array<number>} data.image_ids - 图片ID列表
 * @param {number} data.duration_per_image - 每张图片显示时长（秒）
 * @param {File} data.background_music - 背景音乐文件（可选）
 */
export const generateVideo = (data) => {
  const formData = new FormData()
  formData.append('product_id', data.product_id)
  formData.append('image_ids', JSON.stringify(data.image_ids))
  formData.append('duration_per_image', data.duration_per_image)

  if (data.background_music) {
    formData.append('background_music', data.background_music)
  }

  return axios.post('/v1/videos/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 300000 // 5分钟超时
  })
}

/**
 * 获取视频列表
 * @param {Object} params - 查询参数
 */
export const getVideos = (params) => {
  return axios.get('/v1/videos', { params })
}

/**
 * 获取视频详情
 * @param {number} id - 视频ID
 */
export const getVideo = (id) => {
  return axios.get(`/v1/videos/${id}`)
}

/**
 * 下载视频
 * @param {number} id - 视频ID
 */
export const downloadVideo = (id) => {
  return axios.get(`/v1/videos/${id}/download`, {
    responseType: 'blob'
  })
}
