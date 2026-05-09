import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { documentService } from '@/services/documentService'
import { Document } from '@/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Upload, FileText, Trash2, Search, Plus } from 'lucide-react'
import { formatRelativeTime } from '@/utils/helpers'

const DocumentsPage: React.FC = () => {
  const { user } = useAuthStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const queryClient = useQueryClient()

  // Fetch documents
  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', user?.workspace_id, searchTerm],
    queryFn: () => documentService.list(),
    enabled: !!user?.workspace_id,
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file, title }: { file: File; title?: string }) =>
      documentService.upload(file, title, (progress) => setUploadProgress(progress)),
    onSuccess: () => {
      setUploadProgress(0)
      setIsUploading(false)
      queryClient.invalidateQueries(['documents'])
    },
    onError: () => {
      setUploadProgress(0)
      setIsUploading(false)
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: documentService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['documents'])
    },
  })

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const validation = documentService.validateFile(file)
    if (!validation.isValid) {
      alert(validation.error)
      return
    }

    setIsUploading(true)
    uploadMutation.mutate({ file })
  }

  const handleDelete = (doc: Document) => {
    if (confirm(`Are you sure you want to delete "${doc.title}"?`)) {
      deleteMutation.mutate(doc.id)
    }
  }

  const filteredDocuments = documents?.filter(doc =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
            <p className="text-gray-600 mt-2">
              Manage your knowledge base documents
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>

            {/* Upload Button */}
            <div className="relative">
              <input
                type="file"
                onChange={handleFileUpload}
                accept=".txt,.pdf,.docx,.md,.markdown"
                disabled={isUploading}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Button disabled={isUploading}>
                <Plus className="h-4 w-4 mr-2" />
                {isUploading ? `Uploading ${uploadProgress}%` : 'Upload Document'}
              </Button>
            </div>
          </div>
        </div>

        {/* Upload Progress */}
        {isUploading && (
          <div className="mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">
                    Uploading document...
                  </p>
                  <div className="mt-2">
                    <div className="bg-blue-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Documents Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : filteredDocuments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDocuments.map((doc) => (
              <Card key={doc.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="text-2xl">
                        {documentService.getFileIcon(doc.filename)}
                      </div>
                      <div>
                        <CardTitle className="text-lg line-clamp-1">
                          {doc.title}
                        </CardTitle>
                        <CardDescription>
                          {documentService.getFileTypeLabel(doc.filename)}
                        </CardDescription>
                      </div>
                    </div>
                    
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDelete(doc)}
                      disabled={deleteMutation.isLoading}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>{doc.filename}</span>
                      <span>{formatRelativeTime(doc.created_at)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchTerm ? 'No documents found' : 'No documents yet'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchTerm 
                ? 'Try adjusting your search terms'
                : 'Upload your first document to get started with the RAG assistant'
              }
            </p>
            {!searchTerm && (
              <div className="relative">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  accept=".txt,.pdf,.docx,.md,.markdown"
                  disabled={isUploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload First Document
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentsPage
