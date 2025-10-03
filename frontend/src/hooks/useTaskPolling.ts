/**
 * Real-time task status polling hook
 * Polls Celery task status until completion
 */
import { useState, useEffect, useCallback } from 'react';

export interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY';
  ready: boolean;
  successful: boolean | null;
  result?: any;
  error?: string;
}

interface UseTaskPollingOptions {
  taskId: string | null;
  interval?: number;  // Polling interval in ms (default: 2000)
  enabled?: boolean;  // Enable/disable polling
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
}

export function useTaskPolling({
  taskId,
  interval = 2000,
  enabled = true,
  onSuccess,
  onError
}: UseTaskPollingOptions) {
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  const fetchTaskStatus = useCallback(async (id: string) => {
    try {
      const response = await fetch(`/api/tasks/status/${id}`);
      const data: TaskStatus = await response.json();

      setStatus(data);

      // Stop polling if task is complete
      if (data.ready) {
        setIsPolling(false);

        if (data.successful && onSuccess && data.result) {
          onSuccess(data.result);
        } else if (!data.successful && onError && data.error) {
          onError(data.error);
        }
      }

      return data;
    } catch (error) {
      console.error('Failed to fetch task status:', error);
      setIsPolling(false);
      if (onError) {
        onError('Failed to fetch task status');
      }
    }
  }, [onSuccess, onError]);

  useEffect(() => {
    if (!taskId || !enabled) {
      setIsPolling(false);
      return;
    }

    setIsPolling(true);

    // Initial fetch
    fetchTaskStatus(taskId);

    // Set up polling interval
    const pollInterval = setInterval(() => {
      if (!isPolling) {
        clearInterval(pollInterval);
        return;
      }

      fetchTaskStatus(taskId);
    }, interval);

    // Cleanup
    return () => {
      clearInterval(pollInterval);
      setIsPolling(false);
    };
  }, [taskId, interval, enabled, fetchTaskStatus, isPolling]);

  return {
    status,
    isPolling,
    refetch: taskId ? () => fetchTaskStatus(taskId) : null
  };
}
