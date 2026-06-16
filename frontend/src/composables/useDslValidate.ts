import { workflowApi } from '@/api/workflow'
import { useWorkflowStore } from '@/stores/workflow'

// Frontend-triggered validation that delegates to the backend validator.
export function useDslValidate() {
  const wf = useWorkflowStore()

  async function validate(): Promise<{ valid: boolean; errors: string[] }> {
    return workflowApi.validate(wf.toDsl())
  }

  return { validate }
}
