"""
Account Balances Tab - Display projected account balances and net worth
"""

import streamlit as st
from ui.components.charts import create_net_worth_chart
from ui.components.metrics import display_account_balance_metrics
from services.formatting_service import fmt_currency, style_negative_red, calculate_ages_for_year
from services.scenario_service import ScenarioCache


def render_account_balances_tab():
    """Render the account balances tab with charts and detailed data"""
    st.header("📈 Projected Account Balances")
    
    # Disclaimer
    st.error("""
    ⚠️ **DISCLAIMER**: Beta software - not financial advice. Verify all projections independently and consult financial professionals.
    """)
    
    st.info("📊 **Deterministic Projection:** These results assume you receive exactly your expected investment returns every year. This represents the 'smooth path' scenario. For risk analysis with market volatility, see the Monte Carlo tab.")
    
    if not st.session_state.projection_calculated:
        st.info("👈 Go to 'Scenario Setup' and click 'Calculate Projections'")
        return
    
    df = st.session_state.projection_df
    metrics = st.session_state.metrics
    retirement_ages = st.session_state.retirement_ages
    
    display_account_balance_metrics(df, metrics)
    
    st.divider()
    fig = create_net_worth_chart(df, retirement_ages)
    st.pyplot(fig)
    import matplotlib.pyplot as plt
    plt.close(fig)
    
    with st.expander("📋 Detailed Year-by-Year Data"):
        display_df = df.drop(columns=['age']).copy()
        current_year, _, _ = ScenarioCache.get_cached_scenario_params()
        display_df['ages'] = display_df['year'].apply(lambda year: calculate_ages_for_year(year, current_year))
        currency_columns = ['income', 'expenses', 'net_cashflow', 'real_estate_sales', 
                          'portfolio_contribution', 'portfolio_return_amount', 
                          'portfolio_balance', 'real_estate_equity', 'total_net_worth']
        
        for col in currency_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(fmt_currency)
        cols = list(display_df.columns)
        if 'ages' in cols:
            cols.remove('ages')
            cols.insert(2, 'ages')
            display_df = display_df[cols]
        styled_df = display_df.style.map(style_negative_red, 
                                         subset=['net_cashflow', 'portfolio_contribution'])
        st.dataframe(styled_df, width="stretch", height=400)