import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ImageUploader } from '@/components/ImageUploader'
import { ModelSelector } from '@/components/ModelSelector'
import { PredictionCard } from '@/components/PredictionCard'
import { AttentionCanvas } from '@/components/AttentionCanvas'
import { LayerBrowser } from '@/components/LayerBrowser'
import { analyzeImage, fetchModels } from '@/lib/api'
import type { Model, AnalysisResult } from '@/types'
import { Loader2, Search, Sparkles } from 'lucide-react'

export function AnalyzePage() {
  const [models, setModels] = useState<Model[]>([])
  const [selectedModel, setSelectedModel] = useState('resnet50')
  const [image, setImage] = useState<File | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedLayer, setSelectedLayer] = useState(0)
  const [view, setView] = useState<'native' | 'class_conditioned'>('class_conditioned')
  const [opacity, setOpacity] = useState(0.5)

  useEffect(() => {
    fetchModels().then(setModels).catch(console.error)
  }, [])

  const handleAnalyze = async () => {
    if (!image) return
    setLoading(true)
    try {
      const res = await analyzeImage(image, selectedModel)
      setResult(res)
      setSelectedLayer(0)
    } catch (err) {
      console.error(err)
      alert('Analysis failed. Check console for details.')
    } finally {
      setLoading(false)
    }
  }

  const handleViewChange = (newView: 'native' | 'class_conditioned') => {
    setView(newView)
    // Stay on the same layer, just switch its view type
    if (result && selectedLayer >= 0) {
      const currentLayerName = result.layers[selectedLayer].layer_name
      const sameLayerNewViewIdx = result.layers.findIndex(
        (l) => l.layer_name === currentLayerName && l.view === newView
      )
      if (sameLayerNewViewIdx !== -1) {
        setSelectedLayer(sameLayerNewViewIdx)
      }
    }
  }

  const handleLayerSelect = (idx: number) => {
    setSelectedLayer(idx)
    // Sync the view state with the selected layer
    if (result) {
      const layer = result.layers[idx]
      setView(layer.view)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/60 text-primary-foreground shadow-lg shadow-primary/20">
          <Sparkles className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analyze Attention</h1>
          <p className="text-muted-foreground mt-1">
            Explore what your model is looking at — layer by layer
          </p>
        </div>
      </div>

      {!result && (
        <div className="grid gap-8 lg:grid-cols-[1fr_1fr_auto]">
          <div className="space-y-6">
            <ImageUploader onImageSelect={setImage} />
          </div>
          <div className="space-y-6">
            <ModelSelector
              models={models}
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </div>
          <div className="flex items-end lg:pb-2">
            <Button
              onClick={handleAnalyze}
              disabled={!image || loading}
              size="lg"
              className="h-12 px-8 text-base shadow-lg shadow-primary/20"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              {loading ? 'Analyzing...' : 'Analyze Image'}
            </Button>
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="flex gap-4 items-center">
            <Button
              variant="outline"
              onClick={() => {
                setResult(null)
                setImage(null)
              }}
              className="gap-2"
            >
              ← New Analysis
            </Button>
            <div className="flex items-center gap-3 text-sm">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary font-medium">
                {result.model_id === 'resnet50' ? 'ResNet-50' : 'ViT-B/16'}
              </span>
              <span className="text-muted-foreground">
                {result.layers.length} attention maps
              </span>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
            <div className="space-y-6">
              <AttentionCanvas
                baseImageB64={result.base_image_b64}
                layers={result.layers}
                selectedLayer={selectedLayer}
                view={view}
                onViewChange={handleViewChange}
                opacity={opacity}
                onOpacityChange={setOpacity}
              />
              <PredictionCard
                predictions={result.top5}
                predictedClass={result.pred_label}
                confidence={result.confidence}
              />
            </div>

            <LayerBrowser
              layers={result.layers}
              selectedLayer={selectedLayer}
              view={view}
              onLayerSelect={handleLayerSelect}
            />
          </div>
        </div>
      )}
    </div>
  )
}
