"""
ProjectionCache - Caches expensive calculations during projections to avoid redundant work.
Especially useful for real estate calculations that are called multiple times per year.
"""

from models.real_estate_v2 import calculate_real_estate_impact_v2 as calculate_real_estate_impact


class ProjectionCache:
    """Manages caching of expensive calculations during projections"""
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        """Clear all cached data"""
        self._people_ages = {}
        self._re_impact = {}
        self._current_year = None
    
    def get_person_age(self, person_name, year, people_data, current_year):
        """Get cached person age or calculate and cache it"""
        cache_key = f"{person_name}_{year}"
        
        if cache_key not in self._people_ages:
            person = next((p for p in people_data if p['name'] == person_name), None)
            if person:
                age = person['current_age'] + (year - current_year)
            else:
                age = None
            self._people_ages[cache_key] = age
        
        return self._people_ages[cache_key]
    
    def get_real_estate_impact(self, properties, current_year, age, year):
        """Get cached real estate impact or calculate and cache it"""
        cache_key = f"re_{year}"
        
        if cache_key not in self._re_impact:
            impact = calculate_real_estate_impact(properties, current_year, age, year)
            self._re_impact[cache_key] = impact
        
        return self._re_impact[cache_key]


_projection_cache = ProjectionCache()


def get_projection_cache():
    """Get the global projection cache instance"""
    return _projection_cache


def clear_projection_cache():
    """Clear the global projection cache"""
    _projection_cache.clear()