import { useEffect, useCallback } from 'react'
import { dbService } from '../services/DatabaseService'

export const useIntegrityTracking = () => {
  const trackAction = useCallback(async (studentId, action, metadata = {}) => {
    await dbService.logAction(studentId, action, metadata)
  }, [])

  const updateScore = useCallback(async (studentId, newScore) => {
    return await dbService.updateIntegrityScore(studentId, newScore)
  }, [])

  const recordWorkstreamProgress = useCallback(async (studentId, workstreamId, progress, status) => {
    return await dbService.recordWorkstreamUpdate(studentId, workstreamId, {
      progress,
      status,
      completedAt: status === 'completed' ? new Date().toISOString() : null
    })
  }, [])

  return {
    trackAction,
    updateScore,
    recordWorkstreamProgress
  }
}
