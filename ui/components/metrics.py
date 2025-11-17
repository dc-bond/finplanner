"""
Metrics display components for the financial planning application.
Reusable metric displays with consistent formatting.
"""

import streamlit as st
from services.formatting_service import fmt_currency


def display_account_balance_metrics(df, metrics):
    """Display the metrics for account balances tab"""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Starting Net Worth", fmt_currency(df.iloc[0]['total_net_worth']))
    col2.metric("Final Net Worth", fmt_currency(df.iloc[-1]['total_net_worth']))
    col3.metric("Portfolio Depletes", 
               f"Age {metrics['first_deficit_age']:.0f}" if metrics['first_deficit_age'] else "Never ✅")
    col4.metric("Investment Gains", fmt_currency(metrics['total_investment_gains']))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Contributions", fmt_currency(metrics['total_contributions']))
    col2.metric("Total Withdrawals", fmt_currency(metrics['total_withdrawals']))


def display_cash_flow_metrics(df):
    """Display the metrics for cash flow tab"""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Surplus", fmt_currency(df[df['net_cashflow'] > 0]['net_cashflow'].sum()))
    col2.metric("Total Deficit", fmt_currency(abs(df[df['net_cashflow'] < 0]['net_cashflow'].sum())))
    col3.metric("Peak Income", fmt_currency(df['income'].max()))
    col4.metric("Peak Expenses", fmt_currency(df['expenses'].max()))
    
    if df['real_estate_sales'].sum() > 0:
        col1, col2 = st.columns(2)
        col1.metric("Real Estate Sales", fmt_currency(df['real_estate_sales'].sum()))
        col2.metric("Peak RE Equity", fmt_currency(df['real_estate_equity'].max()))