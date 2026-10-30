import { Brain, Layers, Check } from 'lucide-react'
import type { Model } from '@/types'
import { cn } from '@/lib/utils'

interface ModelSelectorProps {
  models: Model[]
  selectedModel: string
  onModelChange: (modelId: string) => void
}

export function ModelSelector({
  models,
  selectedModel,
  onModelChange,
}: ModelSelectorProps) {
  const iconMap: Record<string, React.ElementType> = {
    resnet50: Layers,
    vit_b16: Brain,
  }

  return (
    <div className="rounded-xl border bg-card p-5 space-y-3">
      <div className="flex items-center gap-2">
        <Layers className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-semibold">Model</h3>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {models.map((model) => {
          const Icon = iconMap[model.id] || Layers
          const isSelected = selectedModel === model.id
          return (
            <button
              key={model.id}
              onClick={() => onModelChange(model.id)}
              className={cn(
                'relative flex flex-col items-start gap-2 rounded-lg border-2 p-4 text-left transition-all cursor-pointer',
                isSelected
                  ? 'border-primary bg-primary/5 shadow-md shadow-primary/10'
                  : 'border-border hover:border-primary/40 hover:bg-muted/50'
              )}
            >
              {isSelected && (
                <div className="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <Check className="w-3 h-3" />
                </div>
              )}
              <div
                className={cn(
                  'flex h-9 w-9 items-center justify-center rounded-lg transition-colors',
                  isSelected
                    ? 'bg-gradient-to-br from-primary to-primary/70 text-primary-foreground shadow-sm'
                    : 'bg-muted text-muted-foreground'
                )}
              >
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <div className={cn(
                  'font-semibold text-sm',
                  isSelected ? 'text-primary' : 'text-foreground'
                )}>
                  {model.name}
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">
                  {model.arch.toUpperCase()} · {model.layers.length} layers
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
