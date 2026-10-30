import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, AlertTriangle, CheckCircle2, Target } from 'lucide-react'
import type { InterventionResult } from '@/types'
import { cn } from '@/lib/utils'

interface InterventionResultCardProps {
  result: InterventionResult | null
}

export function InterventionResultCard({ result }: InterventionResultCardProps) {
  if (!result) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-muted-foreground" />
            <CardTitle className="text-base">Intervention Result</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground text-center py-10 border-2 border-dashed border-border rounded-lg">
            <Target className="w-8 h-8 mx-auto mb-2 opacity-30" />
            Click on the image and run a probe
            <br />
            to see results
          </div>
        </CardContent>
      </Card>
    )
  }

  const reliedOnRegion = result.logit_delta > 0

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          {reliedOnRegion ? (
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          )}
          <CardTitle className="text-base">Intervention Result</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-2 items-center py-3 rounded-lg bg-muted/50">
          <div className="text-center">
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 font-semibold">
              Before
            </div>
            <div className="font-bold text-sm truncate">{result.pred_before}</div>
          </div>
          <ArrowRight className="w-4 h-4 mx-auto text-muted-foreground" />
          <div className="text-center">
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 font-semibold">
              After
            </div>
            <div className="font-bold text-sm truncate">{result.pred_after}</div>
          </div>
        </div>

        <div className="pt-3 border-t">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1 font-semibold">
            Logit Delta
          </div>
          <div
            className={cn(
              'text-3xl font-bold tabular-nums',
              reliedOnRegion ? 'text-amber-500 dark:text-amber-400' : 'text-emerald-500 dark:text-emerald-400'
            )}
          >
            {result.logit_delta > 0 ? '+' : ''}
            {result.logit_delta.toFixed(3)}
          </div>
        </div>

        <div
          className={cn(
            'p-3 rounded-lg border-2 text-sm',
            reliedOnRegion
              ? 'bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-950/30 dark:border-amber-900 dark:text-amber-100'
              : 'bg-emerald-50 border-emerald-200 text-emerald-900 dark:bg-emerald-950/30 dark:border-emerald-900 dark:text-emerald-100'
          )}
        >
          {reliedOnRegion ? (
            <>
              <div className="flex items-center gap-1.5 font-bold mb-1">
                <AlertTriangle className="w-4 h-4" />
                Model relied on this region
              </div>
              <div className="opacity-90 text-xs">
                Masking caused the prediction confidence to drop — this region
                was important for the model's decision.
              </div>
            </>
          ) : (
            <>
              <div className="flex items-center gap-1.5 font-bold mb-1">
                <CheckCircle2 className="w-4 h-4" />
                Model ignored this region
              </div>
              <div className="opacity-90 text-xs">
                Masking did not significantly affect the prediction — the model
                does not rely on this area.
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
