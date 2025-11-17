"""
Scenario management and caching service.
Handles caching of expensive calculations to avoid redundant work.
"""

import streamlit as st
from .formatting_service import calculate_auto_scenario_params


class ScenarioCache:
    """Manages cached scenario calculations"""
    
    @staticmethod
    def get_cached_scenario_params():
        """Get cached scenario parameters or calculate and cache them"""
        cache_key = '_cached_scenario_params'
        
        current_data_hash = ScenarioCache._get_data_hash()
        cached_hash = st.session_state.get('_data_hash')
        
        if (cache_key not in st.session_state or 
            cached_hash != current_data_hash):
            st.session_state[cache_key] = calculate_auto_scenario_params()
            st.session_state['_data_hash'] = current_data_hash
        
        return st.session_state[cache_key]
    
    @staticmethod
    def _get_data_hash():
        """Generate a simple hash of the data to detect changes"""
        income_hash = len(st.session_state.income_df) if hasattr(st.session_state, 'income_df') else 0
        expenses_hash = len(st.session_state.expenses_df) if hasattr(st.session_state, 'expenses_df') else 0
        people_hash = len(st.session_state.people_df) if hasattr(st.session_state, 'people_df') else 0
        
        return hash((income_hash, expenses_hash, people_hash))
    
    @staticmethod
    def clear_cache():
        """Clear cached scenario parameters (call when data changes)"""
        keys_to_remove = ['_cached_scenario_params', '_data_hash']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]