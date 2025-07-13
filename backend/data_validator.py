import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
from models.data_models import Match

class DataValidator:
    """Validates and cross-checks match data from multiple sources"""
    
    def __init__(self):
        self.validation_rules = {
            'min_sources_required': 2,  # At least 2 sources must confirm the match
            'max_date_difference': 1,   # Max 1 day difference between sources
            'required_fields': ['home_team', 'away_team', 'date', 'status'],
            'valid_statuses': ['scheduled', 'not_started', 'live'],
            'excluded_statuses': ['postponed', 'cancelled', 'abandoned', 'finished']
        }
    
    def validate_matches(self, matches_data: Dict) -> Dict:
        """Validate and cross-check matches from multiple sources"""
        logger.info("Starting match validation and cross-checking")
        
        # Group matches by unique identifier
        grouped_matches = self._group_matches_by_id(matches_data['matches'])
        
        # Validate each group
        validated_matches = []
        validation_errors = []
        
        for match_id, sources in grouped_matches.items():
            try:
                validation_result = self._validate_match_group(match_id, sources)
                if validation_result['is_valid']:
                    validated_matches.append(validation_result['best_match'])
                else:
                    validation_errors.append({
                        'match_id': match_id,
                        'errors': validation_result['errors'],
                        'sources': list(sources.keys())
                    })
            except Exception as e:
                logger.error(f"Error validating match group {match_id}: {e}")
                validation_errors.append({
                    'match_id': match_id,
                    'errors': [str(e)],
                    'sources': list(sources.keys()) if 'sources' in locals() else []
                })
        
        logger.info(f"Validation complete: {len(validated_matches)} valid matches, {len(validation_errors)} errors")
        
        return {
            'valid_matches': validated_matches,
            'validation_errors': validation_errors,
            'validation_summary': {
                'total_matches': len(matches_data['matches']),
                'valid_matches': len(validated_matches),
                'invalid_matches': len(validation_errors),
                'validation_rate': len(validated_matches) / len(matches_data['matches']) if matches_data['matches'] else 0
            }
        }
    
    def _group_matches_by_id(self, matches: List[Dict]) -> Dict[str, Dict]:
        """Group matches by a unique identifier based on teams and date"""
        grouped = {}
        
        for match in matches:
            # Create a unique ID based on teams and date
            home_team = match.get('home_team', '').lower().strip()
            away_team = match.get('away_team', '').lower().strip()
            date = match.get('date', '')
            
            if home_team and away_team and date:
                # Normalize team names
                home_team = self._normalize_team_name(home_team)
                away_team = self._normalize_team_name(away_team)
                
                # Create unique ID
                unique_id = f"{home_team}_{away_team}_{date[:10]}"  # Use date part only
                
                if unique_id not in grouped:
                    grouped[unique_id] = {}
                
                source = match.get('source', 'unknown')
                grouped[unique_id][source] = match
        
        return grouped
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names for comparison"""
        # Remove common suffixes and prefixes
        normalized = team_name.lower()
        
        # Remove common words
        common_words = ['fc', 'cf', 'cd', 'real', 'atletico', 'atletico', 'deportivo', 'united', 'city']
        for word in common_words:
            normalized = normalized.replace(word, '').strip()
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _validate_match_group(self, match_id: str, sources: Dict) -> Dict:
        """Validate a group of matches from different sources"""
        errors = []
        
        # Check minimum sources requirement
        if len(sources) < self.validation_rules['min_sources_required']:
            errors.append(f"Insufficient sources: {len(sources)} < {self.validation_rules['min_sources_required']}")
        
        # Check required fields
        for source_name, match_data in sources.items():
            for field in self.validation_rules['required_fields']:
                if field not in match_data or not match_data[field]:
                    errors.append(f"Missing required field '{field}' in source '{source_name}'")
        
        # Check status validity
        valid_matches = []
        for source_name, match_data in sources.items():
            status = match_data.get('status', '').lower()
            if status in self.validation_rules['excluded_statuses']:
                errors.append(f"Match excluded due to status '{status}' in source '{source_name}'")
            elif status in self.validation_rules['valid_statuses']:
                valid_matches.append((source_name, match_data))
        
        if not valid_matches:
            errors.append("No valid match status found across sources")
        
        # Check date consistency
        if len(valid_matches) > 1:
            dates = []
            for source_name, match_data in valid_matches:
                try:
                    date_str = match_data['date']
                    if 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    match_date = datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append((source_name, match_date))
                except Exception as e:
                    errors.append(f"Invalid date format in source '{source_name}': {e}")
            
            # Check date differences
            if len(dates) > 1:
                for i in range(len(dates)):
                    for j in range(i + 1, len(dates)):
                        date_diff = abs((dates[i][1] - dates[j][1]).days)
                        if date_diff > self.validation_rules['max_date_difference']:
                            errors.append(f"Date mismatch between '{dates[i][0]}' and '{dates[j][0]}': {date_diff} days")
        
        # Check team name consistency
        if len(valid_matches) > 1:
            home_teams = set()
            away_teams = set()
            
            for source_name, match_data in valid_matches:
                home_teams.add(self._normalize_team_name(match_data['home_team']))
                away_teams.add(self._normalize_team_name(match_data['away_team']))
            
            if len(home_teams) > 1:
                errors.append(f"Home team name inconsistency: {home_teams}")
            if len(away_teams) > 1:
                errors.append(f"Away team name inconsistency: {away_teams}")
        
        # Determine if match is valid
        is_valid = len(errors) == 0
        
        # Select best match data (prioritize official sources)
        best_match = None
        if is_valid and valid_matches:
            # Prioritize official sources
            source_priority = {
                'laliga_official': 1,
                'promiedos': 2,
                'flashscore': 3,
                'sofascore': 4,
                'betsapi': 5
            }
            
            best_source = min(valid_matches, key=lambda x: source_priority.get(x[0], 999))
            best_match = best_source[1]
            
            # Add validation metadata
            best_match['validation_metadata'] = {
                'sources_confirmed': list(sources.keys()),
                'validation_timestamp': datetime.now().isoformat(),
                'confidence_score': self._calculate_confidence_score(sources)
            }
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'best_match': best_match,
            'sources_count': len(sources)
        }
    
    def _calculate_confidence_score(self, sources: Dict) -> float:
        """Calculate confidence score based on sources and their reliability"""
        source_weights = {
            'laliga_official': 1.0,    # Official source - highest weight
            'promiedos': 0.9,          # Reliable Spanish football coverage
            'flashscore': 0.8,         # Well-established
            'sofascore': 0.8,          # Well-established
            'betsapi': 0.7,            # Good but less reliable
            'whoscored': 0.7,
            'transfermarkt': 0.6
        }
        
        total_weight = 0
        for source_name in sources.keys():
            total_weight += source_weights.get(source_name, 0.5)
        
        # Normalize by number of sources
        confidence = total_weight / len(sources) if sources else 0
        
        # Boost confidence for multiple sources
        if len(sources) >= 3:
            confidence *= 1.2
        elif len(sources) >= 2:
            confidence *= 1.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def filter_matches_for_predictions(self, validated_matches: List[Dict]) -> List[Dict]:
        """Filter matches that are suitable for predictions"""
        suitable_matches = []
        
        for match in validated_matches:
            try:
                # Check if match is in the future
                match_date = datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
                now = datetime.now()
                
                # Only include matches in the next 7 days
                if match_date > now and (match_date - now).days <= 7:
                    # Check if match is scheduled
                    status = match.get('status', '').lower()
                    if status in ['scheduled', 'not_started']:
                        # Check confidence score
                        confidence = match.get('validation_metadata', {}).get('confidence_score', 0)
                        if confidence >= 0.7:  # Minimum confidence threshold
                            suitable_matches.append(match)
                
            except Exception as e:
                logger.error(f"Error filtering match {match.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Found {len(suitable_matches)} matches suitable for predictions")
        return suitable_matches
    
    def generate_validation_report(self, validation_result: Dict) -> str:
        """Generate a human-readable validation report"""
        report = []
        report.append("=== MATCH DATA VALIDATION REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        summary = validation_result['validation_summary']
        report.append(f"Total matches processed: {summary['total_matches']}")
        report.append(f"Valid matches: {summary['valid_matches']}")
        report.append(f"Invalid matches: {summary['invalid_matches']}")
        report.append(f"Validation rate: {summary['validation_rate']:.2%}")
        report.append("")
        
        if validation_result['validation_errors']:
            report.append("=== VALIDATION ERRORS ===")
            for error in validation_result['validation_errors'][:10]:  # Show first 10 errors
                report.append(f"Match ID: {error['match_id']}")
                report.append(f"Sources: {', '.join(error['sources'])}")
                report.append(f"Errors: {', '.join(error['errors'])}")
                report.append("")
        
        return "\n".join(report) 