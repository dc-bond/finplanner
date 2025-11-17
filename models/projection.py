"""
Comprehensive financial projection engine.
Takes a scenario dictionary and produces year-by-year projections of:
- Income (all sources)
- Expenses (recurring + planned)
- Net cashflow
- Account balances (with investment returns)
- Withdrawal strategy during retirement
"""

import pandas as pd
import numpy as np
from .real_estate_v2 import calculate_real_estate_impact_v2 as calculate_real_estate_impact
from services.projection_cache import get_projection_cache, clear_projection_cache


def calculate_account_growth_rate(account, owner_age, people_data):
    """
    Calculate the growth rate for an account based on owner's age and transition settings.
    
    Age-based rate calculation:
    - Uses young age rate when owner is young (≤ transition start age)  
    - Uses old age rate when owner is old (≥ transition end age)
    - Linear transition between the rates during transition period
    - For fixed rate behavior: set young age rate = old age rate
    
    Args:
        account: Dict with rate and transition age details
        owner_age: Current age of the account owner
        people_data: List of people with their current ages (for age calculation)
    
    Returns:
        float: The growth rate to use for this account in this year
    """
    aggressive_rate = account.get('aggressive_rate', 6.0)
    conservative_rate = account.get('conservative_rate', 6.0)
    transition_start = account.get('transition_start_age', 50)
    transition_end = account.get('transition_end_age', 65)
    
    if owner_age <= transition_start:
        return aggressive_rate / 100
    elif owner_age >= transition_end:
        return conservative_rate / 100
    else:
        transition_progress = (owner_age - transition_start) / (transition_end - transition_start)
        return (aggressive_rate + (conservative_rate - aggressive_rate) * transition_progress) / 100


def calculate_total_income(scenario, age, year):
    """Calculate total income for a given age/year"""
    total_income = 0
    
    if 'income_sources' in scenario and scenario['income_sources']:
        for income_src in scenario['income_sources']:
            income_person = income_src.get('person', 'Joint')
            
            if income_person != 'Joint':
                if 'people' in scenario and scenario['people']:
                    person_data = next((p for p in scenario['people'] if p['name'] == income_person), None)
                    if person_data:
                        person_age = person_data['current_age'] + (year - scenario['current_year'])
                        income_age = person_age
                    else:
                        income_age = age
                else:
                    income_age = age
            else:
                income_age = age
            
            if income_src['start_age'] <= income_age <= income_src['end_age']:
                years_from_start = income_age - income_src['start_age']
                amount = income_src['annual_amount'] * (1 + income_src['growth_rate'] / 100) ** years_from_start
                total_income += amount
    
    if 'retirement_income' in scenario and scenario['retirement_income']:
        for ret_income in scenario['retirement_income']:
            income_person = ret_income.get('person', 'Joint')
            
            if income_person != 'Joint':
                if 'people' in scenario and scenario['people']:
                    person_data = next((p for p in scenario['people'] if p['name'] == income_person), None)
                    if person_data:
                        person_age = person_data['current_age'] + (year - scenario['current_year'])
                        income_age = person_age
                    else:
                        income_age = age
                else:
                    income_age = age
            else:
                income_age = age
            
            if ret_income['start_age'] <= income_age <= ret_income['end_age']:
                years_from_start = income_age - ret_income['start_age']
                amount = ret_income['annual_amount'] * (1 + ret_income['growth_rate'] / 100) ** years_from_start
                total_income += amount
    
    if 'real_estate' in scenario and scenario['real_estate']:
        cache = get_projection_cache()
        re_impact = cache.get_real_estate_impact(
            scenario['real_estate'], scenario['current_year'], age, year
        )
        total_income += re_impact['annual_income']
    
    return total_income


def calculate_total_expenses(scenario, age, year):
    """
    Calculate total expenses for a given age/year with enhanced error handling.
    
    Args:
        scenario: Financial scenario dictionary
        age: Primary person's age in this year
        year: Calendar year
        
    Returns:
        float: Total expenses for the year
    """
    total_expenses = 0
    debug_mode = scenario.get('debug_expenses', False)
    
    if 'recurring_expenses' in scenario and scenario['recurring_expenses']:
        for i, expense in enumerate(scenario['recurring_expenses']):
            try:
                required_fields = ['person', 'start_age', 'end_age', 'annual_amount', 'growth_rate']
                missing_fields = [field for field in required_fields if field not in expense or expense[field] is None]
                if missing_fields:
                    if debug_mode:
                        print(f"Warning: Expense {i} missing fields: {missing_fields}")
                    continue
                
                expense_person = expense.get('person', 'Joint')
                expense_name = expense.get('name', f'Expense_{i}')
                
                if expense_person != 'Joint':
                    if 'people' in scenario and scenario['people']:
                        person_data = next((p for p in scenario['people'] if p['name'] == expense_person), None)
                        if person_data:
                            person_age = person_data['current_age'] + (year - scenario['current_year'])
                            expense_age = person_age
                        else:
                            if debug_mode:
                                print(f"Warning: Person '{expense_person}' not found for expense '{expense_name}', using scenario age")
                            expense_age = age
                    else:
                        if debug_mode:
                            print(f"Warning: No people data available for expense '{expense_name}', using scenario age")
                        expense_age = age
                else:
                    expense_age = age
                
                start_age = expense['start_age']
                end_age = expense['end_age']
                
                if start_age > end_age:
                    if debug_mode:
                        print(f"Error: Expense '{expense_name}' has invalid age range: {start_age} > {end_age}")
                    continue
                
                if start_age <= expense_age <= end_age:
                    years_from_start = expense_age - start_age
                    
                    growth_rate_percent = expense.get('growth_rate', 0)
                    if growth_rate_percent < -50 or growth_rate_percent > 50:
                        if debug_mode:
                            print(f"Warning: Expense '{expense_name}' has extreme growth rate: {growth_rate_percent:.1f}%")
                    
                    growth_rate = growth_rate_percent / 100
                    
                    try:
                        amount = expense['annual_amount'] * (1 + growth_rate) ** years_from_start
                        
                        if amount < 0:
                            if debug_mode:
                                print(f"Warning: Expense '{expense_name}' calculated negative amount: ${amount:.2f}")
                            amount = 0
                        
                        total_expenses += amount
                        
                        if debug_mode:
                            print(f"Active expense: {expense_name} (person: {expense_person}, age: {expense_age}, amount: ${amount:,.2f})")
                    
                    except (ValueError, OverflowError) as e:
                        if debug_mode:
                            print(f"Error calculating expense '{expense_name}': {str(e)}")
                        continue
                
            except Exception as e:
                if debug_mode:
                    print(f"Error processing expense {i}: {str(e)}")
                continue
    
    if 'planned_expenses' in scenario and scenario['planned_expenses']:
        for planned in scenario['planned_expenses']:
            if pd.isna(planned.get('year')) or pd.isna(planned.get('amount')):
                continue
                
            if planned['year'] == year:
                total_expenses += planned['amount']
            elif not pd.isna(planned.get('recurring_years')) and planned.get('recurring_years', 1) > 1:
                if planned['year'] <= year < planned['year'] + planned['recurring_years']:
                    total_expenses += planned['amount']
            
            repeat_every = planned.get('repeat_every')
            repeat_until = planned.get('repeat_until_year')
            
            if not pd.isna(repeat_every) and not pd.isna(repeat_until):
                years_since_first = year - planned['year']
                if years_since_first > 0 and years_since_first % repeat_every == 0:
                    if year <= repeat_until:
                        total_expenses += planned['amount']
    
    if 'real_estate' in scenario and scenario['real_estate']:
        cache = get_projection_cache()
        re_impact = cache.get_real_estate_impact(
            scenario['real_estate'], scenario['current_year'], age, year
        )
        total_expenses += re_impact['annual_expenses']
        total_expenses += re_impact['one_time_expenses']  # Down payments, etc.
    
    return total_expenses


def project_scenario(scenario):
    """
    Main projection function. Returns a DataFrame with year-by-year projections.
    
    Now handles individual accounts with their own growth strategies.
    
    Columns:
    - age: person's age
    - year: calendar year
    - income: total income from all sources
    - expenses: total expenses (recurring + planned)
    - net_cashflow: income - expenses
    - portfolio_contribution: amount added/withdrawn from portfolio
    - portfolio_balance: total portfolio value after returns + contributions
    - portfolio_return_amount: dollar amount gained from investments
    """
    clear_projection_cache()
    
    current_age = scenario['current_age']
    max_age = scenario['max_projection_age']
    current_year = scenario['current_year']
    people_data = scenario.get('people', [])
    
    if isinstance(scenario.get('accounts'), dict):
        account_balances = {}
        for account_name, balance in scenario['accounts'].items():
            account_balances[account_name] = {
                'balance': balance,
                'aggressive_rate': 0.05,
                'conservative_rate': 0.05,
                'transition_start_age': 50,
                'transition_end_age': 65,
                'account_owner': 'Joint'
            }
    else:
        account_balances = {}
        accounts_list = scenario.get('account_details', [])
        for account in accounts_list:
            account_key = f"{account['account_type']}_{account['account_owner']}"
            account_balances[account_key] = {
                'balance': account['current_balance'],
                'aggressive_rate': account.get('aggressive_rate', 0.05),
                'conservative_rate': account.get('conservative_rate', 0.05),
                'transition_start_age': account.get('transition_start_age', 50),
                'transition_end_age': account.get('transition_end_age', 65),
                'account_owner': account['account_owner']
            }
    
    projections = []
    real_estate_equity = 0
    
    for age in range(current_age, max_age + 1):
        year = current_year + (age - current_age)
        
        income = calculate_total_income(scenario, age, year)
        expenses = calculate_total_expenses(scenario, age, year)
        
        real_estate_cash_from_sales = 0
        if 'real_estate' in scenario and scenario['real_estate']:
            cache = get_projection_cache()
            re_impact = cache.get_real_estate_impact(
                scenario['real_estate'], scenario['current_year'], age, year
            )
            real_estate_cash_from_sales = re_impact['sale_proceeds']
            current_re_equity = sum(re_impact['equity_values'].values())
            real_estate_equity = current_re_equity
        
        net_cashflow = income - expenses + real_estate_cash_from_sales
        
        total_return_amount = 0
        total_portfolio_balance = 0
        
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
            
            growth_rate = calculate_account_growth_rate(account_data, owner_age, people_data)
            
            account_return = account_data['balance'] * growth_rate
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
        })
    
    return pd.DataFrame(projections)


def calculate_success_metrics(projection_df):
    """
    Calculate key success metrics from a projection.
    
    Returns dict with:
    - final_balance: portfolio balance at max age
    - years_solvent: number of years with positive balance
    - first_deficit_age: first age where portfolio hits zero (or None)
    - total_contributions: sum of all positive contributions
    - total_withdrawals: sum of all negative contributions
    - total_investment_gains: sum of all investment returns
    """
    
    if projection_df.empty:
        return {
            'final_balance': 0,
            'years_solvent': 0,
            'first_deficit_age': None,
            'total_contributions': 0,
            'total_withdrawals': 0,
            'total_investment_gains': 0,
        }
    
    final_balance = projection_df.iloc[-1]['portfolio_balance']
    years_solvent = len(projection_df[projection_df['portfolio_balance'] > 0])
    
    depleted = projection_df[projection_df['portfolio_balance'] == 0]
    first_deficit_age = depleted.iloc[0]['age'] if len(depleted) > 0 else None
    
    total_contributions = projection_df[projection_df['portfolio_contribution'] > 0]['portfolio_contribution'].sum()
    total_withdrawals = abs(projection_df[projection_df['portfolio_contribution'] < 0]['portfolio_contribution'].sum())
    total_investment_gains = projection_df['portfolio_return_amount'].sum()
    
    return {
        'final_balance': final_balance,
        'years_solvent': years_solvent,
        'first_deficit_age': first_deficit_age,
        'total_contributions': total_contributions,
        'total_withdrawals': total_withdrawals,
        'total_investment_gains': total_investment_gains,
    }


def get_retirement_ages(scenario):
    """
    Extract retirement ages from income sources.
    Returns list of dicts: [{'person': name, 'retirement_age': age}, ...]
    """
    retirement_ages = []
    
    if 'income_sources' in scenario and scenario['income_sources']:
        for income_src in scenario['income_sources']:
            retirement_ages.append({
                'person': income_src.get('person', 'Unknown'),
                'retirement_age': income_src.get('end_age', 65)
            })
    
    return retirement_ages