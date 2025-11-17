"""
Enhanced expense validation service to prevent age mapping errors and other data inconsistencies.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import warnings

class ExpenseValidationService:
    """Service for validating expense data integrity and consistency"""
    
    @staticmethod
    def validate_expense_age_consistency(expenses_df: pd.DataFrame, people_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate that expense age ranges are consistent with the assigned person.
        
        Returns:
            List of validation issues found
        """
        issues = []
        
        people_lookup = {row['name']: row['current_age'] for _, row in people_df.iterrows()}
        
        for idx, expense in expenses_df.iterrows():
            person_name = expense['person']
            start_age = expense['start_age']
            end_age = expense['end_age']
            expense_name = expense['name']
            
            if person_name == 'Joint':
                continue
                
            if person_name not in people_lookup:
                issues.append({
                    'type': 'missing_person',
                    'severity': 'error',
                    'expense': expense_name,
                    'message': f"Person '{person_name}' not found in people data",
                    'row': idx
                })
                continue
            
            person_current_age = people_lookup[person_name]
            
            if start_age > end_age:
                issues.append({
                    'type': 'invalid_age_range',
                    'severity': 'error',
                    'expense': expense_name,
                    'message': f"Start age ({start_age}) > end age ({end_age})",
                    'row': idx
                })
            
            if person_current_age < 18:
                if start_age > 25 or end_age > 25:
                    issues.append({
                        'type': 'suspicious_child_age',
                        'severity': 'warning',
                        'expense': expense_name,
                        'message': f"Child '{person_name}' (age {person_current_age}) has expense with age range {start_age}-{end_age}. This may be using parent ages instead of child ages.",
                        'row': idx
                    })
            
            if person_current_age < start_age and (start_age - person_current_age) > 50:
                issues.append({
                    'type': 'suspicious_future_age',
                    'severity': 'warning', 
                    'expense': expense_name,
                    'message': f"Person '{person_name}' (age {person_current_age}) has expense starting at age {start_age}. This seems unusually far in the future.",
                    'row': idx
                })
            
            if person_current_age > end_age and 'College' not in expense_name:
                issues.append({
                    'type': 'expired_expense',
                    'severity': 'warning',
                    'expense': expense_name,
                    'message': f"Person '{person_name}' (age {person_current_age}) has expense ending at age {end_age}. This expense period has already passed.",
                    'row': idx
                })
        
        return issues
    
    @staticmethod
    def validate_income_age_consistency(income_df: pd.DataFrame, people_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate that income age ranges are consistent with the assigned person.
        
        Returns:
            List of validation issues found
        """
        issues = []
        
        people_lookup = {row['name']: row['current_age'] for _, row in people_df.iterrows()}
        
        for idx, income in income_df.iterrows():
            person_name = income['person']
            start_age = income['start_age']
            end_age = income['end_age']
            income_name = income['name']
            
            if person_name == 'Joint':
                continue
                
            if person_name not in people_lookup:
                issues.append({
                    'type': 'missing_person',
                    'severity': 'error',
                    'income': income_name,
                    'message': f"Person '{person_name}' not found in people data",
                    'row': idx
                })
                continue
            
            person_current_age = people_lookup[person_name]
            
            if start_age > end_age:
                issues.append({
                    'type': 'invalid_age_range',
                    'severity': 'error',
                    'income': income_name,
                    'message': f"Start age ({start_age}) > end age ({end_age})",
                    'row': idx
                })
            
            if 'Social Security' not in income_name and 'Pension' not in income_name:
                if start_age < 16:
                    issues.append({
                        'type': 'early_work_age',
                        'severity': 'warning',
                        'income': income_name,
                        'message': f"Working income starting at age {start_age} is unusually early",
                        'row': idx
                    })
                
                if end_age > 75:
                    issues.append({
                        'type': 'late_work_age',
                        'severity': 'warning',
                        'income': income_name,
                        'message': f"Working income ending at age {end_age} is unusually late",
                        'row': idx
                    })
        
        return issues
    
    @staticmethod
    def validate_account_consistency(accounts_df: pd.DataFrame, people_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate that account data is consistent and realistic.
        
        Returns:
            List of validation issues found
        """
        issues = []
        
        people_lookup = {row['name']: row['current_age'] for _, row in people_df.iterrows()}
        
        for idx, account in accounts_df.iterrows():
            account_owner = account['account_owner']
            account_type = account['account_type']
            current_balance = account['current_balance']
            aggressive_rate = account.get('aggressive_rate', 0)
            conservative_rate = account.get('conservative_rate', 0)
            transition_start = account.get('transition_start_age', 50)
            transition_end = account.get('transition_end_age', 65)
            
            if account_owner != 'Joint' and account_owner not in people_lookup:
                issues.append({
                    'type': 'missing_person',
                    'severity': 'error',
                    'account': f"{account_type} ({account_owner})",
                    'message': f"Account owner '{account_owner}' not found in people data",
                    'row': idx
                })
                continue
            
            if transition_start >= transition_end:
                issues.append({
                    'type': 'invalid_transition_ages',
                    'severity': 'error',
                    'account': f"{account_type} ({account_owner})",
                    'message': f"Transition start age ({transition_start}) >= end age ({transition_end})",
                    'row': idx
                })
            
            if aggressive_rate < 0 or aggressive_rate > 20.0:
                issues.append({
                    'type': 'unrealistic_growth_rate',
                    'severity': 'warning',
                    'account': f"{account_type} ({account_owner})",
                    'message': f"Aggressive rate {aggressive_rate:.1f}% is outside typical range (0-20%)",
                    'row': idx
                })
            
            if conservative_rate < 0 or conservative_rate > 15.0:
                issues.append({
                    'type': 'unrealistic_growth_rate',
                    'severity': 'warning',
                    'account': f"{account_type} ({account_owner})",
                    'message': f"Conservative rate {conservative_rate:.1f}% is outside typical range (0-15%)",
                    'row': idx
                })
            
            if conservative_rate > aggressive_rate:
                issues.append({
                    'type': 'inverted_growth_rates',
                    'severity': 'warning',
                    'account': f"{account_type} ({account_owner})",
                    'message': f"Conservative rate ({conservative_rate:.1f}%) > aggressive rate ({aggressive_rate:.1f}%)",
                    'row': idx
                })
            
            if current_balance < 0:
                issues.append({
                    'type': 'negative_balance',
                    'severity': 'error',
                    'account': f"{account_type} ({account_owner})",
                    'message': f"Current balance cannot be negative: ${current_balance:,.2f}",
                    'row': idx
                })
        
        return issues
    
    @staticmethod
    def run_comprehensive_validation() -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all validation checks on current session state data.
        
        Returns:
            Dictionary with validation results for each data type
        """
        results = {
            'expenses': [],
            'income': [],
            'accounts': []
        }
        
        try:
            if hasattr(st.session_state, 'expenses_df') and hasattr(st.session_state, 'people_df'):
                results['expenses'] = ExpenseValidationService.validate_expense_age_consistency(
                    st.session_state.expenses_df, st.session_state.people_df
                )
            
            if hasattr(st.session_state, 'income_df') and hasattr(st.session_state, 'people_df'):
                results['income'] = ExpenseValidationService.validate_income_age_consistency(
                    st.session_state.income_df, st.session_state.people_df
                )
            
            if hasattr(st.session_state, 'accounts_df') and hasattr(st.session_state, 'people_df'):
                results['accounts'] = ExpenseValidationService.validate_account_consistency(
                    st.session_state.accounts_df, st.session_state.people_df
                )
            
        except Exception as e:
            for category in results:
                results[category].append({
                    'type': 'validation_error',
                    'severity': 'error',
                    'message': f"Validation failed: {str(e)}",
                    'row': None
                })
        
        return results
    
    @staticmethod
    def display_validation_results(validation_results: Dict[str, List[Dict[str, Any]]]):
        """
        Display validation results in Streamlit UI with appropriate styling.
        """
        total_issues = sum(len(issues) for issues in validation_results.values())
        
        if total_issues == 0:
            st.success("✅ All data validation checks passed!")
            return
        
        error_count = 0
        warning_count = 0
        
        for category_issues in validation_results.values():
            for issue in category_issues:
                if issue['severity'] == 'error':
                    error_count += 1
                else:
                    warning_count += 1
        
        if error_count > 0:
            st.error(f"❌ Found {error_count} errors and {warning_count} warnings in data validation")
        else:
            st.warning(f"⚠️ Found {warning_count} warnings in data validation")
        
        for category, issues in validation_results.items():
            if not issues:
                continue
                
            with st.expander(f"📋 {category.title()} Issues ({len(issues)})"):
                for issue in issues:
                    if issue['severity'] == 'error':
                        st.error(f"**Error:** {issue['message']}")
                    else:
                        st.warning(f"**Warning:** {issue['message']}")
                    
                    if issue.get('row') is not None:
                        st.caption(f"Row: {issue['row'] + 1}")
