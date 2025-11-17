"""
Formatting and utility functions for the financial planning app.
Extracted from app.py for better organization and reusability.
"""

import pandas as pd
from datetime import datetime
import streamlit as st


def fmt_currency(value):
    """Format number as USD with commas, no decimals"""
    if pd.isna(value):
        return "-"
    return f"${value:,.0f}"


def fmt_percent(value):
    """Format decimal as percentage"""
    if pd.isna(value):
        return "-"
    return f"{value*100:.1f}%"


def style_negative_red(val):
    """Apply red color to negative currency values"""
    if isinstance(val, str) and '$-' in val:
        return 'color: red'
    return ''


def calculate_ages_for_year(year, current_year=None):
    """Calculate ages for all people in a given year"""
    if current_year is None:
        current_year = datetime.now().year
    
    ages = []
    for _, person in st.session_state.people_df.iterrows():
        if pd.notna(person['current_age']) and person['current_age'] > 0:
            age_in_year = person['current_age'] + (year - current_year)
            name = person['name'].strip() if person['name'].strip() else person['person_id']
            ages.append(f"{age_in_year}")
    
    return "/".join(ages) if ages else ""


def calculate_auto_scenario_params():
    """Auto-calculate current year, current age, and max projection age from data"""
    current_year = datetime.now().year
    
    min_start_age = float('inf')
    for income in st.session_state.income_df.to_dict('records'):
        if pd.notna(income.get('start_age')):
            min_start_age = min(min_start_age, income['start_age'])
    
    current_age = int(min_start_age) if min_start_age != float('inf') else 35
    
    max_age = 65
    
    for income in st.session_state.income_df.to_dict('records'):
        if pd.notna(income.get('end_age')):
            max_age = max(max_age, income['end_age'])
        if income.get('type') == 'Retirement' and pd.notna(income.get('start_age')):
            max_age = max(max_age, income['start_age'] + 30)
    
    for expense in st.session_state.expenses_df.to_dict('records'):
        if expense.get('type') == 'Recurring' and pd.notna(expense.get('end_age')):
            max_age = max(max_age, expense['end_age'])
        elif expense.get('type') == 'Planned':
            if pd.notna(expense.get('year')) and pd.notna(expense.get('repeat_until_year')):
                years_from_now = expense['repeat_until_year'] - current_year
                projected_age = current_age + years_from_now
                max_age = max(max_age, projected_age)
            elif pd.notna(expense.get('year')):
                years_from_now = expense['year'] - current_year
                projected_age = current_age + years_from_now
                max_age = max(max_age, projected_age)
    
    max_projection_age = min(max(max_age, 95), 120)
    
    return current_year, current_age, max_projection_age


def convert_percentages_to_decimals(data_list, percentage_fields):
    """Convert percentage fields from 0-100 format to 0-1 decimal format"""
    converted_data = []
    for item in data_list:
        item_converted = item.copy()
        for field in percentage_fields:
            if field in item_converted and pd.notna(item_converted[field]):
                item_converted[field] = item_converted[field] / 100
        converted_data.append(item_converted)
    return converted_data