const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

/**
 * 解决媒体文件 URL：
 * - 绝对 URL（http/https）直接返回
 * - 生产环境下相对路径补上后端域名
 * - 开发环境下保留相对路径（Vite 代理 /static → localhost:8000）
 */
export function resolveMediaUrl(url) {
  if (!url) return url
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('data:') || url.startsWith('blob:')) return url
  if (API_BASE) {
    return API_BASE + url
  }
  return url
}
