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
    let message = '请求失败'
    const detail = error.response?.data?.detail

    if (typeof detail === 'string') {
      message = detail
    } else if (detail?.message) {
      // 后端返回 ErrorResponse 对象
      message = detail.message
      if (detail.details) {
        message += `: ${detail.details}`
      }
    } else if (error.message) {
      message = error.message
    }

    console.error('API Error:', message, error.response?.data)
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
 * 批量上传并分析多个文件
 * @param {File[]} files - 要上传的文件数组
 * @returns {Promise<Object>} 批量分析结果
 */
export async function analyzeBatch(files) {
  const formData = new FormData()

  for (const file of files) {
    formData.append('files', file)
  }

  return apiClient.post('/analyze/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 120000, // 批量分析需要更长超时（2分钟）
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

/**
 * 导出分析报告为Markdown文件
 * @param {Object} report - 分析结果对象（SEOReport）
 * @returns {Promise<Blob>} Markdown文件Blob
 */
export async function exportMarkdownReport(report) {
  return apiClient.post('/analyze/export/markdown', report, {
    responseType: 'blob',
    headers: {
      Accept: 'text/markdown',
    },
  })
}

// 同步方法到默认客户端，便于统一调用
apiClient.exportMarkdownReport = exportMarkdownReport

export default apiClient
