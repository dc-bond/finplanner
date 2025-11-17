"""
Improved real estate calculation module using property classes.
Cleaner, more maintainable approach to real estate financial modeling.
"""

import pandas as pd
from .property_classes import create_property


def calculate_monthly_mortgage_payment(principal, annual_rate, years):
    """
    Calculate monthly mortgage payment using standard amortization formula.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (as decimal, e.g., 0.04 for 4%)
        years: Loan term in years
    
    Returns:
        Monthly payment amount
    """
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                     ((1 + monthly_rate)**num_payments - 1)
    
    return monthly_payment


def calculate_mortgage_balance(original_principal, annual_rate, term_years, payments_made):
    """
    Calculate remaining mortgage balance after a number of payments.
    
    Args:
        original_principal: Original loan amount
        annual_rate: Annual interest rate (as decimal)
        term_years: Original loan term in years
        payments_made: Number of monthly payments already made
    
    Returns:
        Remaining balance
    """
    if annual_rate == 0:
        total_payments = term_years * 12
        return max(0, original_principal - (original_principal * payments_made / total_payments))
    
    monthly_rate = annual_rate / 12
    total_payments = term_years * 12
    
    if payments_made >= total_payments:
        return 0
    
    remaining_balance = original_principal * \
                       ((1 + monthly_rate)**(total_payments) - (1 + monthly_rate)**payments_made) / \
                       ((1 + monthly_rate)**(total_payments) - 1)
    
    return max(0, remaining_balance)


def calculate_real_estate_impact_v2(properties, current_year, age, year):
    """
    Calculate the impact of real estate on finances for a specific year.
    
    Uses property classes for cleaner, more maintainable calculations.
    
    Property Value Calculations:
    - Existing Properties: Use 'current_value' as baseline, apply appreciation from current_year forward
    - Future Properties: Use 'purchase_price' as baseline, apply appreciation from purchase_year forward
    - 'purchase_year' and 'purchase_price' for existing properties are only used for mortgage calculations
    
    Returns dict with:
    - expenses: Total annual expenses (mortgage + operating costs)
    - income: Rental income (if any)  
    - one_time_expenses: Down payments or other one-time costs
    - property_values: Dict of current property values
    - equity_values: Dict of equity (value - mortgage balance)
    - sale_proceeds: Cash from property sales this year
    """
    
    result = {
        'annual_expenses': 0,
        'annual_income': 0,
        'one_time_expenses': 0,
        'property_values': {},
        'equity_values': {},
        'sale_proceeds': 0,
    }
    
    for prop_data in properties:
        if pd.isna(prop_data.get('property_name')):
            continue
        
        property_obj = create_property(prop_data)
        
        if property_obj.is_sold_before_year(year):
            continue
        
        property_value = property_obj.calculate_value_at_year(year, current_year)
        equity_value = property_obj.calculate_equity_at_year(year, current_year)
        mortgage_balance = property_obj.calculate_mortgage_balance_at_year(year, current_year)
        
        result['property_values'][property_obj.property_name] = property_value
        result['equity_values'][property_obj.property_name] = equity_value
        
        if hasattr(property_obj, 'get_down_payment_in_year'):
            down_payment = property_obj.get_down_payment_in_year(year)
            result['one_time_expenses'] += down_payment
        
        if mortgage_balance > 0 and not property_obj.is_sold_in_year(year):
            if hasattr(property_obj, 'current_mortgage_balance') and property_obj.current_mortgage_balance > 0:
                years_already_paid = current_year - property_obj.purchase_year
                remaining_term = max(1, property_obj.mortgage_term_years - years_already_paid)
                monthly_payment = calculate_monthly_mortgage_payment(
                    property_obj.current_mortgage_balance,
                    property_obj.mortgage_rate,
                    remaining_term
                )
            else:
                mortgage_principal = property_obj.purchase_price * (1 - property_obj.down_payment_percent)
                monthly_payment = calculate_monthly_mortgage_payment(
                    mortgage_principal,
                    property_obj.mortgage_rate,
                    property_obj.mortgage_term_years
                )
            
            result['annual_expenses'] += monthly_payment * 12
        
        if property_obj.is_sold_in_year(year):
            sale_proceeds = property_obj.calculate_sale_proceeds(year, current_year)
            result['sale_proceeds'] += sale_proceeds
            result['equity_values'][property_obj.property_name] = 0
    
    return result