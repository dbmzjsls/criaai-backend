/**
 * 素材库 API
 */
import axios from './axios'

/**
 * 上传素材
 */
export const uploadMedia = async (file, tags = []) => {
  const formData = new FormData()
  formData.append('file', file)
  if (tags.length > 0) {
    formData.append('tags', tags.join(','))
  }
  const response = await axios.post('/v1/media/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

/**
 * 获取素材列表
 */
export const getMediaList = async (mediaType = null) => {
  const params = mediaType ? { media_type: mediaType } : {}
  const response = await axios.get('/v1/media', { params })
  return response.data
}

/**
 * 删除素材
 */
export const deleteMedia = async (mediaId) => {
  const response = await axios.delete(`/v1/media/${mediaId}`)
  return response.data
}
