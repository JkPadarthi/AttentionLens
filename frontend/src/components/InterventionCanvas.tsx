import { useRef, useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Label } from '@/components/ui/label'
import { MousePointerClick, Ruler } from 'lucide-react'

interface InterventionCanvasProps {
  imageB64: string
  maskSize: number
  onMaskSizeChange: (size: number) => void
  onMaskPosition: (x: number, y: number, size: number) => void
}

export function InterventionCanvas({
  imageB64,
  maskSize,
  onMaskSizeChange,
  onMaskPosition,
}: InterventionCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [maskPosition, setMaskPosition] = useState<{ x: number; y: number } | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const img = new Image()
    img.src = `data:image/png;base64,${imageB64}`

    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height

      const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(img, 0, 0)

        if (maskPosition) {
          // Amber fill for mask
          ctx.fillStyle = 'rgba(245, 158, 11, 0.35)'
          ctx.fillRect(
            maskPosition.x - maskSize / 2,
            maskPosition.y - maskSize / 2,
            maskSize,
            maskSize
          )
          // Amber border with dashes
          ctx.strokeStyle = 'rgba(245, 158, 11, 0.9)'
          ctx.lineWidth = 2
          ctx.setLineDash([6, 4])
          ctx.strokeRect(
            maskPosition.x - maskSize / 2,
            maskPosition.y - maskSize / 2,
            maskSize,
            maskSize
          )
          ctx.setLineDash([])
          // Crosshair in center
          ctx.strokeStyle = 'rgba(245, 158, 11, 1)'
          ctx.lineWidth = 1.5
          const cx = maskPosition.x
          const cy = maskPosition.y
          ctx.beginPath()
          ctx.moveTo(cx - 8, cy)
          ctx.lineTo(cx + 8, cy)
          ctx.moveTo(cx, cy - 8)
          ctx.lineTo(cx, cy + 8)
          ctx.stroke()
        }
      }

      draw()
    }
  }, [imageB64, maskPosition, maskSize])

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * canvas.width
    const y = ((e.clientY - rect.top) / rect.height) * canvas.height

    setMaskPosition({ x, y })
    onMaskPosition(x, y, maskSize)
  }

  return (
    <Card>
      <CardContent className="p-5 space-y-4">
        <div className="space-y-2">
          <Label className="text-xs font-semibold flex items-center gap-1.5 text-muted-foreground">
            <Ruler className="w-3.5 h-3.5" />
            Mask Size
            <span className="ml-auto font-mono text-primary text-sm">
              {maskSize}px
            </span>
          </Label>
          <Slider
            value={[maskSize]}
            onValueChange={([val]) => {
              onMaskSizeChange(val)
              if (maskPosition) {
                onMaskPosition(maskPosition.x, maskPosition.y, val)
              }
            }}
            max={112}
            min={8}
            step={8}
          />
        </div>

        <div className="relative flex justify-center bg-muted/50 rounded-lg overflow-hidden border border-border/50 ring-1 ring-border cursor-crosshair group">
          <canvas
            ref={canvasRef}
            onClick={handleClick}
            className="max-w-full h-auto"
          />
          {!maskPosition && (
            <div className="absolute inset-0 flex items-center justify-center bg-foreground/30 pointer-events-none">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-background/90 text-sm font-medium text-foreground shadow-md">
                <MousePointerClick className="w-4 h-4 text-primary" />
                Click to place mask
              </div>
            </div>
          )}
        </div>

        {maskPosition && (
          <div className="text-xs text-center text-muted-foreground font-mono">
            Mask at ({Math.round(maskPosition.x)}, {Math.round(maskPosition.y)}) · {maskSize}px
          </div>
        )}
      </CardContent>
    </Card>
  )
}
