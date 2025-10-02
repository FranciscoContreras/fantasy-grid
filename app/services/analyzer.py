import numpy as np
from sklearn.preprocessing import StandardScaler

class PlayerAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()

    def calculate_matchup_score(self, player_stats, defense_stats):
        """
        Calculate matchup score (0-100) based on player stats vs defense
        Higher score = better matchup
        """
        matchup_factors = {
            'yards_allowed': defense_stats.get('yards_allowed', 0),
            'tds_allowed': defense_stats.get('tds_allowed', 0),
            'rank': defense_stats.get('rank', 16)
        }

        score = self._compute_score(matchup_factors)
        return min(100, max(0, score))

    def calculate_weather_impact(self, weather_data, player_position):
        """
        Calculate weather impact on player performance (0-100)
        100 = ideal conditions, 0 = worst conditions
        """
        if not weather_data:
            return 100

        wind_speed = weather_data.get('wind_speed', 0)
        precipitation = weather_data.get('precipitation', 0)
        temperature = weather_data.get('temperature', 70)

        impact_score = 100

        # QBs and WRs affected by wind
        if player_position in ['QB', 'WR']:
            if wind_speed > 15:
                impact_score -= (wind_speed - 15) * 2

        # All positions affected by heavy rain/snow
        if precipitation > 0.5:
            impact_score -= precipitation * 20

        # Extreme temperatures affect all players
        if temperature < 20 or temperature > 95:
            impact_score -= 10

        return max(0, min(100, impact_score))

    def _compute_score(self, factors):
        """Compute matchup score from defense factors"""
        rank = factors.get('rank', 16)

        # Higher rank (worse defense) = better matchup
        # Rank 1 (best defense) = lower score
        # Rank 32 (worst defense) = higher score
        base_score = ((32 - rank) / 32) * 100

        return round(base_score, 2)

    def calculate_advanced_matchup_score(self, player_position, player_advanced_stats, defense_advanced_stats):
        """
        Calculate enhanced matchup score using API v2 advanced stats.
        
        Args:
            player_position: QB, RB, WR, TE
            player_advanced_stats: Player's Next Gen Stats, EPA, etc.
            defense_advanced_stats: Defense's advanced metrics
        
        Returns:
            Enhanced matchup score (0-100) with detailed breakdown
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not player_advanced_stats or not defense_advanced_stats:
            # Fallback to basic calculation
            return {'score': 50, 'confidence': 'low', 'factors': []}
        
        matchup_score = 50  # Baseline
        factors = []
        
        # QB Matchup Analysis
        if player_position == 'QB':
            player_cpoe = player_advanced_stats.get('cpoe', 0)
            player_epa = player_advanced_stats.get('epa_per_play', 0)
            def_pressure_rate = defense_advanced_stats.get('pressure_rate', 30)
            def_passer_rating_allowed = defense_advanced_stats.get('passer_rating_allowed', 95)
            def_completion_pct_allowed = defense_advanced_stats.get('completion_pct_allowed', 65)
            
            # QB excels in accuracy vs soft coverage
            if player_cpoe and player_cpoe > 2.0 and def_completion_pct_allowed > 67:
                matchup_score += 15
                factors.append(f"Accuracy advantage vs soft coverage (CPOE: +{player_cpoe:.1f}%)")
            
            # EPA efficiency vs defense allowing big plays
            if player_epa and player_epa > 0.15 and def_passer_rating_allowed > 100:
                matchup_score += 12
                factors.append(f"Efficiency edge vs vulnerable defense (EPA: {player_epa:.2f})")
            
            # Pressure concerns
            if def_pressure_rate > 35:
                matchup_score -= 10
                factors.append(f"Heavy pressure expected ({def_pressure_rate:.1f}% pressure rate)")
            elif def_pressure_rate < 25:
                matchup_score += 8
                factors.append(f"Clean pocket likely ({def_pressure_rate:.1f}% pressure rate)")
        
        # WR/TE Matchup Analysis
        elif player_position in ['WR', 'TE']:
            player_separation = player_advanced_stats.get('avg_separation', 0)
            player_target_share = player_advanced_stats.get('target_share', 0)
            player_yac = player_advanced_stats.get('avg_yac', 0)
            def_completion_allowed = defense_advanced_stats.get('completion_pct_allowed', 65)
            def_yards_per_att_allowed = defense_advanced_stats.get('yards_per_attempt_allowed', 7.0)
            
            # Route running vs coverage
            if player_separation and player_separation > 3.5 and def_completion_allowed > 67:
                matchup_score += 18
                factors.append(f"Route running mismatch ({player_separation:.1f} yd separation vs soft coverage)")
            
            # Target volume with favorable defense
            if player_target_share and player_target_share > 23 and def_yards_per_att_allowed > 7.5:
                matchup_score += 14
                factors.append(f"High volume vs generous defense ({player_target_share:.1f}% targets)")
            
            # YAC ability vs defense allowing yards
            if player_yac and player_yac > 5.5 and def_yards_per_att_allowed > 7.2:
                matchup_score += 10
                factors.append(f"YAC potential vs vulnerable coverage ({player_yac:.1f} YAC)")
        
        # RB Matchup Analysis
        elif player_position == 'RB':
            player_yards_over_exp = player_advanced_stats.get('rush_yards_over_expected_per_att', 0)
            player_success_rate = player_advanced_stats.get('success_rate', 0)
            player_snap_share = player_advanced_stats.get('snap_share', 0)
            def_stuff_rate = defense_advanced_stats.get('stuff_rate', 20)
            def_rush_epa_allowed = defense_advanced_stats.get('epa_per_play_allowed', 0)
            def_explosive_rate = defense_advanced_stats.get('explosive_play_rate_allowed', 15)
            
            # Vision/elusiveness vs run defense
            if player_yards_over_exp and player_yards_over_exp > 0.4 and def_stuff_rate < 20:
                matchup_score += 16
                factors.append(f"Elite vision vs soft front ({player_yards_over_exp:.1f}+ yd over expected)")
            
            # Workload with favorable defense
            if player_snap_share and player_snap_share > 65 and def_rush_epa_allowed > -0.05:
                matchup_score += 13
                factors.append(f"Workhorse role vs vulnerable run D ({player_snap_share:.1f}% snaps)")
            
            # Big play potential
            if player_success_rate and player_success_rate > 48 and def_explosive_rate > 16:
                matchup_score += 11
                factors.append(f"Explosive play potential ({player_success_rate:.1f}% success vs {def_explosive_rate:.1f}% allowed)")
            
            # Tough matchup
            if def_stuff_rate > 24:
                matchup_score -= 12
                factors.append(f"Stout run defense ({def_stuff_rate:.1f}% stuff rate)")
        
        # Cap score at 0-100
        matchup_score = max(0, min(100, matchup_score))
        
        # Determine confidence based on data quality
        confidence = 'high' if len(factors) >= 2 else 'medium' if len(factors) == 1 else 'low'
        
        logger.info(f"{player_position} advanced matchup score: {matchup_score:.1f} ({confidence} confidence)")
        
        return {
            'score': round(matchup_score, 1),
            'confidence': confidence,
            'factors': factors,
            'advanced_analysis': True
        }
    
    def analyze_player_trends(self, advanced_stats_history):
        """
        Analyze player performance trends using advanced stats over time.
        
        Args:
            advanced_stats_history: List of advanced stats dicts from recent games/weeks
        
        Returns:
            Trend analysis with momentum indicators
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not advanced_stats_history or len(advanced_stats_history) < 3:
            return {'trend': 'unknown', 'momentum': 'neutral', 'insights': []}
        
        insights = []
        
        # Extract key metrics over time
        epa_values = [s.get('epa_per_play', 0) for s in advanced_stats_history if s.get('epa_per_play')]
        success_rates = [s.get('success_rate', 0) for s in advanced_stats_history if s.get('success_rate')]
        snap_shares = [s.get('snap_share', 0) for s in advanced_stats_history if s.get('snap_share')]
        
        # EPA Trend
        if len(epa_values) >= 3:
            recent_epa = np.mean(epa_values[-3:])
            earlier_epa = np.mean(epa_values[:-3]) if len(epa_values) > 3 else np.mean(epa_values)
            
            if recent_epa > earlier_epa + 0.05:
                insights.append(f"EPA trending up (recent: {recent_epa:.2f} vs earlier: {earlier_epa:.2f})")
                trend = 'improving'
            elif recent_epa < earlier_epa - 0.05:
                insights.append(f"EPA trending down (recent: {recent_epa:.2f} vs earlier: {earlier_epa:.2f})")
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        # Success Rate Trend
        if len(success_rates) >= 3:
            recent_success = np.mean(success_rates[-3:])
            if recent_success > 48:
                insights.append(f"Highly efficient recently ({recent_success:.1f}% success rate)")
            elif recent_success < 40:
                insights.append(f"Struggling with efficiency ({recent_success:.1f}% success rate)")
        
        # Snap Share Trend (workload)
        if len(snap_shares) >= 3:
            recent_snaps = np.mean(snap_shares[-3:])
            earlier_snaps = np.mean(snap_shares[:-3]) if len(snap_shares) > 3 else np.mean(snap_shares)
            
            if recent_snaps > earlier_snaps + 5:
                insights.append(f"Increasing workload (snaps: {recent_snaps:.1f}% vs {earlier_snaps:.1f}%)")
            elif recent_snaps < earlier_snaps - 5:
                insights.append(f"Decreasing workload (snaps: {recent_snaps:.1f}% vs {earlier_snaps:.1f}%)")
        
        # Overall momentum
        if trend == 'improving' and len(insights) >= 2:
            momentum = 'hot'
        elif trend == 'declining':
            momentum = 'cold'
        else:
            momentum = 'neutral'
        
        logger.info(f"Player trends: {trend} trend, {momentum} momentum, {len(insights)} insights")
        
        return {
            'trend': trend,
            'momentum': momentum,
            'insights': insights
        }
    
    def calculate_injury_risk_impact(self, injury_data):
        """
        Assess injury risk and performance impact using API v2 injury data.
        
        Args:
            injury_data: Enhanced injury report from API v2
        
        Returns:
            Risk assessment and projected impact on performance
        """
        if not injury_data or not isinstance(injury_data, list) or len(injury_data) == 0:
            return {'risk': 'none', 'impact': 0, 'status': 'healthy', 'details': []}
        
        current_injury = injury_data[0]  # Most recent injury
        status = current_injury.get('injury_status', '').upper()
        injury_type = current_injury.get('injury_type', 'Unknown')
        weeks_out = current_injury.get('weeks_out', 0)
        
        risk_level = 'none'
        impact_score = 0  # 0-100, higher = worse impact
        details = []
        
        # Status-based assessment
        if status == 'OUT' or status == 'IR':
            risk_level = 'extreme'
            impact_score = 100
            details.append(f"Player OUT - {injury_type}")
        elif status == 'DOUBTFUL':
            risk_level = 'high'
            impact_score = 80
            details.append(f"Doubtful to play - {injury_type}")
        elif status == 'QUESTIONABLE':
            risk_level = 'moderate'
            impact_score = 40
            details.append(f"Questionable - {injury_type}")
        elif status == 'PROBABLE':
            risk_level = 'low'
            impact_score = 15
            details.append(f"Probable to play - {injury_type}")
        
        # Injury type severity
        high_risk_injuries = ['ACL', 'Achilles', 'Concussion', 'Hamstring']
        if any(injury in injury_type for injury in high_risk_injuries):
            details.append(f"High-risk injury type: {injury_type}")
            if impact_score < 50:
                impact_score += 20
        
        # Practice participation
        practice_status = []
        if current_injury.get('wednesday_practice'):
            practice_status.append(f"Wed: {current_injury['wednesday_practice']}")
        if current_injury.get('thursday_practice'):
            practice_status.append(f"Thu: {current_injury['thursday_practice']}")
        if current_injury.get('friday_practice'):
            practice_status.append(f"Fri: {current_injury['friday_practice']}")
        
        if practice_status:
            details.append(f"Practice: {', '.join(practice_status)}")
        
        # Expected return timeline
        if weeks_out and weeks_out > 0:
            details.append(f"Expected out {weeks_out} week(s)")
        
        return {
            'risk': risk_level,
            'impact': min(100, impact_score),
            'status': status,
            'injury_type': injury_type,
            'details': details
        }
