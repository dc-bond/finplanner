"""
Validation service for financial planning inputs.
Provides comprehensive validation for user-entered data.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataValidator:
    """Comprehensive data validation for financial planning inputs"""
    
    @staticmethod
    def validate_people(people_df: pd.DataFrame) -> List[str]:
        """Validate people data and return list of error messages"""
        errors = []
        
        if people_df.empty:
            errors.append("At least one person must be defined")
            return errors
        
        for idx, person in people_df.iterrows():
            if pd.isna(person.get('name')) or str(person['name']).strip() == '':
                errors.append(f"Row {idx + 1}: Name cannot be empty")
            
            name_counts = people_df['name'].value_counts()
            if any(count > 1 for count in name_counts):
                duplicates = name_counts[name_counts > 1].index.tolist()
                errors.append(f"Duplicate names found: {', '.join(duplicates)}")
            
            age = person.get('current_age')
            if pd.isna(age) or age < 0 or age > 120:
                errors.append(f"Row {idx + 1}: Age must be between 0 and 120")
        
        return errors
    
    @staticmethod
    def validate_accounts(accounts_df: pd.DataFrame) -> List[str]:
        """Validate account data and return list of error messages"""
        errors = []
        
        if accounts_df.empty:
            errors.append("At least one account must be defined")
            return errors
        
        for idx, account in accounts_df.iterrows():
            if pd.isna(account.get('account_type')) or str(account['account_type']).strip() == '':
                errors.append(f"Row {idx + 1}: Account type cannot be empty")
            
            if pd.isna(account.get('account_owner')) or str(account['account_owner']).strip() == '':
                errors.append(f"Row {idx + 1}: Account owner cannot be empty")
            
            balance = account.get('current_balance')
            if pd.isna(balance) or balance < 0:
                errors.append(f"Row {idx + 1}: Current balance cannot be negative")
            
            agg_rate = account.get('aggressive_rate')
            cons_rate = account.get('conservative_rate')
            
            if pd.isna(agg_rate) or agg_rate < -50 or agg_rate > 50:
                errors.append(f"Row {idx + 1}: Aggressive rate must be between -50% and 50%")
            
            if pd.isna(cons_rate) or cons_rate < -50 or cons_rate > 50:
                errors.append(f"Row {idx + 1}: Conservative rate must be between -50% and 50%")
            
            start_age = account.get('transition_start_age')
            end_age = account.get('transition_end_age')
            
            if not pd.isna(start_age) and not pd.isna(end_age):
                if start_age >= end_age:
                    errors.append(f"Row {idx + 1}: Transition start age must be less than end age")
                if start_age < 0 or end_age > 120:
                    errors.append(f"Row {idx + 1}: Transition ages must be between 0 and 120")
        
        return errors
    
    @staticmethod
    def validate_real_estate(real_estate_df: pd.DataFrame) -> List[str]:
        """Validate real estate data and return list of error messages"""
        errors = []
        
        if real_estate_df.empty:
            return errors
        
        for idx, prop in real_estate_df.iterrows():
            if pd.isna(prop.get('property_name')) or str(prop['property_name']).strip() == '':
                continue
            
            purchase_price = prop.get('purchase_price')
            if pd.isna(purchase_price) or purchase_price <= 0:
                errors.append(f"Row {idx + 1}: Purchase price must be greater than 0")
            
            down_payment_pct = prop.get('down_payment_percent')
            if pd.isna(down_payment_pct) or down_payment_pct < 0 or down_payment_pct > 100:
                errors.append(f"Row {idx + 1}: Down payment percent must be between 0 and 100")
            
            mortgage_rate = prop.get('mortgage_rate')
            if pd.isna(mortgage_rate) or mortgage_rate < 0 or mortgage_rate > 50:
                errors.append(f"Row {idx + 1}: Mortgage rate must be between 0% and 50%")
            
            appreciation_rate = prop.get('appreciation_rate')
            if pd.isna(appreciation_rate) or appreciation_rate < -50 or appreciation_rate > 50:
                errors.append(f"Row {idx + 1}: Appreciation rate must be between -50% and 50%")
            
            mortgage_term = prop.get('mortgage_term_years')
            if pd.isna(mortgage_term) or mortgage_term < 1 or mortgage_term > 50:
                errors.append(f"Row {idx + 1}: Mortgage term must be between 1 and 50 years")
            
            purchase_year = prop.get('purchase_year')
            sale_year = prop.get('sale_year')
            
            if pd.isna(purchase_year) or purchase_year < 1900 or purchase_year > 2100:
                errors.append(f"Row {idx + 1}: Purchase year must be between 1900 and 2100")
            
            if not pd.isna(sale_year):
                if sale_year < 1900 or sale_year > 2100:
                    errors.append(f"Row {idx + 1}: Sale year must be between 1900 and 2100")
                elif not pd.isna(purchase_year) and sale_year <= purchase_year:
                    errors.append(f"Row {idx + 1}: Sale year must be after purchase year")
        
        return errors
    
    @staticmethod
    def validate_income(income_df: pd.DataFrame) -> List[str]:
        """Validate income data and return list of error messages"""
        errors = []
        
        for idx, income in income_df.iterrows():
            if pd.isna(income.get('name')) or str(income['name']).strip() == '':
                errors.append(f"Row {idx + 1}: Income name cannot be empty")
            
            amount = income.get('annual_amount')
            if pd.isna(amount) or amount < 0:
                errors.append(f"Row {idx + 1}: Annual amount cannot be negative")
            
            start_age = income.get('start_age')
            end_age = income.get('end_age')
            
            if pd.isna(start_age) or start_age < 0 or start_age > 120:
                errors.append(f"Row {idx + 1}: Start age must be between 0 and 120")
            
            if pd.isna(end_age) or end_age < 0 or end_age > 120:
                errors.append(f"Row {idx + 1}: End age must be between 0 and 120")
            
            if not pd.isna(start_age) and not pd.isna(end_age) and start_age > end_age:
                errors.append(f"Row {idx + 1}: Start age must be less than or equal to end age")
            
            growth_rate = income.get('growth_rate')
            if pd.isna(growth_rate) or growth_rate < -50 or growth_rate > 50:
                errors.append(f"Row {idx + 1}: Growth rate must be between -50% and 50%")
        
        return errors
    
    @staticmethod
    def validate_expenses(expenses_df: pd.DataFrame) -> List[str]:
        """Validate expense data and return list of error messages"""
        errors = []
        
        for idx, expense in expenses_df.iterrows():
            if pd.isna(expense.get('name')) or str(expense['name']).strip() == '':
                errors.append(f"Row {idx + 1}: Expense name cannot be empty")
            
            amount = expense.get('annual_amount')
            if pd.isna(amount) or amount < 0:
                errors.append(f"Row {idx + 1}: Annual amount cannot be negative")
            
            start_age = expense.get('start_age')
            end_age = expense.get('end_age')
            
            if pd.isna(start_age) or start_age < 0 or start_age > 120:
                errors.append(f"Row {idx + 1}: Start age must be between 0 and 120")
            
            if pd.isna(end_age) or end_age < 0 or end_age > 120:
                errors.append(f"Row {idx + 1}: End age must be between 0 and 120")
            
            if not pd.isna(start_age) and not pd.isna(end_age) and start_age > end_age:
                errors.append(f"Row {idx + 1}: Start age must be less than or equal to end age (equal ages are valid for one-time expenses)")
            
            growth_rate = expense.get('growth_rate')
            if pd.isna(growth_rate) or growth_rate < -50 or growth_rate > 50:
                errors.append(f"Row {idx + 1}: Growth rate must be between -50% and 50%")
        
        return errors
    
    @staticmethod
    def validate_scenario(scenario_dict: Dict[str, Any]) -> List[str]:
        """Validate complete scenario and return list of error messages"""
        errors = []
        
        return errors
    
    @staticmethod
    def validate_all_data(people_df, accounts_df, real_estate_df, income_df, expenses_df, scenario) -> Tuple[bool, List[str]]:
        """Validate all data and return (is_valid, error_messages)"""
        all_errors = []
        
        all_errors.extend(DataValidator.validate_people(people_df))
        all_errors.extend(DataValidator.validate_accounts(accounts_df))
        all_errors.extend(DataValidator.validate_real_estate(real_estate_df))
        all_errors.extend(DataValidator.validate_income(income_df))
        all_errors.extend(DataValidator.validate_expenses(expenses_df))
        all_errors.extend(DataValidator.validate_scenario(scenario))
        
        return len(all_errors) == 0, all_errors