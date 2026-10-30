import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ImageUploader } from '@/components/ImageUploader'
import { ModelSelector } from '@/components/ModelSelector'
import { InterventionCanvas } from '@/components/InterventionCanvas'
import { InterventionResultCard } from '@/components/InterventionResultCard'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { intervene, fetchModels } from '@/lib/api'
import type { Model, InterventionResult } from '@/types'
import { Loader2, Target, Zap } from 'lucide-react'

export function InterventionPage() {
  const [models, setModels] = useState<Model[]>([])
  const [selectedModel, setSelectedModel] = useState('resnet50')
  const [imageB64, setImageB64] = useState<string | null>(null)
  const [maskSize, setMaskSize] = useState(48)
  const [maskPosition, setMaskPosition] = useState<{ x: number; y: number; size: number } | null>(null)
  const [strategy, setStrategy] = useState<'zero' | 'blur' | 'var'>('zero')
  const [result, setResult] = useState<InterventionResult | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchModels().then(setModels).catch(console.error)
  }, [])

  const handleImageSelect = (file: File) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1]
      setImageB64(base64)
    }
    reader.readAsDataURL(file)
  }

  const handleRunProbe = async () => {
    if (!imageB64 || !maskPosition) return
    setLoading(true)
    try {
      const res = await intervene({
        image_b64: imageB64,
        model_id: selectedModel,
        regions: [
          {
            x: Math.round(maskPosition.x - maskPosition.size / 2),
            y: Math.round(maskPosition.y - maskPosition.size / 2),
            w: maskPosition.size,
            h: maskPosition.size,
          },
        ],
        strategy,
      })
      if (res.results.length > 0) {
        setResult(res.results[0])
      }
    } catch (err) {
      console.error(err)
      alert('Intervention failed. Check console for details.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/60 text-primary-foreground shadow-lg shadow-primary/20">
          <Zap className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Intervention Lab</h1>
          <p className="text-muted-foreground mt-1">
            Test causal dependencies — mask regions and watch predictions change
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          {!imageB64 ? (
            <ImageUploader onImageSelect={handleImageSelect} />
          ) : (
            <>
              <InterventionCanvas
                imageB64={imageB64}
                maskSize={maskSize}
                onMaskSizeChange={setMaskSize}
                onMaskPosition={(x, y, size) => setMaskPosition({ x, y, size })}
              />
              <Button
                variant="outline"
                onClick={() => {
                  setImageB64(null)
                  setResult(null)
                  setMaskPosition(null)
                }}
                className="gap-2"
              >
                ← Upload Different Image
              </Button>
            </>
          )}
        </div>

        <div className="space-y-6">
          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
          />

          <div className="rounded-lg border bg-card p-4 space-y-4">
            <div className="space-y-2">
              <Label className="text-sm font-semibold">Masking Strategy</Label>
              <Select
                value={strategy}
                onValueChange={(val) => setStrategy(val as any)}
              >
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="zero">Zero (ImageNet mean)</SelectItem>
                  <SelectItem value="blur">Blur (box average)</SelectItem>
                  <SelectItem value="var">Variance (noise injection)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleRunProbe}
              disabled={!maskPosition || loading}
              size="lg"
              className="w-full h-11 gap-2 shadow-lg shadow-primary/20"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Target className="w-5 h-5" />
              )}
              {loading ? 'Probing...' : 'Run Probe'}
            </Button>
          </div>

          <InterventionResultCard result={result} />
        </div>
      </div>
    </div>
  )
}
