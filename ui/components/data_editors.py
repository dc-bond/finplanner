"""
Data editor components for the financial planning application.
Reusable data editors with consistent configurations.
"""

import streamlit as st


def get_people_options():
    """Get the list of people names plus 'Joint' for dropdown options"""
    people_names = []
    if 'people_df' in st.session_state and not st.session_state.people_df.empty:
        people_names = []
        for name in st.session_state.people_df['name'].tolist():
            if name is not None and str(name).strip():
                clean_name = str(name).strip()
                if clean_name not in people_names:
                    people_names.append(clean_name)
    
    if 'Joint' not in people_names:
        people_names.append('Joint')
    
    return people_names


def create_people_editor(people_df):
    """Create the people data editor"""
    return st.data_editor(
        people_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "name": st.column_config.TextColumn("Name", help="Enter the person's name"),
            "current_age": st.column_config.NumberColumn("Current Age", min_value=0, max_value=120, step=1),
        }
    )


def create_accounts_editor(accounts_df):
    """Create the accounts data editor"""
    people_options = get_people_options()
    
    return st.data_editor(
        accounts_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "account_type": st.column_config.TextColumn("Account Type", required=True),
            "account_owner": st.column_config.SelectboxColumn("Account Owner ▼", 
                options=people_options),
            "current_balance": st.column_config.NumberColumn("Current Balance", format="dollar", step=1),
            "aggressive_rate": st.column_config.NumberColumn("Aggressive Growth Rate %", format="%.1f%%", 
                help="Growth rate when account owner is younger (e.g., 8.0 = 8%)"),
            "conservative_rate": st.column_config.NumberColumn("Conservative Growth Rate %", format="%.1f%%",
                help="Growth rate when account owner is older (e.g., 4.0 = 4%)"),
            "transition_start_age": st.column_config.NumberColumn("Transition Start Age", 
                help="Account owner's age when account starts transitioning from agressive to conservative growth rate"),
            "transition_end_age": st.column_config.NumberColumn("Transition End Age",
                help="Account owner's age when account has fully transitioned to conservative growth rate"),
        }
    )


def create_real_estate_editor(real_estate_df):
    """Create the real estate data editor"""
    return st.data_editor(
        real_estate_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "property_name": st.column_config.TextColumn("Property Name", required=True),
            "address": st.column_config.TextColumn("Address/Description"),
            "purchase_year": st.column_config.NumberColumn("Purchase Year", format="%d", step=1),
            "purchase_price": st.column_config.NumberColumn("Purchase Price", format="dollar", step=1000),
            "down_payment_percent": st.column_config.NumberColumn("Down Payment %", format="%.1f%%", step=1.0, help="e.g. 20 for 20%"),
            "mortgage_rate": st.column_config.NumberColumn("Mortgage Rate %", format="%.1f%%", help="e.g. 2.8 for 2.8%"),
            "mortgage_term_years": st.column_config.NumberColumn("Mortgage Term (Years)", step=1),
            "appreciation_rate": st.column_config.NumberColumn("Appreciation Rate %", format="%.1f%%", help="e.g. 3.5 for 3.5%"),
            "sale_year": st.column_config.NumberColumn("Sale Year (optional)", format="%d", step=1),
            "current_value": st.column_config.NumberColumn("Current Value", format="dollar", step=1000, help="Current market value (for existing properties)"),
            "current_mortgage_balance": st.column_config.NumberColumn("Current Mortgage Balance", format="dollar", step=1, help="Current outstanding balance (for existing properties)"),
            "is_existing_property": st.column_config.CheckboxColumn("Existing Property?", help="Check if already owned, uncheck for future purchase"),
        }
    )


def create_income_editor(income_df):
    """Create the income data editor"""
    people_options = get_people_options()
    
    return st.data_editor(
        income_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "name": st.column_config.TextColumn("Income Name", required=True),
            "person": st.column_config.SelectboxColumn("Person ▼", 
                options=people_options),
            "annual_amount": st.column_config.NumberColumn("Annual Amount", format="dollar", step=1),
            "start_age": st.column_config.NumberColumn("Start Age"),
            "end_age": st.column_config.NumberColumn("End Age"),
            "growth_rate": st.column_config.NumberColumn("Growth Rate %", format="%.1f%%", help="e.g., 3.0 = 3% for salary growth, 2.0 = 2% for COLA"),
        }
    )


def create_expenses_editor(expenses_df):
    """Create the expenses data editor"""
    people_options = get_people_options()
    
    return st.data_editor(
        expenses_df,
        width="stretch",
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Expense Name", required=True),
            "person": st.column_config.SelectboxColumn("Person ▼", 
                options=people_options),
            "annual_amount": st.column_config.NumberColumn("Annual Amount", format="dollar", step=1),
            "start_age": st.column_config.NumberColumn("Start Age"),
            "end_age": st.column_config.NumberColumn("End Age"),
            "growth_rate": st.column_config.NumberColumn("Growth Rate %", format="%.1f%%", help="Annual inflation rate"),
        }
    )