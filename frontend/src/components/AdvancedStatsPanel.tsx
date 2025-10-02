import React from 'react';
import { AdvancedPlayerStats, NextGenStatsQB, NextGenStatsReceiver, NextGenStatsRusher } from '../types/advancedStats';

interface AdvancedStatsPanelProps {
  stats: AdvancedPlayerStats | null;
  loading?: boolean;
}

export const AdvancedStatsPanel: React.FC<AdvancedStatsPanelProps> = ({ stats, loading }) => {
  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Advanced Stats</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Advanced Stats</h3>
        <p className="text-gray-500">No advanced stats available</p>
      </div>
    );
  }

  const { position } = stats;

  return (
    <div className="p-6 bg-white rounded-lg shadow space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Advanced Stats (Next Gen Stats)</h3>
        <span className="text-sm text-gray-500">
          {stats.season} {stats.week ? `Week ${stats.week}` : 'Season'}
        </span>
      </div>

      {/* QB Stats */}
      {position === 'QB' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {stats.cpoe !== undefined && (
              <StatCard
                label="CPOE"
                value={`${stats.cpoe > 0 ? '+' : ''}${stats.cpoe.toFixed(1)}%`}
                description="Completion % Over Expected"
                highlight={stats.cpoe > 3 ? 'positive' : stats.cpoe < -3 ? 'negative' : undefined}
              />
            )}
            {stats.epa_per_play !== undefined && (
              <StatCard
                label="EPA/Play"
                value={stats.epa_per_play.toFixed(2)}
                description="Expected Points Added per Play"
                highlight={stats.epa_per_play > 0.2 ? 'positive' : stats.epa_per_play < -0.1 ? 'negative' : undefined}
              />
            )}
            {stats.time_to_throw !== undefined && (
              <StatCard
                label="Time to Throw"
                value={`${stats.time_to_throw.toFixed(1)}s`}
                description="Average time from snap to release"
                highlight={stats.time_to_throw < 2.3 ? 'positive' : undefined}
              />
            )}
            {stats.avg_air_yards !== undefined && (
              <StatCard
                label="Avg Air Yards"
                value={stats.avg_air_yards.toFixed(1)}
                description="Average depth of target"
              />
            )}
          </div>

          {stats.success_rate !== undefined && (
            <div className="pt-4 border-t">
              <StatCard
                label="Success Rate"
                value={`${stats.success_rate.toFixed(1)}%`}
                description="% of plays with positive EPA"
                highlight={stats.success_rate > 50 ? 'positive' : undefined}
              />
            </div>
          )}
        </div>
      )}

      {/* WR/TE Stats */}
      {(position === 'WR' || position === 'TE') && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {stats.avg_separation !== undefined && (
              <StatCard
                label="Avg Separation"
                value={`${stats.avg_separation.toFixed(1)} yd`}
                description="Average yards from nearest defender"
                highlight={stats.avg_separation > 3.5 ? 'positive' : stats.avg_separation < 2.0 ? 'negative' : undefined}
              />
            )}
            {stats.avg_yac !== undefined && (
              <StatCard
                label="Avg YAC"
                value={`${stats.avg_yac.toFixed(1)} yd`}
                description="Yards After Catch per reception"
                highlight={stats.avg_yac > 6.0 ? 'positive' : undefined}
              />
            )}
            {stats.target_share !== undefined && (
              <StatCard
                label="Target Share"
                value={`${stats.target_share.toFixed(1)}%`}
                description="% of team's targets"
                highlight={stats.target_share > 25 ? 'positive' : stats.target_share < 12 ? 'negative' : undefined}
              />
            )}
            {stats.wopr !== undefined && (
              <StatCard
                label="WOPR"
                value={stats.wopr.toFixed(2)}
                description="Weighted Opportunity Rating"
                highlight={stats.wopr > 0.7 ? 'positive' : undefined}
              />
            )}
          </div>

          {stats.snap_share !== undefined && (
            <div className="pt-4 border-t">
              <StatCard
                label="Snap Share"
                value={`${stats.snap_share.toFixed(1)}%`}
                description="% of offensive snaps played"
                highlight={stats.snap_share > 80 ? 'positive' : stats.snap_share < 50 ? 'negative' : undefined}
              />
            </div>
          )}
        </div>
      )}

      {/* RB Stats */}
      {position === 'RB' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {stats.rush_yards_over_expected_per_att !== undefined && (
              <StatCard
                label="Yards Over Expected"
                value={`${stats.rush_yards_over_expected_per_att > 0 ? '+' : ''}${stats.rush_yards_over_expected_per_att.toFixed(1)} yd`}
                description="Per carry vs expected"
                highlight={stats.rush_yards_over_expected_per_att > 0.5 ? 'positive' : stats.rush_yards_over_expected_per_att < -0.3 ? 'negative' : undefined}
              />
            )}
            {stats.success_rate !== undefined && (
              <StatCard
                label="Success Rate"
                value={`${stats.success_rate.toFixed(1)}%`}
                description="% of carries with positive EPA"
                highlight={stats.success_rate > 50 ? 'positive' : undefined}
              />
            )}
            {stats.snap_share !== undefined && (
              <StatCard
                label="Snap Share"
                value={`${stats.snap_share.toFixed(1)}%`}
                description="% of offensive snaps"
                highlight={stats.snap_share > 70 ? 'positive' : stats.snap_share < 40 ? 'negative' : undefined}
              />
            )}
            {stats.epa_per_play !== undefined && (
              <StatCard
                label="EPA/Play"
                value={stats.epa_per_play.toFixed(2)}
                description="Expected Points Added per play"
                highlight={stats.epa_per_play > 0.15 ? 'positive' : undefined}
              />
            )}
          </div>
        </div>
      )}

      {/* EPA Summary (all positions) */}
      {stats.epa_total !== undefined && (
        <div className="pt-4 border-t">
          <div className="text-sm text-gray-600 mb-2">Total EPA This Season</div>
          <div className="text-2xl font-bold">
            {stats.epa_total > 0 ? '+' : ''}{stats.epa_total.toFixed(1)}
          </div>
        </div>
      )}

      <div className="pt-4 border-t text-xs text-gray-500">
        <p>Data provided by Next Gen Stats via Grid Iron Mind API v2</p>
      </div>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: string;
  description: string;
  highlight?: 'positive' | 'negative';
}

const StatCard: React.FC<StatCardProps> = ({ label, value, description, highlight }) => {
  const bgColor = highlight === 'positive'
    ? 'bg-green-50 border-green-200'
    : highlight === 'negative'
    ? 'bg-red-50 border-red-200'
    : 'bg-gray-50 border-gray-200';

  const valueColor = highlight === 'positive'
    ? 'text-green-700'
    : highlight === 'negative'
    ? 'text-red-700'
    : 'text-gray-900';

  return (
    <div className={`p-4 rounded-lg border ${bgColor}`}>
      <div className="text-xs font-medium text-gray-600 uppercase tracking-wide">{label}</div>
      <div className={`text-2xl font-bold ${valueColor} mt-1`}>{value}</div>
      <div className="text-xs text-gray-500 mt-1">{description}</div>
    </div>
  );
};

export default AdvancedStatsPanel;
