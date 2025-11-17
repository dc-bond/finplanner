"""
Cash Flow Tab - Display annual cash flow analysis
"""

import streamlit as st
from ui.components.charts import create_cash_flow_charts
from ui.components.metrics import display_cash_flow_metrics
from services.formatting_service import fmt_currency, style_negative_red, calculate_ages_for_year
from services.scenario_service import ScenarioCache


def render_cash_flow_tab():
    """Render the cash flow tab with charts and detailed data"""
    st.header("💰 Annual Cash Flow")
    
    # Disclaimer
    st.error("""
    ⚠️ **DISCLAIMER**: Beta software - not financial advice. Verify all projections independently and consult financial professionals.
    """)
    
    st.info("📊 **Deterministic Projection:** This shows your cash flow assuming steady, predictable investment returns. Real markets have ups and downs - use the Monte Carlo tab to see how market volatility might affect your plan.")
    
    if not st.session_state.projection_calculated:
        st.info("👈 Go to 'Scenario Setup' and click 'Calculate Projections'")
        return
    
    df = st.session_state.projection_df
    retirement_ages = st.session_state.retirement_ages
    
    display_cash_flow_metrics(df)
    
    st.divider()
    fig = create_cash_flow_charts(df, retirement_ages)
    st.pyplot(fig)
    import matplotlib.pyplot as plt
    plt.close(fig)
    
    with st.expander("📋 Detailed Year-by-Year Cash Flow"):
        display_df = df[['year', 'income', 'expenses', 'net_cashflow', 'real_estate_sales']].copy()
        current_year, _, _ = ScenarioCache.get_cached_scenario_params()
        display_df['ages'] = display_df['year'].apply(lambda year: calculate_ages_for_year(year, current_year))
        currency_columns = ['income', 'expenses', 'net_cashflow', 'real_estate_sales']
        for col in currency_columns:
            display_df[col] = display_df[col].apply(fmt_currency)
        cols = list(display_df.columns)
        if 'ages' in cols:
            cols.remove('ages')
            cols.insert(2, 'ages')
            display_df = display_df[cols]
        styled_df = display_df.style.map(style_negative_red, subset=['net_cashflow'])
        st.dataframe(styled_df, width="stretch", height=400)