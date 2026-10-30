import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Layers3, Activity, CircleDot, SunMedium } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { LayerMap } from '@/types'

interface LayerBrowserProps {
  layers: LayerMap[]
  selectedLayer: number
  view: 'native' | 'class_conditioned'
  onLayerSelect: (idx: number) => void
}

export function LayerBrowser({
  layers,
  selectedLayer,
  view,
  onLayerSelect,
}: LayerBrowserProps) {
  const filteredLayers = layers.filter((l) => l.view === view)

  return (
    <Card className="h-fit">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Layers3 className="w-4 h-4 text-primary" />
          <CardTitle className="text-base">Layers</CardTitle>
          <span className="ml-auto text-xs font-medium text-muted-foreground px-2 py-0.5 rounded-md bg-muted">
            {filteredLayers.length}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1.5">
          {filteredLayers.map((layer) => {
            const originalIdx = layers.findIndex((l) => l === layer)
            const isSelected = selectedLayer === originalIdx
            return (
              <button
                key={layer.layer_name}
                onClick={() => onLayerSelect(originalIdx)}
                className={cn(
                  'w-full p-3 rounded-lg border-2 text-left transition-all cursor-pointer',
                  isSelected
                    ? 'border-primary bg-primary/5 shadow-md shadow-primary/10'
                    : 'border-transparent bg-muted/30 hover:bg-muted/60 hover:border-primary/30'
                )}
              >
                <div className="flex items-center gap-2">
                  <div
                    className={cn(
                      'flex h-7 w-7 items-center justify-center rounded-md text-xs font-bold transition-colors',
                      isSelected
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground'
                    )}
                  >
                    {layer.layer_name.replace(/\D/g, '').slice(-2) || '?'}
                  </div>
                  <div
                    className={cn(
                      'font-semibold text-sm',
                      isSelected ? 'text-primary' : 'text-foreground'
                    )}
                  >
                    {layer.layer_name}
                  </div>
                </div>

                {(layer.metadata.entropy !== undefined ||
                  layer.metadata.object_relevance_share !== undefined) && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {layer.metadata.entropy !== undefined && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-muted text-xs font-medium text-muted-foreground">
                        <Activity className="w-3 h-3" />
                        H: {layer.metadata.entropy.toFixed(1)}
                      </span>
                    )}
                    {layer.metadata.object_relevance_share !== undefined && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-accent/60 text-xs font-medium text-accent-foreground">
                        <CircleDot className="w-3 h-3" />
                        Obj: {(layer.metadata.object_relevance_share * 100).toFixed(0)}%
                      </span>
                    )}
                    {layer.metadata.background_sensitivity !== undefined && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-chart-3/20 text-xs font-medium text-foreground">
                        <SunMedium className="w-3 h-3" />
                        BG: {(layer.metadata.background_sensitivity * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
