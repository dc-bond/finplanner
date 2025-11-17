"""
Monte Carlo simulation engine for financial projections.
Builds on the existing deterministic projection system by adding stochastic returns.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from .projection import project_scenario, calculate_success_metrics
import copy


class MonteCarloEngine:
    """Monte Carlo simulation engine for financial projections"""
    
    ASSET_CLASS_VOLATILITY = {
        'stocks': 0.18,
        'bonds': 0.05,
        'international': 0.20,
        'real_estate': 0.15,
        'cash': 0.01,
        'commodities': 0.25
    }
    
    ASSET_CORRELATIONS = {
        ('stocks', 'bonds'): -0.1,
        ('stocks', 'international'): 0.8,
        ('stocks', 'real_estate'): 0.6,
        ('bonds', 'real_estate'): 0.2,
        ('international', 'real_estate'): 0.5,
    }
    
    def __init__(self, num_simulations: int = 1000):
        """Initialize Monte Carlo engine
        
        Args:
            num_simulations: Number of simulation runs to execute
        """
        self.num_simulations = num_simulations
        self.simulation_results = []
        self.summary_stats = {}
        
    def map_account_to_asset_class(self, account_type: str, growth_strategy: str) -> str:
        """Map account types and strategies to asset classes for volatility calculation"""
        
        if account_type in ['US Treasury', 'Treasury Direct']:
            return 'bonds'
        elif account_type == 'HSA':
            return 'stocks'
        elif account_type in ['401k', 'TSP', 'Roth IRA', 'Traditional IRA']:
            if growth_strategy == 'Target Date':
                return 'stocks'
            else:
                return 'stocks'
        elif account_type == '529':
            return 'stocks'
        elif account_type == 'Taxable':
            return 'stocks'
        else:
            return 'stocks'
    
    def calculate_volatility_from_return(self, return_rate: float) -> float:
        """Calculate volatility based on expected return rate using realistic risk/return relationship
        
        Args:
            return_rate: Expected return rate as decimal (e.g., 0.08 for 8%)
            
        Returns:
            Volatility as decimal (e.g., 0.15 for 15%)
        """
        
        return_pct = return_rate * 100
        
        if return_pct >= 8.0:
            return 0.16 + (return_pct - 8.0) * 0.01
        elif return_pct >= 7.0:
            return 0.12 + (return_pct - 7.0) * 0.04
        elif return_pct >= 5.5:
            return 0.08 + (return_pct - 5.5) * 0.027
        elif return_pct >= 4.0:
            return 0.04 + (return_pct - 4.0) * 0.027
        else:
            return 0.02 + return_pct * 0.005

    def get_account_volatility(self, account: Dict, deterministic_rate: float = None) -> float:
        """Calculate volatility for a specific account based on its current growth rate"""
        
        if deterministic_rate is not None:
            return self.calculate_volatility_from_return(deterministic_rate)
        
        current_return = self.get_current_account_return_rate(account)
        return self.calculate_volatility_from_return(current_return)
    
    def get_current_account_return_rate(self, account: Dict) -> float:
        """Get the current effective return rate for an account, interpolated if in transition"""
        
        aggressive_rate = account.get('aggressive_rate', 7.0)
        conservative_rate = account.get('conservative_rate', 5.0)
        
        return aggressive_rate
    
    def generate_correlated_returns(self, accounts: List[Dict], expected_returns: List[float], 
                                  volatilities: List[float]) -> np.ndarray:
        """Generate correlated returns for multiple accounts using Cholesky decomposition"""
        
        n_accounts = len(accounts)
        if n_accounts == 1:
            return np.random.normal(expected_returns[0], volatilities[0])
        
        correlation_matrix = np.eye(n_accounts)
        for i in range(n_accounts):
            for j in range(i + 1, n_accounts):
                correlation_matrix[i, j] = correlation_matrix[j, i] = 0.3
        
        chol = np.linalg.cholesky(correlation_matrix)
        uncorrelated = np.random.normal(0, 1, n_accounts)
        correlated = chol @ uncorrelated
        
        returns = []
        for i, (expected, vol) in enumerate(zip(expected_returns, volatilities)):
            returns.append(expected + vol * correlated[i])
        
        return np.array(returns)
    
    def calculate_stochastic_return(self, account: Dict, owner_age: int, people_data: List,
                                  deterministic_rate: float) -> float:
        """Calculate stochastic return for an account, preserving deterministic logic as mean"""
        
        volatility = self.get_account_volatility(account)
        stochastic_return = np.random.normal(deterministic_rate, volatility)
        return np.clip(stochastic_return, -0.5, 1.0)
    
    def run_single_simulation(self, scenario: Dict, simulation_id: int = 0) -> pd.DataFrame:
        """Run a single Monte Carlo simulation by modifying the projection calculation"""
        
        sim_scenario = copy.deepcopy(scenario)
        
        from .projection import (calculate_total_income, calculate_total_expenses, 
                               calculate_account_growth_rate, get_projection_cache, 
                               clear_projection_cache)
        
        clear_projection_cache()
        
        current_age = sim_scenario['current_age']
        max_age = sim_scenario['max_projection_age']
        current_year = sim_scenario['current_year']
        people_data = sim_scenario.get('people', [])
        
        if isinstance(sim_scenario.get('accounts'), dict):
            account_balances = {}
            for account_name, balance in sim_scenario['accounts'].items():
                account_balances[account_name] = {
                    'balance': balance,
                    'growth_strategy': 'Fixed',
                    'aggressive_rate': 0.05,
                    'account_owner': 'Joint',
                    'account_type': 'Taxable'
                }
        else:
            account_balances = {}
            accounts_list = sim_scenario.get('account_details', [])
            for account in accounts_list:
                account_key = f"{account['account_type']}_{account['account_owner']}"
                account_balances[account_key] = {
                    'balance': account['current_balance'],
                    'growth_strategy': account.get('growth_strategy', 'Fixed'),
                    'aggressive_rate': account.get('aggressive_rate', 0.05),
                    'conservative_rate': account.get('conservative_rate', 0.05),
                    'transition_start_age': account.get('transition_start_age', 50),
                    'transition_end_age': account.get('transition_end_age', 65),
                    'account_owner': account['account_owner'],
                    'account_type': account['account_type']
                }
        
        projections = []
        real_estate_equity = 0
        
        np.random.seed(simulation_id * 1000)
        
        for age in range(current_age, max_age + 1):
            year = current_year + (age - current_age)
            
            income = calculate_total_income(sim_scenario, age, year)
            expenses = calculate_total_expenses(sim_scenario, age, year)
            
            real_estate_cash_from_sales = 0
            if 'real_estate' in sim_scenario and sim_scenario['real_estate']:
                cache = get_projection_cache()
                re_impact = cache.get_real_estate_impact(
                    sim_scenario['real_estate'], sim_scenario['current_year'], age, year
                )
                real_estate_cash_from_sales = re_impact['sale_proceeds']
                current_re_equity = sum(re_impact['equity_values'].values())
                real_estate_equity = current_re_equity
            
            net_cashflow = income - expenses + real_estate_cash_from_sales
            
            total_return_amount = 0
            total_portfolio_balance = 0
            
            account_keys = list(account_balances.keys())
            deterministic_rates = []
            volatilities = []
            account_objects = []
            
            for account_key, account_data in account_balances.items():
                owner_name = account_data['account_owner']
                if owner_name == 'Joint':
                    owner_age = age
                else:
                    person = next((p for p in people_data if p['name'] == owner_name), None)
                    if person:
                        owner_age = person['current_age'] + (year - current_year)
                    else:
                        owner_age = age
                
                det_rate = calculate_account_growth_rate(account_data, owner_age, people_data)
                deterministic_rates.append(det_rate)
                volatilities.append(self.get_account_volatility(account_data, det_rate))
                account_objects.append(account_data)
            
            if account_keys:
                stochastic_returns = self.generate_correlated_returns(
                    account_objects, deterministic_rates, volatilities
                )
                
                for i, (account_key, account_data) in enumerate(account_balances.items()):
                    stochastic_rate = stochastic_returns[i] if len(account_keys) > 1 else stochastic_returns
                    
                    account_return = account_data['balance'] * stochastic_rate
                    total_return_amount += account_return
                    
                    account_data['balance'] += account_return
                    total_portfolio_balance += account_data['balance']
            
            if net_cashflow != 0:
                if total_portfolio_balance > 0:
                    for account_key, account_data in account_balances.items():
                        account_proportion = account_data['balance'] / total_portfolio_balance
                        account_contribution = net_cashflow * account_proportion
                        account_data['balance'] += account_contribution
                        
                        if account_data['balance'] < 0:
                            account_data['balance'] = 0
                else:
                    if net_cashflow > 0:
                        if account_balances:
                            first_account = list(account_balances.values())[0]
                            first_account['balance'] = max(0, net_cashflow)
            
            total_portfolio_balance = sum(acc['balance'] for acc in account_balances.values())
            
            projections.append({
                'age': age,
                'year': year,
                'income': income,
                'expenses': expenses,
                'net_cashflow': net_cashflow - real_estate_cash_from_sales,
                'real_estate_sales': real_estate_cash_from_sales,
                'portfolio_contribution': net_cashflow,
                'portfolio_return_amount': total_return_amount,
                'portfolio_balance': total_portfolio_balance,
                'real_estate_equity': real_estate_equity,
                'total_net_worth': total_portfolio_balance + real_estate_equity,
                'simulation_id': simulation_id
            })
        
        return pd.DataFrame(projections)
    
    def run_monte_carlo_simulation(self, scenario: Dict) -> Dict:
        """Run full Monte Carlo simulation with multiple iterations"""
        
        print(f"Running Monte Carlo simulation with {self.num_simulations} iterations...")
        
        all_simulations = []
        success_metrics = []
        
        for sim_id in range(self.num_simulations):
            if sim_id % 100 == 0:
                print(f"Completed {sim_id}/{self.num_simulations} simulations...")
            
            # Run single simulation
            sim_df = self.run_single_simulation(scenario, sim_id)
            all_simulations.append(sim_df)
            
            metrics = calculate_success_metrics(sim_df)
            metrics['simulation_id'] = sim_id
            success_metrics.append(metrics)
        
        combined_df = pd.concat(all_simulations, ignore_index=True)
        metrics_df = pd.DataFrame(success_metrics)
        
        summary_stats = self.calculate_summary_statistics(combined_df, metrics_df)
        
        self.simulation_results = combined_df
        self.success_metrics = metrics_df
        self.summary_stats = summary_stats
        
        print(f"Monte Carlo simulation completed!")
        
        return {
            'simulation_results': combined_df,
            'success_metrics': metrics_df,
            'summary_stats': summary_stats
        }
    
    def calculate_summary_statistics(self, simulation_df: pd.DataFrame, 
                                   metrics_df: pd.DataFrame) -> Dict:
        """Calculate summary statistics across all simulations"""
        
        age_groups = simulation_df.groupby('age')['portfolio_balance']
        
        percentile_data = []
        for age, balances in age_groups:
            percentiles = np.percentile(balances, [5, 10, 25, 50, 75, 90, 95])
            percentile_data.append({
                'age': age,
                'p5': percentiles[0],
                'p10': percentiles[1], 
                'p25': percentiles[2],
                'p50': percentiles[3],  # median
                'p75': percentiles[4],
                'p90': percentiles[5],
                'p95': percentiles[6],
                'mean': balances.mean(),
                'std': balances.std()
            })
        
        percentiles_df = pd.DataFrame(percentile_data)
        
        success_rate = len(metrics_df[metrics_df['first_deficit_age'].isna()]) / len(metrics_df)
        
        depleted_sims = metrics_df[metrics_df['first_deficit_age'].notna()]
        depletion_ages = depleted_sims['first_deficit_age'].values if len(depleted_sims) > 0 else []
        
        final_balances = metrics_df['final_balance']
        
        return {
            'success_rate': success_rate,
            'percentiles_by_age': percentiles_df,
            'final_balance_stats': {
                'mean': final_balances.mean(),
                'median': final_balances.median(),
                'std': final_balances.std(),
                'min': final_balances.min(),
                'max': final_balances.max(),
                'p5': np.percentile(final_balances, 5),
                'p95': np.percentile(final_balances, 95)
            },
            'depletion_analysis': {
                'depletion_rate': len(depleted_sims) / len(metrics_df),
                'median_depletion_age': np.median(depletion_ages) if len(depletion_ages) > 0 else None,
                'earliest_depletion': min(depletion_ages) if len(depletion_ages) > 0 else None,
                'latest_depletion': max(depletion_ages) if len(depletion_ages) > 0 else None
            },
            'total_simulations': self.num_simulations
        }


def run_monte_carlo_analysis(scenario: Dict, num_simulations: int = 1000) -> Dict:
    """Convenience function to run Monte Carlo analysis"""
    engine = MonteCarloEngine(num_simulations)
    return engine.run_monte_carlo_simulation(scenario)