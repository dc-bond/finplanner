"""
Scenario Setup Tab - Form interface for configuring financial scenarios
"""

import streamlit as st
from ui.components.data_editors import (
    create_people_editor, create_accounts_editor, create_real_estate_editor,
    create_income_editor, create_expenses_editor
)
from services.scenario_service import ScenarioCache
from services.validation_service import DataValidator


def render_scenario_setup_tab(run_projection_callback):
    """Render the scenario setup tab with all input forms"""
    st.header("Build Your Financial Scenario")
    
    # Disclaimer
    st.error("""
    ⚠️ **IMPORTANT DISCLAIMER**: This software is in beta and should not be relied upon as financial advice. 
    Verify all calculations independently and consult with qualified financial professionals before making any financial decisions. 
    Use at your own risk.
    """)
    
    st.subheader("👥 People")
    people_edited = create_people_editor(st.session_state.people_df)
    if not people_edited.equals(st.session_state.people_df):
        st.session_state.people_df = people_edited
        st.rerun()
    
    st.divider()
    
    with st.form("scenario_form", clear_on_submit=False):        
        st.subheader("💼 Current Account Balances")
        st.info("""
        📊 **Account Balance Table Strategy Guide:**

        As people get older, they typically shift their investments from higher-risk, higher-return options toward safer, lower-return options to protect what they've accumulated.

        Fill in an agressive and conservative growth rate for each account and use the transition ages to control when this shift happens — the account will gradually move from the agressive rate to the conservative rate between these two ages. If you want an account to keep the same growth rate throughout life, set the agressive and conservative rates to the same value.

        **Examples:**
        • **Account A**: Agressive 10%, Conservative 5%, Transition ages 45-65
        • **Account B**: Agressive 7%, Conservative 4%, Transition ages 55-67
        • **Account C**: Agressive 3%, Conservative 3%, Transition ages [don't matter because the account keeps a fixed rate]
        """)
        
        accounts_edited = create_accounts_editor(st.session_state.accounts_df)
        
        st.divider()
        
        # Real Estate
        st.subheader("🏠 Real Estate Properties")
        st.info("💡 **Future Purchases:** Leave 'Current Value' and 'Current Mortgage Balance' as None and 'Existing Property' unchecked. **Note:** Don't forget to add annual home ownership expenses in the expense table below for each property (e.g. maintenance, property taxes, insurance, etc.). You can also add rental income in the income table if applicable.")
        
        real_estate_edited = create_real_estate_editor(st.session_state.real_estate_df)
        
        st.divider()
        
        st.subheader("💵 All Income Sources")
        income_edited = create_income_editor(st.session_state.income_df)
        
        st.divider()
        
        st.subheader("💳 All Expenses")
        expenses_edited = create_expenses_editor(st.session_state.expenses_df)
        
        st.divider()
        
        submitted = st.form_submit_button(
            "🔄 Calculate Projections", 
            type="primary", 
            width='stretch'
        )
    if submitted:
        is_valid, validation_errors = DataValidator.validate_all_data(
            st.session_state.people_df, accounts_edited, real_estate_edited, 
            income_edited, expenses_edited, 
            {}
        )
        
        if not is_valid:
            st.error("Please fix the following validation errors:")
            for error in validation_errors:
                st.error(f"❌ {error}")
            return
        
        ScenarioCache.clear_cache()
        st.session_state.accounts_df = accounts_edited
        st.session_state.real_estate_df = real_estate_edited
        st.session_state.income_df = income_edited
        st.session_state.expenses_df = expenses_edited
        if run_projection_callback():
            st.success("✅ Projections calculated! View results on other tabs.")
            st.rerun()