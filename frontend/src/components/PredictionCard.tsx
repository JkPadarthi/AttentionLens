import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp } from 'lucide-react'
import type { Prediction } from '@/types'

interface PredictionCardProps {
  predictions: Prediction[]
  predictedClass: string
  confidence: number
}

export function PredictionCard({
  predictions,
  predictedClass,
  confidence,
}: PredictionCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-primary" />
          <CardTitle className="text-base">Top Predictions</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-5 pb-5 border-b">
          <div className="flex items-baseline gap-2">
            <div className="text-2xl font-bold tracking-tight">{predictedClass}</div>
            <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs font-semibold">
              <TrendingUp className="w-3 h-3" />
              {(confidence * 100).toFixed(1)}%
            </div>
          </div>
        </div>
        <div className="space-y-3">
          {predictions.map((pred, idx) => (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="font-medium truncate">{pred.label}</span>
                <span className="font-mono text-muted-foreground tabular-nums">
                  {(pred.probability * 100).toFixed(1)}%
                </span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${pred.probability * 100}%`,
                    background: idx === 0
                      ? 'linear-gradient(90deg, var(--primary), var(--primary) 80%)'
                      : idx === 1
                        ? 'linear-gradient(90deg, var(--chart-2), var(--chart-2) 80%)'
                        : 'linear-gradient(90deg, var(--muted-foreground), var(--muted-foreground) 80%)',
                    opacity: idx === 0 ? 1 : idx === 1 ? 0.8 : 0.4,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
