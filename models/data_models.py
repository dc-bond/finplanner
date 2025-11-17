"""
Data models with type safety for the financial planning application.
Uses dataclasses for better structure and type hints for clarity.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class GrowthStrategy(Enum):
    FIXED = "Fixed"
    TARGET_DATE = "Target Date"



@dataclass
class Person:
    """Represents a person in the financial plan"""
    name: str
    current_age: int
    
    def __post_init__(self):
        if self.current_age < 0 or self.current_age > 120:
            raise ValueError(f"Age must be between 0 and 120, got {self.current_age}")


@dataclass
class Account:
    """Represents a financial account"""
    account_type: str
    account_owner: str
    current_balance: float
    growth_strategy: GrowthStrategy
    aggressive_rate: float
    conservative_rate: float
    transition_start_age: int
    transition_end_age: int
    
    def __post_init__(self):
        if self.current_balance < 0:
            raise ValueError(f"Account balance cannot be negative: {self.current_balance}")
        if self.transition_start_age >= self.transition_end_age:
            raise ValueError("Transition start age must be less than end age")


@dataclass
class IncomeSource:
    """Represents an income source"""
    name: str
    person: str
    annual_amount: float
    start_age: int
    end_age: int
    growth_rate: float
    
    def __post_init__(self):
        if self.annual_amount < 0:
            raise ValueError(f"Income amount cannot be negative: {self.annual_amount}")
        if self.start_age > self.end_age:
            raise ValueError("Start age must be less than or equal to end age")


@dataclass
class Expense:
    """Represents an expense"""
    name: str
    person: str
    annual_amount: float
    start_age: int
    end_age: int
    growth_rate: float
    
    def __post_init__(self):
        if self.annual_amount < 0:
            raise ValueError(f"Expense amount cannot be negative: {self.annual_amount}")
        if self.start_age > self.end_age:
            raise ValueError("Start age must be less than or equal to end age")


@dataclass
class RealEstateProperty:
    """Represents a real estate property"""
    property_name: str
    address: str
    purchase_year: int
    purchase_price: float
    down_payment_percent: float
    mortgage_rate: float
    mortgage_term_years: int
    appreciation_rate: float
    sale_year: Optional[int] = None
    current_value: Optional[float] = None
    current_mortgage_balance: Optional[float] = None
    is_existing_property: bool = False
    
    def __post_init__(self):
        if self.purchase_price <= 0:
            raise ValueError(f"Purchase price must be positive: {self.purchase_price}")
        if not 0 <= self.down_payment_percent <= 1:
            raise ValueError(f"Down payment percent must be between 0 and 1: {self.down_payment_percent}")
        if self.sale_year and self.sale_year <= self.purchase_year:
            raise ValueError("Sale year must be after purchase year")


@dataclass
class FinancialScenario:
    """Represents a complete financial scenario"""
    current_year: int
    current_age: int
    max_projection_age: int
    people: List[Person]
    accounts: List[Account]
    income_sources: List[IncomeSource]
    expenses: List[Expense]
    real_estate: List[RealEstateProperty]
    
    def __post_init__(self):
        if self.current_age >= self.max_projection_age:
            raise ValueError("Current age must be less than max projection age")


@dataclass
class ProjectionResult:
    """Represents the result of a financial projection for one year"""
    age: int
    year: int
    income: float
    expenses: float
    net_cashflow: float
    real_estate_sales: float
    portfolio_contribution: float
    portfolio_return_amount: float
    portfolio_balance: float
    real_estate_equity: float
    total_net_worth: float


@dataclass
class SuccessMetrics:
    """Represents success metrics from a projection"""
    final_balance: float
    years_solvent: int
    first_deficit_age: Optional[float]
    total_contributions: float
    total_withdrawals: float
    total_investment_gains: float




def person_from_dict(data: Dict[str, Any]) -> Person:
    """Create Person from dictionary"""
    return Person(
        name=data['name'],
        current_age=int(data['current_age'])
    )


def account_from_dict(data: Dict[str, Any]) -> Account:
    """Create Account from dictionary"""
    return Account(
        account_type=data['account_type'],
        account_owner=data['account_owner'],
        current_balance=float(data['current_balance']),
        growth_strategy=GrowthStrategy(data['growth_strategy']),
        aggressive_rate=float(data['aggressive_rate']),
        conservative_rate=float(data['conservative_rate']),
        transition_start_age=int(data['transition_start_age']),
        transition_end_age=int(data['transition_end_age'])
    )


def income_from_dict(data: Dict[str, Any]) -> IncomeSource:
    """Create IncomeSource from dictionary"""
    return IncomeSource(
        name=data['name'],
        person=data['person'],
        annual_amount=float(data['annual_amount']),
        start_age=int(data['start_age']),
        end_age=int(data['end_age']),
        growth_rate=float(data['growth_rate'])
    )


def expense_from_dict(data: Dict[str, Any]) -> Expense:
    """Create Expense from dictionary"""
    return Expense(
        name=data['name'],
        person=data['person'],
        annual_amount=float(data['annual_amount']),
        start_age=int(data['start_age']),
        end_age=int(data['end_age']),
        growth_rate=float(data['growth_rate'])
    )


def property_from_dict(data: Dict[str, Any]) -> RealEstateProperty:
    """Create RealEstateProperty from dictionary"""
    return RealEstateProperty(
        property_name=data['property_name'],
        address=data.get('address', ''),
        purchase_year=int(data['purchase_year']),
        purchase_price=float(data['purchase_price']),
        down_payment_percent=float(data['down_payment_percent']),
        mortgage_rate=float(data['mortgage_rate']),
        mortgage_term_years=int(data['mortgage_term_years']),
        appreciation_rate=float(data['appreciation_rate']),
        sale_year=int(data['sale_year']) if data.get('sale_year') is not None else None,
        current_value=float(data['current_value']) if data.get('current_value') is not None else None,
        current_mortgage_balance=float(data['current_mortgage_balance']) if data.get('current_mortgage_balance') is not None else None,
        is_existing_property=bool(data.get('is_existing_property', False))
    )