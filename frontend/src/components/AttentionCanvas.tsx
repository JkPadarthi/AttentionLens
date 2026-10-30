import { useRef, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Label } from '@/components/ui/label'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Eye, Crosshair, SlidersHorizontal } from 'lucide-react'
import type { LayerMap } from '@/types'

interface AttentionCanvasProps {
  baseImageB64: string
  layers: LayerMap[]
  selectedLayer: number
  view: 'native' | 'class_conditioned'
  onViewChange: (view: 'native' | 'class_conditioned') => void
  opacity: number
  onOpacityChange: (opacity: number) => void
}

export function AttentionCanvas({
  baseImageB64,
  layers,
  selectedLayer,
  view,
  onViewChange,
  opacity,
  onOpacityChange,
}: AttentionCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const baseImageRef = useRef<HTMLImageElement | null>(null)
  const overlayImageRef = useRef<HTMLImageElement | null>(null)

  const selectedMap = layers[selectedLayer]

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const baseImg = new Image()
    baseImg.src = `data:image/png;base64,${baseImageB64}`
    baseImageRef.current = baseImg

    baseImg.onload = () => {
      canvas.width = baseImg.width
      canvas.height = baseImg.height

      const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(baseImg, 0, 0)

        if (selectedMap) {
          const overlayImg = new Image()
          overlayImg.src = `data:image/png;base64,${selectedMap.map_b64}`
          overlayImageRef.current = overlayImg

          overlayImg.onload = () => {
            ctx.globalAlpha = opacity
            ctx.drawImage(overlayImg, 0, 0, canvas.width, canvas.height)
            ctx.globalAlpha = 1.0
          }
        }
      }

      draw()
    }
  }, [baseImageB64, selectedMap, opacity])

  return (
    <Card>
      <CardContent className="p-5 space-y-4">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="space-y-2">
            <Label className="text-xs font-semibold flex items-center gap-1.5 text-muted-foreground">
              <Eye className="w-3.5 h-3.5" />
              View
            </Label>
            <Tabs value={view} onValueChange={(v) => onViewChange(v as any)}>
              <TabsList>
                <TabsTrigger value="native">Native</TabsTrigger>
                <TabsTrigger value="class_conditioned">
                  <span className="flex items-center gap-1.5">
                    <Crosshair className="w-3 h-3" />
                    Class-Conditioned
                  </span>
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
          <div className="flex-1 min-w-[200px] space-y-2">
            <Label className="text-xs font-semibold flex items-center gap-1.5 text-muted-foreground">
              <SlidersHorizontal className="w-3.5 h-3.5" />
              Overlay Opacity
              <span className="ml-auto font-mono text-primary">
                {Math.round(opacity * 100)}%
              </span>
            </Label>
            <Slider
              value={[opacity]}
              onValueChange={([val]) => onOpacityChange(val)}
              max={1}
              min={0}
              step={0.05}
            />
          </div>
        </div>

        <div className="flex justify-center bg-muted/50 rounded-lg overflow-hidden border border-border/50 ring-1 ring-border">
          <canvas ref={canvasRef} className="max-w-full h-auto" />
        </div>

        {selectedMap && (
          <div className="flex items-center justify-center gap-3 text-xs">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-primary/10 text-primary font-medium">
              {selectedMap.layer_name}
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-accent text-accent-foreground font-medium">
              {selectedMap.view === 'native' ? 'Native' : 'Class-Conditioned'}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
