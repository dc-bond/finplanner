"""
ScenarioManager - Centralized data transformation and scenario building logic.
Handles conversion from UI session state to projection scenario format.
"""

import streamlit as st
from .formatting_service import convert_percentages_to_decimals
from .scenario_service import ScenarioCache


class ScenarioManager:
    """Manages scenario data transformation and building"""
    
    @staticmethod
    def build_scenario_from_session_state():
        """Build a complete scenario dictionary from Streamlit session state"""
        try:
            current_year, current_age, max_projection_age = ScenarioCache.get_cached_scenario_params()
            
            scenario = {
                'current_year': current_year,
                'current_age': current_age,
                'max_projection_age': max_projection_age,
            }
            
            scenario['account_details'] = ScenarioManager._convert_account_data()
            
            income_sources, retirement_income = ScenarioManager._convert_income_data()
            scenario['income_sources'] = income_sources
            scenario['retirement_income'] = retirement_income
            
            scenario['recurring_expenses'] = ScenarioManager._convert_expense_data()
            scenario['planned_expenses'] = []
            
            scenario['people'] = st.session_state.people_df.to_dict('records')
            
            scenario['real_estate'] = ScenarioManager._convert_real_estate_data()
            
            return scenario
            
        except Exception as e:
            raise Exception(f"Error building scenario: {str(e)}")
    
    @staticmethod
    def _convert_account_data():
        """Convert account DataFrame to scenario format keeping percentages"""
        return st.session_state.accounts_df.to_dict('records')
    
    @staticmethod
    def _convert_income_data():
        """Convert income DataFrame and split into working vs retirement income"""
        all_income = st.session_state.income_df.to_dict('records')
        
        income_sources = [inc for inc in all_income if inc['end_age'] <= 67]
        retirement_income = [inc for inc in all_income if inc['start_age'] >= 65]
        
        return income_sources, retirement_income
    
    @staticmethod
    def _convert_expense_data():
        """Convert expense DataFrame to scenario format keeping percentages"""
        return st.session_state.expenses_df.to_dict('records')
    
    @staticmethod
    def _convert_real_estate_data():
        """Convert real estate DataFrame to scenario format keeping percentages"""
        return st.session_state.real_estate_df.to_dict('records')