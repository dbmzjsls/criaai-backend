import axios from './axios'

export const copywritingApi = {
  // 生成营销文案
  generateCopywriting(data) {
    return axios.post('/v1/copywriting/generate', data)
  }
}
