"""
dto/schemas.py — Data Transfer Objects для передачі даних між шарами.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateCustomerDTO:
    name: str
    email: str


@dataclass
class CreateDishDTO:
    name: str
    price: float


@dataclass
class PlaceOrderDTO:
    customer_id: str
    dish_ids: List[str]
    order_type: str = "regular"   # "regular" | "bulk"


@dataclass
class OrderResponseDTO:
    order_id: str
    customer_name: str
    items: List[str]
    total: float
    order_type: str
    status: str


@dataclass
class CustomerResponseDTO:
    customer_id: str
    name: str
    email: str


@dataclass
class DishResponseDTO:
    dish_id: str
    name: str
    price: float
