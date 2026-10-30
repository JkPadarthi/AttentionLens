import axios from 'axios'
import type {
  Model,
  AnalysisResult,
  InterveneRequest,
  InterveneResponse,
} from '@/types'

const api = axios.create({
  baseURL: '/api',
})

export async function fetchModels(): Promise<Model[]> {
  const { data } = await api.get<Model[]>('/models')
  return data
}

export async function analyzeImage(
  image: File,
  modelId: string
): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append('image', image)
  formData.append('model_id', modelId)

  const { data } = await api.post<AnalysisResult>('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function intervene(
  request: InterveneRequest
): Promise<InterveneResponse> {
  const { data } = await api.post<InterveneResponse>('/intervene', request)
  return data
}
