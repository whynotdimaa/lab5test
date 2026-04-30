"""
repositories/ — шар доступу до даних (in-memory реалізація).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from models.entities import Customer, Dish, Order


# ─── Interfaces ───────────────────────────────────────────────

class ICustomerRepository(ABC):
    @abstractmethod
    def save(self, customer: Customer) -> None: ...

    @abstractmethod
    def find_by_id(self, customer_id: str) -> Optional[Customer]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Customer]: ...

    @abstractmethod
    def find_all(self) -> List[Customer]: ...

    @abstractmethod
    def delete(self, customer_id: str) -> bool: ...


class IDishRepository(ABC):
    @abstractmethod
    def save(self, dish: Dish) -> None: ...

    @abstractmethod
    def find_by_id(self, dish_id: str) -> Optional[Dish]: ...

    @abstractmethod
    def find_by_name(self, name: str) -> List[Dish]: ...

    @abstractmethod
    def find_all(self) -> List[Dish]: ...


class IOrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]: ...

    @abstractmethod
    def find_all(self) -> List[Order]: ...

    @abstractmethod
    def update(self, order: Order) -> None: ...


# ─── In-memory implementations ───────────────────────────────

class InMemoryCustomerRepository(ICustomerRepository):
    """Зберігає клієнтів у пам'яті."""

    def __init__(self) -> None:
        self._store: Dict[str, Customer] = {}

    def save(self, customer: Customer) -> None:
        self._store[customer.customer_id] = customer

    def find_by_id(self, customer_id: str) -> Optional[Customer]:
        return self._store.get(customer_id)

    def find_by_email(self, email: str) -> Optional[Customer]:
        return next((c for c in self._store.values() if c.email == email), None)

    def find_all(self) -> List[Customer]:
        return list(self._store.values())

    def delete(self, customer_id: str) -> bool:
        if customer_id in self._store:
            del self._store[customer_id]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()


class InMemoryDishRepository(IDishRepository):
    """Зберігає страви у пам'яті."""

    def __init__(self) -> None:
        self._store: Dict[str, Dish] = {}

    def save(self, dish: Dish) -> None:
        self._store[dish.dish_id] = dish

    def find_by_id(self, dish_id: str) -> Optional[Dish]:
        return self._store.get(dish_id)

    def find_by_name(self, name: str) -> List[Dish]:
        name_lower = name.lower()
        return [d for d in self._store.values() if name_lower in d.name.lower()]

    def find_all(self) -> List[Dish]:
        return list(self._store.values())

    def clear(self) -> None:
        self._store.clear()


class InMemoryOrderRepository(IOrderRepository):
    """Зберігає замовлення у пам'яті."""

    def __init__(self) -> None:
        self._store: Dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.order_id] = order

    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._store.get(order_id)

    def find_by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._store.values()
                if o.customer.customer_id == customer_id]

    def find_all(self) -> List[Order]:
        return list(self._store.values())

    def update(self, order: Order) -> None:
        if order.order_id not in self._store:
            raise KeyError(f"Order {order.order_id} not found")
        self._store[order.order_id] = order

    def clear(self) -> None:
        self._store.clear()
