"""
controllers/restaurant_controller.py — точка входу (CLI-контролер).

Контролер лише:
  - приймає вхідні дані від користувача
  - формує DTO
  - передає до сервісу
  - виводить результат

Жодної бізнес-логіки тут немає.
"""
from __future__ import annotations

from src.dto.schemas import CreateCustomerDTO, CreateDishDTO, PlaceOrderDTO
from src.services.services import CustomerService, MenuService, OrderService


class RestaurantController:
    """CLI-контролер системи ресторану."""

    def __init__(
        self,
        customer_service: CustomerService,
        menu_service: MenuService,
        order_service: OrderService,
    ) -> None:
        self._customers = customer_service
        self._menu = menu_service
        self._orders = order_service

    # ── Customer endpoints ─────────────────────────────────────

    def register_customer(self, name: str, email: str) -> dict:
        try:
            dto = CreateCustomerDTO(name=name, email=email)
            result = self._customers.register_customer(dto)
            return {"success": True, "data": result}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def get_customer(self, customer_id: str) -> dict:
        try:
            result = self._customers.get_customer(customer_id)
            return {"success": True, "data": result}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    # ── Menu endpoints ─────────────────────────────────────────

    def add_dish(self, name: str, price: float) -> dict:
        try:
            dto = CreateDishDTO(name=name, price=price)
            result = self._menu.add_dish(dto)
            return {"success": True, "data": result}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def search_dishes(self, query: str) -> dict:
        try:
            results = self._menu.search_dishes(query)
            return {"success": True, "data": results, "count": len(results)}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def list_menu(self) -> dict:
        results = self._menu.get_all_dishes()
        return {"success": True, "data": results, "count": len(results)}

    # ── Order endpoints ────────────────────────────────────────

    def place_order(
        self, customer_id: str, dish_ids: list, order_type: str = "regular"
    ) -> dict:
        try:
            dto = PlaceOrderDTO(
                customer_id=customer_id,
                dish_ids=dish_ids,
                order_type=order_type,
            )
            result = self._orders.place_order(dto)
            return {"success": True, "data": result}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def cancel_order(self, order_id: str) -> dict:
        try:
            result = self._orders.cancel_order(order_id)
            return {"success": True, "data": result}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def confirm_order(self, order_id: str) -> dict:
        try:
            result = self._orders.confirm_order(order_id)
            return {"success": True, "data": result}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def get_customer_orders(self, customer_id: str) -> dict:
        try:
            results = self._orders.get_customer_orders(customer_id)
            return {"success": True, "data": results, "count": len(results)}
        except ValueError as e:
            return {"success": False, "error": str(e)}


# ── Demo CLI ───────────────────────────────────────────────────

def _build_controller() -> RestaurantController:
    """Фабрична функція для збирання залежностей (Composition Root)."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from src.repositories.repositories import (
        InMemoryCustomerRepository,
        InMemoryDishRepository,
        InMemoryOrderRepository,
    )

    cust_repo  = InMemoryCustomerRepository()
    dish_repo  = InMemoryDishRepository()
    order_repo = InMemoryOrderRepository()

    return RestaurantController(
        customer_service=CustomerService(cust_repo),
        menu_service=MenuService(dish_repo),
        order_service=OrderService(cust_repo, dish_repo, order_repo),
    )


if __name__ == "__main__":
    ctrl = _build_controller()

    print("=== Реєстрація клієнтів ===")
    r1 = ctrl.register_customer("Alice", "alice@example.com")
    r2 = ctrl.register_customer("Bob",   "bob@example.com")
    print(r1)
    print(r2)

    print("\n=== Додавання страв ===")
    d1 = ctrl.add_dish("Pizza Margherita", 150.0)
    d2 = ctrl.add_dish("Pasta Carbonara",  120.0)
    d3 = ctrl.add_dish("Tiramisu",          80.0)
    print(d1); print(d2); print(d3)

    print("\n=== Пошук страв ===")
    print(ctrl.search_dishes("pasta"))

    print("\n=== Розміщення замовлення ===")
    cid = r1["data"].customer_id
    did1 = d1["data"].dish_id
    did2 = d2["data"].dish_id
    order = ctrl.place_order(cid, [did1, did2])
    print(order)

    print("\n=== Підтвердження замовлення ===")
    oid = order["data"].order_id
    print(ctrl.confirm_order(oid))

    print("\n=== Замовлення клієнта ===")
    print(ctrl.get_customer_orders(cid))

    print("\n=== Дублікат email (негативний кейс) ===")
    print(ctrl.register_customer("Alice2", "alice@example.com"))
