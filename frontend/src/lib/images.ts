/**
 * Utility functions for getting team logos and player images from ESPN CDN
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

  // ESPN uses specific team abbreviations
  const espnTeamMap: Record<string, string> = {
    'JAX': 'jac',  // Jacksonville uses 'jac' in ESPN
    'LAR': 'lar',
    'LAC': 'lac',
    'WSH': 'wsh',
    'KC': 'kc',
  };

  const espnAbbr = espnTeamMap[teamAbbr] || teamAbbr.toLowerCase();

  return `${ESPN_CDN_BASE}/teamlogos/nfl/500/${espnAbbr}.png`;
}

/**
 * Get player headshot URL from ESPN CDN
 * @param espnPlayerId - ESPN player ID
 * @param size - Image size (default 'headshot')
 */
export function getPlayerImageUrl(espnPlayerId: string | number | null | undefined): string {
  if (!espnPlayerId) {
    // Return a default avatar
    return 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
  }

  return `${ESPN_CDN_BASE}/headshots/nfl/players/full/${espnPlayerId}.png`;
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
