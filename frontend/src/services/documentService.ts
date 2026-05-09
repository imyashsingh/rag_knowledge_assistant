import { api, uploadFile } from '@/utils/api'
import { Document } from '@/types'
import { API_ENDPOINTS, UPLOAD_CONSTANTS } from '@/constants/api'

export const documentService = {
  // Upload document
  upload: async (
    file: File,
    title?: string,
    onProgress?: (progress: number) => void
  ): Promise<Document> => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }

    const response = await uploadFile(
      API_ENDPOINTS.DOCUMENTS.UPLOAD,
      file,
      onProgress
    )
    return response.data
  },

  // List documents
  list: async (params?: {
    skip?: number
    limit?: number
  }): Promise<Document[]> => {
    const response = await api.get<Document[]>(
      API_ENDPOINTS.DOCUMENTS.LIST,
      { params }
    )
    return response.data
  },

  // Get document by ID
  getById: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(
      API_ENDPOINTS.DOCUMENTS.DETAIL(id)
    )
    return response.data
  },

  // Delete document
  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(
      API_ENDPOINTS.DOCUMENTS.DELETE(id)
    )
    return response.data
  },

  // Validate file
  validateFile: (file: File): { isValid: boolean; error?: string } => {
    // Check file size
    if (file.size > UPLOAD_CONSTANTS.MAX_FILE_SIZE) {
      return {
        isValid: false,
        error: `File size must be less than ${UPLOAD_CONSTANTS.MAX_FILE_SIZE / (1024 * 1024)}MB`
      }
    }

    // Check file extension
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!UPLOAD_CONSTANTS.SUPPORTED_EXTENSIONS.includes(fileExtension as any)) {
      return {
        isValid: false,
        error: `Unsupported file type. Supported types: ${UPLOAD_CONSTANTS.SUPPORTED_EXTENSIONS.join(', ')}`
      }
    }

    return { isValid: true }
  },

  // Get file icon based on type
  getFileIcon: (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase()
    
    switch (extension) {
      case 'pdf':
        return '📄'
      case 'docx':
        return '📝'
      case 'txt':
        return '📄'
      case 'md':
      case 'markdown':
        return '📄'
      default:
        return '📄'
    }
  },

  // Get file type label
  getFileTypeLabel: (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase()
    
    switch (extension) {
      case 'pdf':
        return 'PDF Document'
      case 'docx':
        return 'Word Document'
      case 'txt':
        return 'Text File'
      case 'md':
      case 'markdown':
        return 'Markdown File'
      default:
        return 'Unknown File'
    }
  },
}
