"""
Property classes for real estate calculations.
Provides polymorphic behavior for existing vs future properties.
"""

import pandas as pd
from abc import ABC, abstractmethod


class Property(ABC):
    """Base class for all property types"""
    
    def __init__(self, property_data):
        self.property_name = property_data['property_name']
        self.address = property_data.get('address', '')
        self.mortgage_rate = property_data.get('mortgage_rate', 4.0) / 100
        self.mortgage_term_years = property_data.get('mortgage_term_years', 30)
        self.appreciation_rate = property_data.get('appreciation_rate', 3.0) / 100
        self.sale_year = property_data.get('sale_year')
        self.purchase_year = int(property_data.get('purchase_year', 2020))
        self.purchase_price = property_data.get('purchase_price', 0)
        self.down_payment_percent = property_data.get('down_payment_percent', 20.0) / 100
    
    @abstractmethod
    def calculate_value_at_year(self, year, current_year=None):
        """Calculate property value in a given year"""
        pass
    
    @abstractmethod
    def calculate_mortgage_balance_at_year(self, year, current_year):
        """Calculate remaining mortgage balance in a given year"""
        pass
    
    def is_sold_before_year(self, year):
        """Check if property was sold before the given year"""
        return not pd.isna(self.sale_year) and year > int(self.sale_year)
    
    def is_sold_in_year(self, year):
        """Check if property is sold in the given year"""
        return not pd.isna(self.sale_year) and int(self.sale_year) == year
    
    def calculate_equity_at_year(self, year, current_year):
        """Calculate equity (value - mortgage balance) in a given year"""
        if self.is_sold_before_year(year):
            return 0
        
        value = self.calculate_value_at_year(year, current_year)
        balance = self.calculate_mortgage_balance_at_year(year, current_year)
        return max(0, value - balance)
    
    def calculate_sale_proceeds(self, year, current_year, closing_cost_rate=0.06):
        """Calculate net proceeds from property sale"""
        if not self.is_sold_in_year(year):
            return 0
        
        equity = self.calculate_equity_at_year(year, current_year)
        return equity * (1 - closing_cost_rate)


class ExistingProperty(Property):
    """
    Property that is already owned with known current values.
    
    For existing properties:
    - 'current_value' is used as the baseline for future appreciation
    - 'current_mortgage_balance' is used for mortgage payment calculations
    - 'purchase_year' and 'purchase_price' are only used for determining 
      mortgage payment schedules (years already paid, remaining term)
    - Appreciation is applied from the current year forward, not from purchase year
    """
    
    def __init__(self, property_data):
        super().__init__(property_data)
        self.current_value = property_data.get('current_value', 0)
        self.current_mortgage_balance = property_data.get('current_mortgage_balance', 0)
    
    def calculate_value_at_year(self, year, current_year=None):
        """Apply appreciation to current value from current year forward"""
        if current_year is None:
            current_year = 2025
        
        years_from_current = max(0, year - current_year)
        return self.current_value * (1 + self.appreciation_rate) ** years_from_current
    
    def calculate_mortgage_balance_at_year(self, year, current_year):
        """Calculate balance progression from current balance"""
        if self.current_mortgage_balance <= 0:
            return 0
        
        years_since_current = year - current_year
        if years_since_current <= 0:
            return self.current_mortgage_balance
        
        years_already_paid = current_year - self.purchase_year
        remaining_term_years = self.mortgage_term_years - years_already_paid
        
        if remaining_term_years <= years_since_current:
            return 0
        
        from .real_estate_v2 import calculate_mortgage_balance
        months_additional = years_since_current * 12
        return calculate_mortgage_balance(
            self.current_mortgage_balance, 
            self.mortgage_rate, 
            remaining_term_years, 
            months_additional
        )


class FutureProperty(Property):
    """
    Property to be purchased in the future.
    
    For future properties:
    - 'purchase_price' is used as the baseline for appreciation calculations
    - 'purchase_year' determines when the property is acquired and payments begin
    - Appreciation is applied from the purchase year forward
    - Down payment is calculated as a percentage of purchase price
    """
    
    def __init__(self, property_data):
        super().__init__(property_data)
    
    def calculate_value_at_year(self, year, current_year=None):
        """Calculate value with appreciation from purchase year"""
        if year < self.purchase_year:
            return 0
        
        years_owned = year - self.purchase_year
        return self.purchase_price * (1 + self.appreciation_rate) ** years_owned
    
    def calculate_mortgage_balance_at_year(self, year, current_year):
        """Calculate mortgage balance from purchase year"""
        if year < self.purchase_year:
            return 0
        
        years_since_purchase = year - self.purchase_year
        mortgage_principal = self.purchase_price * (1 - self.down_payment_percent)
        
        if years_since_purchase >= self.mortgage_term_years:
            return 0
        
        from .real_estate_v2 import calculate_mortgage_balance
        months_since_purchase = years_since_purchase * 12
        return calculate_mortgage_balance(
            mortgage_principal,
            self.mortgage_rate,
            self.mortgage_term_years,
            months_since_purchase
        )
    
    def get_down_payment_in_year(self, year):
        """Get down payment amount if purchased in this year"""
        if year == self.purchase_year:
            return self.purchase_price * self.down_payment_percent
        return 0


def create_property(property_data):
    """Factory function to create appropriate property type"""
    is_existing = property_data.get('is_existing_property', False)
    
    if is_existing:
        return ExistingProperty(property_data)
    else:
        return FutureProperty(property_data)