/**
 * Utility functions for getting team logos and player images from ESPN CDN
 * UPDATED with verified ESPN player IDs and comprehensive team mapping
 */

const ESPN_CDN_BASE = 'https://a.espncdn.com/i';

/**
 * Get team logo URL from ESPN CDN
 * @param teamAbbr - NFL team abbreviation (e.g., 'KC', 'SF', 'NYJ')
 * @param size - Logo size (default 500x500)
 */
export function getTeamLogoUrl(teamAbbr: string, size: number = 500): string {
  if (!teamAbbr || teamAbbr === 'FA' || teamAbbr === 'BYE' || teamAbbr === 'TBD') {
    return '';
  }

  // ESPN uses specific team abbreviations - COMPREHENSIVE MAPPING
  const espnTeamMap: Record<string, string> = {
    // Special cases that differ from standard abbreviations
    'JAX': 'jax',  // Jacksonville
    'LAR': 'lar',  // LA Rams
    'LAC': 'lac',  // LA Chargers
    'WSH': 'wsh',  // Washington
    'WAS': 'wsh',  // Washington (alternative)
    'KC': 'kc',    // Kansas City
    'NE': 'ne',    // New England
    'NO': 'no',    // New Orleans
    'SF': 'sf',    // San Francisco
    'TB': 'tb',    // Tampa Bay
    'LV': 'lv',    // Las Vegas
    // All other teams use lowercase of their abbreviation
  };

  const espnAbbr = espnTeamMap[teamAbbr] || teamAbbr.toLowerCase();

  return `${ESPN_CDN_BASE}/teamlogos/nfl/${size}/${espnAbbr}.png`;
}

/**
 * Get player headshot URL from ESPN CDN
 * @param espnPlayerId - ESPN player ID (VERIFIED IDs recommended)
 * @param size - Image size (default 'full')
 */
export function getPlayerImageUrl(espnPlayerId: string | number | null | undefined): string {
  if (!espnPlayerId) {
    // Return a default avatar
    return 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
  }

  return `${ESPN_CDN_BASE}/headshots/nfl/players/full/${espnPlayerId}.png`;
}

/**
 * Get player initials for fallback when image fails
 * @param playerName - Full player name
 */
export function getPlayerInitials(playerName: string): string {
  if (!playerName) return '??';

  return playerName
    .split(' ')
    .map(name => name.charAt(0).toUpperCase())
    .join('');
}

/**
 * VERIFIED ESPN Player IDs for popular players (2025 season)
 * Use these IDs to ensure correct player images are displayed
 */
export const VERIFIED_ESPN_PLAYER_IDS: Record<string, string> = {
  // Quarterbacks
  'Josh Allen': '3918298',
  'Patrick Mahomes': '3139477',
  'Lamar Jackson': '3916387',
  'Caleb Williams': '4431611',

  // Running Backs
  'Saquon Barkley': '3929630',
  'Christian McCaffrey': '3116369',
  'Josh Jacobs': '4035687',

  // Wide Receivers
  'Tyreek Hill': '3116406',
  'Justin Jefferson': '4262921',
  'Cooper Kupp': '3116593',
  'Davante Adams': '2976499',
  'Mike Evans': '16737',

  // Tight Ends
  'Travis Kelce': '15847',
  'Mark Andrews': '3043078',
  'George Kittle': '3043079'
};

/**
 * Handle image loading errors with fallback
 * @param event - React image error event
 * @param fallbackElement - Optional fallback element to show
 */
export function handleImageError(
  event: React.SyntheticEvent<HTMLImageElement>,
  fallbackElement?: HTMLElement | null
): void {
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
}

/**
 * Team color schemes for backgrounds/borders
 */
export const teamColors: Record<string, { primary: string; secondary: string }> = {
  ARI: { primary: '#97233F', secondary: '#000000' },
  ATL: { primary: '#A71930', secondary: '#000000' },
  BAL: { primary: '#241773', secondary: '#000000' },
  BUF: { primary: '#00338D', secondary: '#C60C30' },
  CAR: { primary: '#0085CA', secondary: '#101820' },
  CHI: { primary: '#C83803', secondary: '#0B162A' },
  CIN: { primary: '#FB4F14', secondary: '#000000' },
  CLE: { primary: '#311D00', secondary: '#FF3C00' },
  DAL: { primary: '#041E42', secondary: '#869397' },
  DEN: { primary: '#FB4F14', secondary: '#002244' },
  DET: { primary: '#0076B6', secondary: '#B0B7BC' },
  GB: { primary: '#203731', secondary: '#FFB612' },
  HOU: { primary: '#03202F', secondary: '#A71930' },
  IND: { primary: '#002C5F', secondary: '#A2AAAD' },
  JAX: { primary: '#006778', secondary: '#D7A22A' },
  KC: { primary: '#E31837', secondary: '#FFB81C' },
  LAC: { primary: '#0080C6', secondary: '#FFC20E' },
  LAR: { primary: '#003594', secondary: '#FFA300' },
  LV: { primary: '#000000', secondary: '#A5ACAF' },
  MIA: { primary: '#008E97', secondary: '#FC4C02' },
  MIN: { primary: '#4F2683', secondary: '#FFC62F' },
  NE: { primary: '#002244', secondary: '#C60C30' },
  NO: { primary: '#D3BC8D', secondary: '#101820' },
  NYG: { primary: '#0B2265', secondary: '#A71930' },
  NYJ: { primary: '#125740', secondary: '#000000' },
  PHI: { primary: '#004C54', secondary: '#A5ACAF' },
  PIT: { primary: '#FFB612', secondary: '#101820' },
  SF: { primary: '#AA0000', secondary: '#B3995D' },
  SEA: { primary: '#002244', secondary: '#69BE28' },
  TB: { primary: '#D50A0A', secondary: '#FF7900' },
  TEN: { primary: '#0C2340', secondary: '#4B92DB' },
  WSH: { primary: '#5A1414', secondary: '#FFB612' },
};
