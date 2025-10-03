import { Button } from '../ui/button';

interface WeekSelectorProps {
  week: number;
  season: number;
  onWeekChange: (week: number) => void;
}

export function WeekSelector({ week, season, onWeekChange }: WeekSelectorProps) {
  const handlePrevious = () => {
    if (week > 1) {
      onWeekChange(week - 1);
    }
  };

  const handleNext = () => {
    if (week < 18) {
      onWeekChange(week + 1);
    }
  };

  return (
    <div className="flex items-center justify-between bg-white border border-gray-200 rounded-xl p-6">
      <Button
        variant="outline"
        onClick={handlePrevious}
        disabled={week <= 1}
        className="px-6 font-bold"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        PREV WEEK
      </Button>

      <div className="text-center">
        <div className="text-4xl font-black tracking-tight">WEEK {week}</div>
        <div className="text-sm text-gray-500 uppercase tracking-wider font-semibold mt-1">
          {season} Season
        </div>
      </div>

      <Button
        variant="outline"
        onClick={handleNext}
        disabled={week >= 18}
        className="px-6 font-bold"
      >
        NEXT WEEK
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </Button>
    </div>
  );
}
