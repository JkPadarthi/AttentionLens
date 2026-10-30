export interface Model {
  id: string
  name: string
  arch: 'cnn' | 'vit'
  description: string
  layers: string[]
}

export interface LayerMap {
  layer_name: string
  arch: string
  view: 'native' | 'class_conditioned'
  model_class: string
  map_b64: string
  head_or_channel: number | null
  metadata: Record<string, number>
}

export interface InterventionResult {
  region: [number, number, number, number]
  pred_before: string
  pred_after: string
  logit_delta: number
  metadata: Record<string, any>
}

export interface Prediction {
  label: string
  probability: number
}

export interface AnalysisResult {
  model_id: string
  image_id: string
  true_label: string
  pred_label: string
  base_image_b64: string
  layers: LayerMap[]
  intervention_results: InterventionResult[]
  top5: Prediction[]
  confidence: number
}

export interface InterveneRequest {
  image_b64: string
  model_id: string
  regions: Array<{ x: number; y: number; w: number; h: number }>
  strategy: 'zero' | 'blur' | 'var'
}

export interface InterveneResponse {
  results: InterventionResult[]
}
