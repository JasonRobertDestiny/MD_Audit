/**
 * 验证文件类型
 * @param {File} file - 要验证的文件
 * @param {Array<string>} allowedExtensions - 允许的扩展名列表（如['.md', '.txt']）
 * @returns {Object} { valid: boolean, error: string }
 */
export function validateFileType(file, allowedExtensions = ['.md', '.txt', '.markdown']) {
  const fileName = file.name.toLowerCase()
  const isValid = allowedExtensions.some((ext) => fileName.endsWith(ext))

  if (!isValid) {
    const extName = fileName.split('.').pop()
    return {
      valid: false,
      error: `不支持的文件格式：.${extName}，仅支持 ${allowedExtensions.join(', ')} 格式`,
    }
  }

  return { valid: true, error: null }
}

/**
 * 验证文件大小
 * @param {File} file - 要验证的文件
 * @param {number} maxSizeInMB - 最大文件大小（MB）
 * @returns {Object} { valid: boolean, error: string }
 */
export function validateFileSize(file, maxSizeInMB = 10) {
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024
  const fileSizeInMB = (file.size / (1024 * 1024)).toFixed(2)

  if (file.size > maxSizeInBytes) {
    return {
      valid: false,
      error: `文件大小超过限制：${fileSizeInMB}MB（最大${maxSizeInMB}MB）`,
    }
  }

  return { valid: true, error: null }
}

/**
 * 验证文件
 * @param {File} file - 要验证的文件
 * @param {Object} options - 验证选项
 * @param {Array<string>} options.allowedExtensions - 允许的扩展名
 * @param {number} options.maxSizeInMB - 最大文件大小（MB）
 * @returns {Object} { valid: boolean, errors: Array<string> }
 */
export function validateFile(file, options = {}) {
  const {
    allowedExtensions = ['.md', '.txt', '.markdown'],
    maxSizeInMB = 10,
  } = options

  const errors = []

  // 验证文件类型
  const typeValidation = validateFileType(file, allowedExtensions)
  if (!typeValidation.valid) {
    errors.push(typeValidation.error)
  }

  // 验证文件大小
  const sizeValidation = validateFileSize(file, maxSizeInMB)
  if (!sizeValidation.valid) {
    errors.push(sizeValidation.error)
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * 验证关键词列表
 * @param {Array<string>} keywords - 关键词列表
 * @returns {Object} { valid: boolean, error: string }
 */
export function validateKeywords(keywords) {
  if (!keywords || keywords.length === 0) {
    return { valid: true, error: null }
  }

  if (!Array.isArray(keywords)) {
    return {
      valid: false,
      error: '关键词必须是数组格式',
    }
  }

  // 检查每个关键词
  const invalidKeywords = keywords.filter(
    (kw) => typeof kw !== 'string' || kw.trim().length === 0
  )

  if (invalidKeywords.length > 0) {
    return {
      valid: false,
      error: '关键词必须是非空字符串',
    }
  }

  // 检查关键词长度
  const tooLongKeywords = keywords.filter((kw) => kw.length > 100)
  if (tooLongKeywords.length > 0) {
    return {
      valid: false,
      error: '关键词长度不能超过100个字符',
    }
  }

  return { valid: true, error: null }
}

/**
 * 验证页码
 * @param {number} page - 页码
 * @returns {boolean}
 */
export function validatePageNumber(page) {
  return Number.isInteger(page) && page >= 1
}

/**
 * 验证页面大小
 * @param {number} pageSize - 页面大小
 * @param {number} maxPageSize - 最大页面大小
 * @returns {boolean}
 */
export function validatePageSize(pageSize, maxPageSize = 100) {
  return Number.isInteger(pageSize) && pageSize >= 1 && pageSize <= maxPageSize
}
