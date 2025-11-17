import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from models.projection import project_scenario, calculate_success_metrics, get_retirement_ages
from models.real_estate_v2 import calculate_real_estate_impact_v2 as calculate_real_estate_impact
from services.scenario_manager import ScenarioManager
from services.validation_service import DataValidator
from ui.tabs.scenario_setup import render_scenario_setup_tab
from ui.tabs.account_balances import render_account_balances_tab
from ui.tabs.cash_flow import render_cash_flow_tab
from ui.tabs.monte_carlo import render_monte_carlo_tab

st.set_page_config(
    page_title="Financial Planning Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
.stDeployButton {display:none;}
.stAppDeployButton {display:none;}
header[data-testid="stHeader"] {display:none;}
.viewerBadge_container__1QSob {display:none;}
footer {visibility: hidden;}
#stDecoration {display:none;}
button[kind="header"] {display:none;}
.css-18e3th9 {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("""
<style>
    /* Import Nord colors as CSS variables for consistency */
    :root {
        --nord0: #2e3440;
        --nord1: #3b4252;
        --nord2: #434c5e;
        --nord3: #4c566a;
        --nord4: #d8dee9;
        --nord5: #e5e9f0;
        --nord6: #eceff4;
        --nord7: #8fbcbb;
        --nord8: #88c0d0;
        --nord9: #81a1c1;
        --nord10: #5e81ac;
        --nord11: #bf616a;
        --nord12: #d08770;
        --nord13: #ebcb8b;
        --nord14: #a3be8c;
        --nord15: #b48ead;
    }
    
    /* Enhanced tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--nord1);
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: var(--nord4);
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--nord2);
        color: var(--nord6);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--nord9) !important;
        color: var(--nord0) !important;
        font-weight: 600;
    }
    
    /* Enhanced metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, var(--nord1) 0%, var(--nord2) 100%);
        border: 1px solid var(--nord3);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    /* Success/positive metrics */
    [data-testid="metric-container"] [data-testid="metric-value"]:contains("✅") {
        color: var(--nord14) !important;
    }
    
    /* Warning metrics */
    [data-testid="metric-container"] [data-testid="metric-value"]:contains("⚠") {
        color: var(--nord13) !important;
    }
    
    /* Error/negative metrics */
    [data-testid="metric-container"] [data-testid="metric-value"]:contains("❌") {
        color: var(--nord11) !important;
    }
    
    /* Enhanced data editor styling */
    .stDataFrame {
        border: 1px solid var(--nord3);
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Form containers */
    .stForm {
        background-color: var(--nord1);
        border: 1px solid var(--nord3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Button enhancements */
    .stButton > button {
        background: linear-gradient(135deg, var(--nord9) 0%, var(--nord10) 100%);
        border: none;
        border-radius: 8px;
        color: var(--nord0);
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--nord8) 0%, var(--nord9) 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    /* Success button (form submit) */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--nord14) 0%, var(--nord7) 100%);
        color: var(--nord0);
        font-weight: 600;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background-color: var(--nord1);
        border-right: 1px solid var(--nord3);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--nord2);
        border-radius: 8px;
        border: 1px solid var(--nord3);
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--nord9);
    }
    
    /* Success alerts */
    .stSuccess {
        background-color: rgba(163, 190, 140, 0.1);
        border-left-color: var(--nord14);
    }
    
    /* Warning alerts */
    .stWarning {
        background-color: rgba(235, 203, 139, 0.1);
        border-left-color: var(--nord13);
    }
    
    /* Error alerts */
    .stError {
        background-color: rgba(191, 97, 106, 0.1);
        border-left-color: var(--nord11);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--nord1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--nord3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--nord9);
    }
    
    /* Header styling */
    .main .block-container {
        padding-top: 2rem;
    }
    
    h1 {
        color: var(--nord6);
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize all session state variables once"""
    if 'initialized' in st.session_state:
        return
    
    st.session_state.initialized = True
    st.session_state.projection_calculated = False
    
    st.session_state.scenario = {}
    
    # Monte Carlo simulation parameters
    st.session_state.monte_carlo = {
        'num_simulations': 1000,
        'market_regime_modeling': False,
        'confidence_levels': [5, 10, 25, 50, 75, 90, 95],
        'results_calculated': False
    }
    
    st.session_state.people_df = pd.DataFrame([
        {'name': 'Jack', 'current_age': 35},
        {'name': 'Jill', 'current_age': 35},
        {'name': 'Child', 'current_age': 8},
    ])
    
    st.session_state.accounts_df = pd.DataFrame([
        {'account_type': '401k', 'account_owner': 'Jack', 'current_balance': 125000,
         'aggressive_rate': 7.0, 'conservative_rate': 5.0, 
         'transition_start_age': 50, 'transition_end_age': 60},
        {'account_type': '401k', 'account_owner': 'Jill', 'current_balance': 110000,
         'aggressive_rate': 7.0, 'conservative_rate': 5.0, 
         'transition_start_age': 55, 'transition_end_age': 65},
        {'account_type': 'Roth IRA', 'account_owner': 'Jack', 'current_balance': 45000,
         'aggressive_rate': 8.0, 'conservative_rate': 6.0, 
         'transition_start_age': 55, 'transition_end_age': 65},
        {'account_type': 'Roth IRA', 'account_owner': 'Jill', 'current_balance': 38000,
         'aggressive_rate': 8.0, 'conservative_rate': 6.0, 
         'transition_start_age': 55, 'transition_end_age': 65},
        {'account_type': 'HSA', 'account_owner': 'Joint', 'current_balance': 12000,
         'aggressive_rate': 6.5, 'conservative_rate': 4.0, 
         'transition_start_age': 55, 'transition_end_age': 65},
        {'account_type': '529', 'account_owner': 'Child', 'current_balance': 25000,
         'aggressive_rate': 7.5, 'conservative_rate': 5.5, 
         'transition_start_age': 8, 'transition_end_age': 16},
        {'account_type': 'Taxable', 'account_owner': 'Joint', 'current_balance': 75000,
         'aggressive_rate': 6.0, 'conservative_rate': 4.5, 
         'transition_start_age': 55, 'transition_end_age': 65},
    ])
    
    st.session_state.income_df = pd.DataFrame([
        {'name': 'Salary', 'person': 'Jack', 
         'annual_amount': 105000, 'start_age': 35, 'end_age': 65, 'growth_rate': 2.9},
        {'name': 'Salary', 'person': 'Jill', 
         'annual_amount': 107000, 'start_age': 35, 'end_age': 63, 'growth_rate': 2.9},
        {'name': 'Social Security', 'person': 'Jack',
         'annual_amount': 29000, 'start_age': 67, 'end_age': 95, 'growth_rate': 2.5},
        {'name': 'Social Security', 'person': 'Jill',
         'annual_amount': 29000, 'start_age': 67, 'end_age': 95, 'growth_rate': 2.5},
    ])
    
    st.session_state.expenses_df = pd.DataFrame([
        {'name': 'Basic Living Expenses', 'person': 'Joint', 'annual_amount': 90000, 'start_age': 35, 'end_age': 95, 'growth_rate': 3.2},
        {'name': 'Childcare & Child Expenses', 'person': 'Child', 'annual_amount': 18000, 'start_age': 8, 'end_age': 17, 'growth_rate': 3.0},
        {'name': 'Healthcare Out of Pocket', 'person': 'Joint', 'annual_amount': 8000, 'start_age': 65, 'end_age': 95, 'growth_rate': 4.5},
        {'name': 'College Tuition', 'person': 'Child', 'annual_amount': 60000, 'start_age': 18, 'end_age': 22, 'growth_rate': 5.0},
        {'name': 'Car Purchase (Family SUV)', 'person': 'Joint', 'annual_amount': 45000, 'start_age': 45, 'end_age': 45, 'growth_rate': 0.0},
        {'name': 'Car Purchase (Replacement)', 'person': 'Joint', 'annual_amount': 50000, 'start_age': 55, 'end_age': 55, 'growth_rate': 0.0},
        {'name': 'Car Purchase (Teen Car)', 'person': 'Child', 'annual_amount': 20000, 'start_age': 18, 'end_age': 18, 'growth_rate': 0.0},
        {'name': 'Primary Home - Property Tax', 'person': 'Joint', 'annual_amount': 9500, 'start_age': 35, 'end_age': 62, 'growth_rate': 3.2},
        {'name': 'Primary Home - Insurance', 'person': 'Joint', 'annual_amount': 1800, 'start_age': 35, 'end_age': 62, 'growth_rate': 4.5},
        {'name': 'Primary Home - Maintenance', 'person': 'Joint', 'annual_amount': 6500, 'start_age': 35, 'end_age': 62, 'growth_rate': 3.8},
        {'name': 'Retirement Home - Property Tax', 'person': 'Joint', 'annual_amount': 6200, 'start_age': 62, 'end_age': 95, 'growth_rate': 3.0},
        {'name': 'Retirement Home - Insurance', 'person': 'Joint', 'annual_amount': 1400, 'start_age': 62, 'end_age': 95, 'growth_rate': 4.0},
        {'name': 'Retirement Home - Maintenance', 'person': 'Joint', 'annual_amount': 4200, 'start_age': 62, 'end_age': 95, 'growth_rate': 3.5},
    ])
    
    st.session_state.real_estate_df = pd.DataFrame([
        {
            'property_name': 'Primary Residence',
            'address': '123 Maple Drive', 
            'purchase_year': 2019,
            'purchase_price': 480000,
            'down_payment_percent': 15.0,
            'mortgage_rate': 3.25,
            'mortgage_term_years': 30,
            'appreciation_rate': 3.5,
            'sale_year': 2052,
            'current_value': 650000,
            'current_mortgage_balance': 320000,
            'is_existing_property': True
        },
        {
            'property_name': 'Retirement Home',
            'address': '456 Sunset Lane', 
            'purchase_year': 2052,
            'purchase_price': 425000,
            'down_payment_percent': 40.0,
            'mortgage_rate': 5.5,
            'mortgage_term_years': 15,
            'appreciation_rate': 2.8,
            'sale_year': None,
            'current_value': None,
            'current_mortgage_balance': None,
            'is_existing_property': False
        }
    ])

init_session_state()


def run_projection():
    """Prepare scenario dict and run projection"""
    try:
        scenario = ScenarioManager.build_scenario_from_session_state()
        
        st.session_state.projection_df = project_scenario(scenario)
        st.session_state.metrics = calculate_success_metrics(st.session_state.projection_df)
        st.session_state.retirement_ages = get_retirement_ages(scenario)
        st.session_state.projection_calculated = True
        
        return True
    except Exception as e:
        st.error(f"Error running projection: {str(e)}")
        return False


st.title("📊 Finplanner 9000")


tabs = st.tabs([
    "🎯 Scenario Setup", 
    "📈 Account Balances", 
    "💰 Cash Flow", 
    "🎲 Monte Carlo"
])

with tabs[0]:
    render_scenario_setup_tab(run_projection)

with tabs[1]:
    render_account_balances_tab()

with tabs[2]:
    render_cash_flow_tab()

with tabs[3]:
    render_monte_carlo_tab()