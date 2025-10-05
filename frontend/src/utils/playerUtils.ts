// Centralized player utilities for ESPN images and team logos

// ESPN player image helper function with fallback
export const getPlayerImage = (playerId: string | number): string => {
  return `https://a.espncdn.com/i/headshots/nfl/players/full/${playerId}.png`;
};

// Player initials fallback for when images fail
export const getPlayerInitials = (name: string): string => {
  return name.split(' ').map(n => n[0]).join('');
};

// Team logo helper function with comprehensive team mapping
export const getTeamLogo = (teamAbbr: string): string => {
  const teamMap: { [key: string]: string } = {
    // AFC East
    'BUF': 'buf',
    'MIA': 'mia',
    'NE': 'ne',
    'NYJ': 'nyj',

    // AFC North
    'BAL': 'bal',
    'CIN': 'cin',
    'CLE': 'cle',
    'PIT': 'pit',

    // AFC South
    'HOU': 'hou',
    'IND': 'ind',
    'JAX': 'jax',
    'TEN': 'ten',

    // AFC West
    'DEN': 'den',
    'KC': 'kc',
    'LV': 'lv',
    'LAC': 'lac',

    // NFC East
    'DAL': 'dal',
    'NYG': 'nyg',
    'PHI': 'phi',
    'WAS': 'wsh',

    // NFC North
    'CHI': 'chi',
    'DET': 'det',
    'GB': 'gb',
    'MIN': 'min',

    // NFC South
    'ATL': 'atl',
    'CAR': 'car',
    'NO': 'no',
    'TB': 'tb',

    // NFC West
    'ARI': 'ari',
    'LAR': 'lar',
    'SF': 'sf',
    'SEA': 'sea'
  };

  return `https://a.espncdn.com/i/teamlogos/nfl/500/${teamMap[teamAbbr] || teamAbbr.toLowerCase()}.png`;
};

// Team colors for fallback initials
export const getTeamColor = (teamAbbr: string): string => {
  const teamColors: { [key: string]: string } = {
    // AFC East
    'BUF': '#00338D',
    'MIA': '#008E97',
    'NE': '#002244',
    'NYJ': '#125740',

    // AFC North
    'BAL': '#241773',
    'CIN': '#FB4F14',
    'CLE': '#311D00',
    'PIT': '#FFB612',

    // AFC South
    'HOU': '#03202F',
    'IND': '#002C5F',
    'JAX': '#9F792C',
    'TEN': '#0C2340',

    // AFC West
    'DEN': '#FB4F14',
    'KC': '#E31837',
    'LV': '#000000',
    'LAC': '#0080C6',

    // NFC East
    'DAL': '#003594',
    'NYG': '#0B2265',
    'PHI': '#004C54',
    'WAS': '#5A1414',

    // NFC North
    'CHI': '#0B162A',
    'DET': '#0076B6',
    'GB': '#203731',
    'MIN': '#4F2683',

    // NFC South
    'ATL': '#A71930',
    'CAR': '#0085CA',
    'NO': '#D3BC8D',
    'TB': '#D50A0A',

    // NFC West
    'ARI': '#97233F',
    'LAR': '#003594',
    'SF': '#AA0000',
    'SEA': '#002244'
  };

  return teamColors[teamAbbr] || '#6B7280'; // Gray fallback
};

// Position color coding
export const getPositionColor = (position: string): string => {
  const positionColors: { [key: string]: string } = {
    'QB': '#3B82F6', // Blue
    'RB': '#10B981', // Green
    'WR': '#F59E0B', // Yellow/Orange
    'TE': '#EF4444', // Red
    'K': '#8B5CF6',  // Purple
    'DEF': '#6B7280' // Gray
  };

  return positionColors[position] || '#6B7280';
};

// Common ESPN player IDs for popular players (for reference/testing)
export const VERIFIED_ESPN_IDS: { [key: string]: string } = {
  'Josh Allen': '3918298',
  'Saquon Barkley': '3929630',
  'Tyreek Hill': '3116406',
  'Justin Jefferson': '4262921',
  'Mike Evans': '16737',
  'Caleb Williams': '4431611',
  'Patrick Mahomes': '3139477',
  'Lamar Jackson': '3916387',
  'Josh Jacobs': '4035687',
  'Cooper Kupp': '3116593',
  'Travis Kelce': '15847',
  'Davante Adams': '2976499'
};

// React component helpers for consistent image rendering
export interface PlayerImageProps {
  playerId: string | number;
  playerName: string;
  teamAbbr?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export const getPlayerImageSizeClasses = (size: 'sm' | 'md' | 'lg' | 'xl' = 'md'): string => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20'
  };

  return sizeClasses[size];
};

// Error handling for image loading
export const handleImageError = (
  event: React.SyntheticEvent<HTMLImageElement>,
  fallbackElement?: HTMLElement | null
): void => {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';

  if (fallbackElement) {
    fallbackElement.style.display = 'flex';
  } else {
    // Try to find the next sibling as fallback
    const fallback = target.nextElementSibling as HTMLElement;
    if (fallback) {
      fallback.style.display = 'flex';
    }
  }
};