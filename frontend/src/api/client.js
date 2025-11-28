import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000, // 30秒超时（分析可能需要较长时间）
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可在此添加认证token等（v2.0功能）
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 统一错误处理
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

/**
 * 上传并分析文件
 * @param {File} file - 要上传的文件
 * @param {Array<string>} keywords - 可选的关键词列表
 * @returns {Promise<Object>} 分析报告和历史记录ID
 */
export async function analyzeFile(file, keywords = []) {
  const formData = new FormData()
  formData.append('file', file)

  if (keywords && keywords.length > 0) {
    formData.append('keywords', JSON.stringify(keywords))
  }

  return apiClient.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 获取历史记录列表
 * @param {number} page - 页码（从1开始）
 * @param {number} pageSize - 每页记录数
 * @param {string} severity - 严重程度过滤（all/error/warning）
 * @returns {Promise<Object>} 历史记录列表和分页信息
 */
export async function getHistory(page = 1, pageSize = 20, severity = 'all') {
  return apiClient.get('/history', {
    params: {
      page,
      page_size: pageSize,
      severity,
    },
  })
}

/**
 * 获取历史记录详情
 * @param {string} recordId - 记录ID
 * @returns {Promise<Object>} 历史记录详情
 */
export async function getHistoryDetail(recordId) {
  return apiClient.get(`/history/${recordId}`)
}

/**
 * 检查API健康状态
 * @returns {Promise<Object>} 健康状态信息
 */
export async function checkHealth() {
  return axios.get('/api/health')
}

export default apiClient
