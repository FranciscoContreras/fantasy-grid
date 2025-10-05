import React from 'react';
import {
  getPlayerImage,
  getPlayerInitials,
  getTeamColor,
  getPlayerImageSizeClasses,
  handleImageError,
  type PlayerImageProps
} from '../../utils/playerUtils';

interface ExtendedPlayerImageProps extends PlayerImageProps {
  showFallback?: boolean;
  borderColor?: string;
}

export function PlayerImage({
  playerId,
  playerName,
  teamAbbr,
  size = 'md',
  className = '',
  showFallback = true,
  borderColor
}: ExtendedPlayerImageProps) {
  const sizeClasses = getPlayerImageSizeClasses(size);
  const teamColor = teamAbbr ? getTeamColor(teamAbbr) : '#6B7280';
  const border = borderColor || 'border-white';

  return (
    <div className={`relative ${className}`}>
      <img
        src={getPlayerImage(playerId)}
        alt={playerName}
        className={`${sizeClasses} rounded-full object-cover border-2 ${border} shadow-md`}
        onError={(e) => handleImageError(e)}
      />
      {showFallback && (
        <div
          className={`${sizeClasses} rounded-full flex items-center justify-center text-white font-bold text-sm border-2 ${border} shadow-md absolute top-0 left-0`}
          style={{ backgroundColor: teamColor, display: 'none' }}
        >
          {getPlayerInitials(playerName)}
        </div>
      )}
    </div>
  );
}

// Alternative compact version for lists/tables
export function PlayerImageCompact({
  playerId,
  playerName,
  teamAbbr,
  className = ''
}: Omit<PlayerImageProps, 'size'>) {
  return (
    <PlayerImage
      playerId={playerId}
      playerName={playerName}
      teamAbbr={teamAbbr}
      size="sm"
      className={className}
    />
  );
}

// Large version for detail views
export function PlayerImageLarge({
  playerId,
  playerName,
  teamAbbr,
  className = ''
}: Omit<PlayerImageProps, 'size'>) {
  return (
    <PlayerImage
      playerId={playerId}
      playerName={playerName}
      teamAbbr={teamAbbr}
      size="xl"
      className={className}
    />
  );
}