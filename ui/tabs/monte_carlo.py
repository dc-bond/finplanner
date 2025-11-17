"""
Monte Carlo Tab - Stochastic financial simulation with risk analysis
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from models.monte_carlo import run_monte_carlo_analysis
from services.scenario_manager import ScenarioManager


def plot_monte_carlo_fan_chart(percentiles_df):
    """Create a fan chart showing confidence bands for portfolio balance over time"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#bf616a', '#d08770', '#ebcb8b', '#a3be8c', '#88c0d0', '#81a1c1', '#5e81ac']
    alpha_levels = [0.1, 0.15, 0.2, 0.3, 0.2, 0.15, 0.1]
    
    ages = percentiles_df['age']
    band_pairs = [
        ('p5', 'p95', colors[0], alpha_levels[0], '90% Confidence'),
        ('p10', 'p90', colors[1], alpha_levels[1], '80% Confidence'), 
        ('p25', 'p75', colors[2], alpha_levels[2], '50% Confidence')
    ]
    
    for lower, upper, color, alpha, label in band_pairs:
        ax.fill_between(ages, percentiles_df[lower], percentiles_df[upper], 
                       color=color, alpha=alpha, label=label)
    ax.plot(ages, percentiles_df['p50'], color='#2e3440', linewidth=3, 
            label='Median Outcome', zorder=10)
    ax.plot(ages, percentiles_df['mean'], color='#4c566a', linewidth=2, 
            linestyle='--', label='Mean Outcome', zorder=10)
    ax.axhline(y=0, color='#bf616a', linestyle='-', alpha=0.7, linewidth=1)
    
    ax.set_xlabel('Age', fontsize=12)
    ax.set_ylabel('Portfolio Balance ($)', fontsize=12)
    ax.set_title('Monte Carlo Portfolio Projections\nConfidence Bands', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    return fig


def plot_success_probability_chart(summary_stats):
    """Create charts showing success probability and failure analysis"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    success_rate = summary_stats['success_rate']
    failure_rate = 1 - success_rate
    
    sizes = [success_rate, failure_rate]
    labels = [f'Success\n{success_rate:.1%}', f'Failure\n{failure_rate:.1%}']
    colors = ['#a3be8c', '#bf616a']
    explode = (0.05, 0)
    
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='',
            shadow=True, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax1.set_title('Portfolio Success Rate\n(Money Never Runs Out)', fontsize=14, fontweight='bold')
    depletion_analysis = summary_stats['depletion_analysis']
    if depletion_analysis['depletion_rate'] > 0:
        median_age_text = f"{depletion_analysis['median_depletion_age']:.0f}" if depletion_analysis['median_depletion_age'] else 'N/A'
        earliest_age_text = f"{depletion_analysis['earliest_depletion']:.0f}" if depletion_analysis['earliest_depletion'] else 'N/A'
        
        ax2.text(0.5, 0.5, f"Portfolio Depletion Analysis\n\n" +
                f"Failure Rate: {depletion_analysis['depletion_rate']:.1%}\n" +
                f"Median Depletion Age: {median_age_text}\n" +
                f"Earliest Depletion: {earliest_age_text}",
                ha='center', va='center', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#d8dee9', alpha=0.8))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('Failure Analysis', fontsize=14, fontweight='bold')
    else:
        ax2.text(0.5, 0.5, "No Portfolio Failures\nDetected in Simulation", 
                ha='center', va='center', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#a3be8c', alpha=0.8))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('Failure Analysis', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_final_balance_distribution(summary_stats):
    """Create histogram of final portfolio balance distribution"""
    
    final_stats = summary_stats['final_balance_stats']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    mean = final_stats['mean']
    std = final_stats['std']
    x_vals = np.linspace(final_stats['min'], final_stats['max'], 100)
    y_vals = np.exp(-0.5 * ((x_vals - mean) / std) ** 2) / (std * np.sqrt(2 * np.pi))
    
    ax.fill_between(x_vals, y_vals, alpha=0.6, color='#81a1c1', label='Distribution')
    percentiles = [final_stats['p5'], final_stats['median'], final_stats['p95']]
    percentile_labels = ['5th Percentile', 'Median', '95th Percentile']
    colors = ['#bf616a', '#4c566a', '#a3be8c']
    
    for p, label, color in zip(percentiles, percentile_labels, colors):
        ax.axvline(p, color=color, linestyle='--', linewidth=2, 
                  label=f'{label}: ${p:,.0f}')
    
    ax.set_xlabel('Final Portfolio Balance ($)', fontsize=12)
    ax.set_ylabel('Probability Density', fontsize=12)
    ax.set_title('Distribution of Final Portfolio Balance', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    return fig


def render_monte_carlo_tab():
    """Render the monte carlo simulation tab"""
    st.header("🎲 Monte Carlo Simulation")
    st.markdown("Run thousands of simulations to understand the probability distribution of your financial outcomes.")
    
    # Disclaimer
    st.error("""
    ⚠️ **DISCLAIMER**: Beta software - not financial advice. Monte Carlo simulations are educational models only. 
    Verify all calculations and consult financial professionals before making decisions.
    """)
    
    st.info("🎯 **Probabilistic Analysis:** Unlike the deterministic projections on the other tabs, Monte Carlo simulation shows the range of possible outcomes when markets experience realistic ups and downs. This reveals the true risk in your financial plan.")
    
    with st.expander("🎛️ Simulation Settings", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            num_sims = st.selectbox(
                "Number of Simulations",
                options=[100, 500, 1000, 2500, 5000, 10000],
                index=2,  # Default to 1000
                help="More simulations provide better accuracy but take longer to run"
            )
        
        with col2:
            st.markdown("**Asset Correlations:**")
            st.write("• Accounts use realistic correlations")
            st.write("• Based on historical market data")
        
        with col3:
            st.markdown("**Visualization Shows:**")
            st.write("• 50% Confidence Band (25th-75th percentile)")
            st.write("• 80% Confidence Band (10th-90th percentile)") 
            st.write("• 90% Confidence Band (5th-95th percentile)")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_simulation = st.button(
            "🚀 Run Monte Carlo Simulation",
            type="primary",
            help="This may take 30-60 seconds depending on number of simulations.",
            width='stretch'
        )
    
    if not st.session_state.get('projection_calculated', False):
        st.warning("⚠️ Please configure and calculate your scenario in the 'Scenario Setup' tab first.")
        return
    
    if run_simulation:
        with st.spinner(f"Running {num_sims:,} Monte Carlo simulations..."):
            try:
                scenario = ScenarioManager.build_scenario_from_session_state()
                st.session_state.monte_carlo.update({
                    'num_simulations': num_sims
                })
                mc_results = run_monte_carlo_analysis(scenario, num_sims)
                st.session_state.monte_carlo_results = mc_results
                st.session_state.monte_carlo['results_calculated'] = True
                
                st.success(f"✅ Completed {num_sims:,} simulations successfully!")
                
            except Exception as e:
                st.error(f"❌ Error running Monte Carlo simulation: {str(e)}")
                return
    if st.session_state.get('monte_carlo', {}).get('results_calculated', False):
        mc_results = st.session_state.get('monte_carlo_results', {})
        
        if mc_results:
            summary_stats = mc_results['summary_stats']
            
            st.subheader("📊 Key Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                success_rate = summary_stats['success_rate']
                status_icon = "✅" if success_rate >= 0.9 else "⚠️" if success_rate >= 0.7 else "❌"
                st.metric(
                    "Success Rate",
                    f"{status_icon} {success_rate:.1%}",
                    help="Probability that portfolio never runs out of money"
                )
            
            with col2:
                median_final = summary_stats['final_balance_stats']['median']
                st.metric(
                    "Median Final Balance",
                    f"${median_final:,.0f}",
                    help="50th percentile of final portfolio balance"
                )
            
            with col3:
                p5_final = summary_stats['final_balance_stats']['p5']
                st.metric(
                    "5th Percentile Final",
                    f"${p5_final:,.0f}", 
                    help="Worst-case scenario (5% chance of doing worse)"
                )
            
            with col4:
                depletion_rate = summary_stats['depletion_analysis']['depletion_rate']
                st.metric(
                    "Depletion Risk",
                    f"{'❌' if depletion_rate > 0 else '✅'} {depletion_rate:.1%}",
                    help="Probability that portfolio runs out of money before you up and die."
                )
            viz_tabs = st.tabs([
                "📈 Portfolio Projections", 
                "📊 Final Balance Distribution"
            ])
            
            with viz_tabs[0]:
                st.subheader("Portfolio Balance Over Time")
                st.markdown("Confidence bands showing the range of possible outcomes:")
                
                try:
                    fan_chart = plot_monte_carlo_fan_chart(summary_stats['percentiles_by_age'])
                    st.pyplot(fan_chart)
                    plt.close()
                except Exception as e:
                    st.error(f"Error creating fan chart: {str(e)}")
                with st.expander("📋 View Percentile Data"):
                    percentiles_display = summary_stats['percentiles_by_age'].copy()
                    money_cols = ['p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'mean']
                    for col in money_cols:
                        percentiles_display[col] = percentiles_display[col].apply(lambda x: f"${x:,.0f}")
                    st.dataframe(percentiles_display, width='stretch')
            
            with viz_tabs[1]:
                st.subheader("Final Balance Distribution")
                st.markdown("Distribution of portfolio values at the end of the projection period:")
                
                try:
                    dist_chart = plot_final_balance_distribution(summary_stats)
                    st.pyplot(dist_chart)
                    plt.close()
                except Exception as e:
                    st.error(f"Error creating distribution chart: {str(e)}")
                st.markdown("### 📈 Statistical Summary")
                final_stats = summary_stats['final_balance_stats']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Central Tendencies:**")
                    st.write(f"• Mean: ${final_stats['mean']:,.0f}")
                    st.write(f"• Median: ${final_stats['median']:,.0f}")
                    st.write(f"• Std Dev: ${final_stats['std']:,.0f}")
                
                with col2:
                    st.markdown("**Range:**")
                    st.write(f"• Minimum: ${final_stats['min']:,.0f}")
                    st.write(f"• Maximum: ${final_stats['max']:,.0f}")
                    st.write(f"• Range: ${(final_stats['max']-final_stats['min']):,.0f}")
                
                with col3:
                    st.markdown("**Percentiles:**")
                    st.write(f"• 5th: ${final_stats['p5']:,.0f}")
                    st.write(f"• 95th: ${final_stats['p95']:,.0f}")
                    st.write(f"• IQR: ${(final_stats['p95']-final_stats['p5']):,.0f}")
            
    else:
        st.info("👆 Configure your simulation settings above and click 'Run Simulation' to see your results.")
        
        st.subheader("🎲 What Monte Carlo Analysis Provides")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Probabilistic Outcomes:**
            • Success rate (probability plan works)
            • Confidence intervals for portfolio balance
            • Risk of running out of money
            • Best/worst case scenarios
            """)
            
        with col2:
            st.markdown("""
            **Advanced Analysis:**
            • Asset correlation effects
            • Sequence of returns risk
            • Market volatility impact
            • Statistical distribution of outcomes
            """)