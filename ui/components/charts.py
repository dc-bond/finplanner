"""
Chart components for the financial planning application.
Reusable chart generation functions with consistent styling.
"""

import matplotlib.pyplot as plt
import streamlit as st

NORD_COLORS = {
    'polar_night': ['#2e3440', '#3b4252', '#434c5e', '#4c566a'],
    'snow_storm': ['#d8dee9', '#e5e9f0', '#eceff4'],
    'frost': ['#8fbcbb', '#88c0d0', '#81a1c1', '#5e81ac'],
    'aurora': ['#bf616a', '#d08770', '#ebcb8b', '#a3be8c', '#b48ead']
}

plt.style.use('dark_background')
plt.rcParams.update({
    'figure.facecolor': NORD_COLORS['polar_night'][0],
    'axes.facecolor': NORD_COLORS['polar_night'][1],
    'axes.edgecolor': NORD_COLORS['polar_night'][3],
    'axes.labelcolor': NORD_COLORS['snow_storm'][2],
    'text.color': NORD_COLORS['snow_storm'][2],
    'xtick.color': NORD_COLORS['snow_storm'][1],
    'ytick.color': NORD_COLORS['snow_storm'][1],
    'grid.color': NORD_COLORS['polar_night'][3],
    'grid.alpha': 0.3
})


def create_net_worth_chart(df, retirement_ages):
    """Create the net worth projection chart with portfolio and real estate breakdown"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.fill_between(df['age'], 0, df['portfolio_balance'], alpha=0.7, color=NORD_COLORS['frost'][2], label='Investment Portfolio')
    ax.fill_between(df['age'], df['portfolio_balance'], df['total_net_worth'], alpha=0.7, color=NORD_COLORS['aurora'][4], label='Real Estate Equity')
    ax.plot(df['age'], df['portfolio_balance'], linewidth=2.5, color=NORD_COLORS['frost'][1])
    ax.plot(df['age'], df['total_net_worth'], linewidth=2.5, color=NORD_COLORS['aurora'][3])
    for ret in retirement_ages:
        ax.axvline(x=ret['retirement_age'], color=NORD_COLORS['aurora'][0], linestyle='--', alpha=0.8, linewidth=2)
        ax.text(ret['retirement_age'], ax.get_ylim()[1] * 0.95, 
               f"{ret['person']}\nRetires", 
               ha='center', fontsize=9, color=NORD_COLORS['snow_storm'][2],
               bbox=dict(boxstyle='round', facecolor=NORD_COLORS['polar_night'][2], alpha=0.8, edgecolor=NORD_COLORS['aurora'][0]))
    
    ax.set_xlabel('Age', fontweight='bold')
    ax.set_ylabel('Net Worth', fontweight='bold')
    ax.set_title('Net Worth Projection (Portfolio + Real Estate)', fontweight='bold', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, p: f'${x:,.0f}'
    ))
    
    plt.tight_layout()
    return fig


def create_cash_flow_charts(df, retirement_ages):
    """Create the dual cash flow charts (income vs expenses, net cash flow)"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    ax1.plot(df['age'], df['income'], label='Income', linewidth=2.5, color=NORD_COLORS['aurora'][3])
    ax1.plot(df['age'], df['expenses'], label='Expenses', linewidth=2.5, color=NORD_COLORS['aurora'][0])
    ax1.fill_between(df['age'], df['income'], df['expenses'], 
                     where=(df['income'] >= df['expenses']), alpha=0.4, color=NORD_COLORS['aurora'][3])
    ax1.fill_between(df['age'], df['income'], df['expenses'], 
                     where=(df['income'] < df['expenses']), alpha=0.4, color=NORD_COLORS['aurora'][0])
    for ret in retirement_ages:
        ax1.axvline(x=ret['retirement_age'], color=NORD_COLORS['aurora'][4], linestyle='--', alpha=0.8, linewidth=2)
    
    ax1.set_ylabel('Amount', fontweight='bold')
    ax1.set_title('Income vs Expenses', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    colors = [NORD_COLORS['aurora'][3] if x >= 0 else NORD_COLORS['aurora'][0] for x in df['net_cashflow']]
    ax2.bar(df['age'], df['net_cashflow'], color=colors, alpha=0.7, edgecolor=NORD_COLORS['polar_night'][3], linewidth=0.5)
    ax2.axhline(y=0, color=NORD_COLORS['snow_storm'][1], linestyle='-', linewidth=1.5, alpha=0.8)
    for ret in retirement_ages:
        ax2.axvline(x=ret['retirement_age'], color=NORD_COLORS['aurora'][4], linestyle='--', alpha=0.8, linewidth=2)
    
    ax2.set_xlabel('Age', fontweight='bold')
    ax2.set_ylabel('Net Cash Flow', fontweight='bold')
    ax2.set_title('Net Cash Flow', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    return fig