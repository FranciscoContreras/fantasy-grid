/**
 * Real-time task status indicator
 * Shows live progress of background Celery tasks
 */
import { useTaskPolling } from '@/hooks/useTaskPolling';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

interface TaskStatusProps {
  taskId: string | null;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

export function TaskStatus({ taskId, onComplete, onError }: TaskStatusProps) {
  const { status, isPolling } = useTaskPolling({
    taskId,
    interval: 2000,
    enabled: !!taskId,
    onSuccess: onComplete,
    onError
  });

  if (!taskId || !status) {
    return null;
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'SUCCESS':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'FAILURE':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'STARTED':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'PENDING':
        return <Clock className="h-5 w-5 text-gray-400" />;
      case 'RETRY':
        return <Loader2 className="h-5 w-5 text-orange-500 animate-spin" />;
      default:
        return <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />;
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'SUCCESS':
        return 'Analysis complete';
      case 'FAILURE':
        return 'Analysis failed';
      case 'STARTED':
        return 'Analyzing players...';
      case 'PENDING':
        return 'Queued for analysis...';
      case 'RETRY':
        return 'Retrying analysis...';
      default:
        return 'Processing...';
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'SUCCESS':
        return 'bg-green-50 border-green-200 text-green-900';
      case 'FAILURE':
        return 'bg-red-50 border-red-200 text-red-900';
      case 'STARTED':
      case 'RETRY':
        return 'bg-blue-50 border-blue-200 text-blue-900';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-900';
    }
  };

  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${getStatusColor()}`}>
      {getStatusIcon()}
      <div className="flex-1">
        <p className="text-sm font-medium">{getStatusText()}</p>
        {status.error && (
          <p className="text-xs mt-1 text-red-600">{status.error}</p>
        )}
      </div>
      {isPolling && (
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
          <span className="text-xs text-gray-500">Live</span>
        </div>
      )}
    </div>
  );
}
