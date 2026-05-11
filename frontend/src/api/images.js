import axios from './axios'

export const imagesApi = {
  // 生成图片
  generateImage(formData) {
    return axios.post('/v1/images/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 图片生成可能需要更长时间
    })
  }
}
