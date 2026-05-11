import axiosInstance from './axios'

export const startPipeline = (data) =>
  axiosInstance.post('/v1/pipeline/generate', data)

export const getTaskStatus = (taskId) =>
  axiosInstance.get(`/v1/pipeline/tasks/${taskId}`)
