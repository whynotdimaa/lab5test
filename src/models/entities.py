"""
models/entities.py — доменні моделі системи ресторану.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
import uuid


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class OrderType(Enum):
    REGULAR = "regular"
    BULK = "bulk"


@dataclass
class Dish:
    name: str
    price: float
    dish_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Dish name cannot be empty")
        if self.price < 0:
            raise ValueError("Price cannot be negative")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Dish) and self.dish_id == other.dish_id

    def __hash__(self) -> int:
        return hash(self.dish_id)


@dataclass
class Customer:
    name: str
    email: str
    customer_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Customer name cannot be empty")
        if "@" not in self.email:
            raise ValueError("Invalid email address")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Customer) and self.customer_id == other.customer_id

    def __hash__(self) -> int:
        return hash(self.customer_id)


@dataclass
class Order:
    customer: Customer
    items: List[Dish]
    order_type: OrderType = OrderType.REGULAR
    status: OrderStatus = OrderStatus.PENDING
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    BULK_DISCOUNT = 0.10

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("Order must contain at least one dish")

    def total(self) -> float:
        subtotal = sum(d.price for d in self.items)
        if self.order_type == OrderType.BULK:
            return round(subtotal * (1 - self.BULK_DISCOUNT), 2)
        return round(subtotal, 2)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Order) and self.order_id == other.order_id

    def __hash__(self) -> int:
        return hash(self.order_id)
