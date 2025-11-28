/**
 * 格式化相对时间
 * @param {string} timestamp - ISO格式时间戳
 * @returns {string} 相对时间字符串（如"5分钟前"）
 */
export function formatRelativeTime(timestamp) {
  const now = new Date()
  const date = new Date(timestamp)
  const diffInSeconds = Math.floor((now - date) / 1000)

  if (diffInSeconds < 60) {
    return '刚刚'
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`
  }

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `${diffInHours}小时前`
  }

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) {
    return `${diffInDays}天前`
  }

  // 超过7天，显示具体日期
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

/**
 * 格式化完整时间
 * @param {string} timestamp - ISO格式时间戳
 * @returns {string} 格式化的时间字符串
 */
export function formatFullTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 可读的文件大小字符串
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * 获取分数等级文本
 * @param {number} score - 分数（0-100）
 * @returns {string} 等级文本
 */
export function getScoreGrade(score) {
  if (score >= 90) return '优秀'
  if (score >= 70) return '良好'
  if (score >= 50) return '中等'
  return '较差'
}

/**
 * 获取分数对应的颜色类名
 * @param {number} score - 分数（0-100）
 * @returns {string} Tailwind CSS颜色类名
 */
export function getScoreColorClass(score) {
  if (score >= 90) return 'text-green-600 bg-green-50 border-green-200'
  if (score >= 70) return 'text-blue-600 bg-blue-50 border-blue-200'
  if (score >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
  return 'text-red-600 bg-red-50 border-red-200'
}

/**
 * 获取严重程度对应的颜色类名
 * @param {string} severity - 严重程度（error/warning/success）
 * @returns {string} Tailwind CSS颜色类名
 */
export function getSeverityColorClass(severity) {
  const colorMap = {
    error: 'text-red-700 bg-red-50 border-red-200',
    warning: 'text-yellow-700 bg-yellow-50 border-yellow-200',
    success: 'text-green-700 bg-green-50 border-green-200',
  }
  return colorMap[severity] || 'text-gray-700 bg-gray-50 border-gray-200'
}

/**
 * 获取严重程度对应的图标
 * @param {string} severity - 严重程度（error/warning/success）
 * @returns {string} 图标表情
 */
export function getSeverityIcon(severity) {
  const iconMap = {
    error: '🔴',
    warning: '🟡',
    success: '🟢',
  }
  return iconMap[severity] || '⚪'
}

/**
 * 截断文本
 * @param {string} text - 原始文本
 * @param {number} maxLength - 最大长度
 * @returns {string} 截断后的文本
 */
export function truncateText(text, maxLength = 100) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
