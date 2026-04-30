"""
tests/test_services.py — модульні тести бізнес-логіки (15 тестів).

Покриття:
  TestCustomerService  (4 тести) — реєстрація, дублікат, отримання, видалення
  TestMenuService      (3 тести) — додавання, пошук, порожній запит
  TestOrderService     (8 тестів) — розміщення, помилки, скасування, bulk, підтвердження
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest

from models.entities import OrderStatus
from src.repositories.repositories import (
    InMemoryCustomerRepository,
    InMemoryDishRepository,
    InMemoryOrderRepository,
)
from src.services.services import CustomerService, MenuService, OrderService
from dto.schemas import (
    CreateCustomerDTO, CreateDishDTO, PlaceOrderDTO
)


def _make_services():
    """Допоміжна фабрика — свіжі репозиторії для кожного тесту."""
    cust_repo  = InMemoryCustomerRepository()
    dish_repo  = InMemoryDishRepository()
    order_repo = InMemoryOrderRepository()
    return (
        CustomerService(cust_repo),
        MenuService(dish_repo),
        OrderService(cust_repo, dish_repo, order_repo),
        cust_repo, dish_repo, order_repo,
    )


# ═══════════════════════════════════════════════════════
# 1. CustomerService
# ═══════════════════════════════════════════════════════
class TestCustomerService(unittest.TestCase):

    def setUp(self):
        self.cs, self.ms, self.os_, *_ = _make_services()

    def test_register_customer_success(self):
        """Тест 1: Успішна реєстрація клієнта."""
        dto = CreateCustomerDTO(name="Alice", email="alice@example.com")
        result = self.cs.register_customer(dto)
        self.assertEqual(result.name, "Alice")
        self.assertEqual(result.email, "alice@example.com")
        self.assertIsNotNone(result.customer_id)

    def test_register_duplicate_email_raises(self):
        """Тест 2: Реєстрація з існуючим email → ValueError."""
        dto = CreateCustomerDTO(name="Alice", email="alice@example.com")
        self.cs.register_customer(dto)
        with self.assertRaises(ValueError) as ctx:
            self.cs.register_customer(CreateCustomerDTO(name="Alice2", email="alice@example.com"))
        self.assertIn("already exists", str(ctx.exception))

    def test_get_customer_not_found_raises(self):
        """Тест 3: Отримання неіснуючого клієнта → ValueError."""
        with self.assertRaises(ValueError):
            self.cs.get_customer("nonexistent-id")

    def test_delete_customer_success(self):
        """Тест 4: Видалення клієнта."""
        dto = CreateCustomerDTO(name="Bob", email="bob@example.com")
        result = self.cs.register_customer(dto)
        deleted = self.cs.delete_customer(result.customer_id)
        self.assertTrue(deleted)
        with self.assertRaises(ValueError):
            self.cs.get_customer(result.customer_id)


# ═══════════════════════════════════════════════════════
# 2. MenuService
# ═══════════════════════════════════════════════════════
class TestMenuService(unittest.TestCase):

    def setUp(self):
        _, self.ms, *_ = _make_services()

    def test_add_dish_success(self):
        """Тест 5: Успішне додавання страви."""
        dto = CreateDishDTO(name="Pizza", price=150.0)
        result = self.ms.add_dish(dto)
        self.assertEqual(result.name, "Pizza")
        self.assertEqual(result.price, 150.0)
        self.assertIsNotNone(result.dish_id)

    def test_search_dishes_partial_match(self):
        """Тест 6: Пошук страв за частковою назвою."""
        self.ms.add_dish(CreateDishDTO("Pasta Carbonara", 120.0))
        self.ms.add_dish(CreateDishDTO("Pasta Bolognese", 130.0))
        self.ms.add_dish(CreateDishDTO("Pizza", 150.0))
        results = self.ms.search_dishes("pasta")
        self.assertEqual(len(results), 2)

    def test_search_empty_query_raises(self):
        """Тест 7: Порожній пошуковий запит → ValueError."""
        with self.assertRaises(ValueError):
            self.ms.search_dishes("   ")


# ═══════════════════════════════════════════════════════
# 3. OrderService
# ═══════════════════════════════════════════════════════
class TestOrderService(unittest.TestCase):

    def setUp(self):
        self.cs, self.ms, self.os_, *_ = _make_services()
        # Реєструємо клієнта і страви для всіх тестів
        cust = self.cs.register_customer(
            CreateCustomerDTO("Hanna", "hanna@example.com"))
        self.cid = cust.customer_id

        d1 = self.ms.add_dish(CreateDishDTO("Pizza", 150.0))
        d2 = self.ms.add_dish(CreateDishDTO("Pasta", 120.0))
        self.did1 = d1.dish_id
        self.did2 = d2.dish_id

    def test_place_order_success(self):
        """Тест 8: Успішне розміщення замовлення."""
        dto = PlaceOrderDTO(customer_id=self.cid, dish_ids=[self.did1])
        result = self.os_.place_order(dto)
        self.assertEqual(result.customer_name, "Hanna")
        self.assertEqual(result.status, "pending")
        self.assertIn("Pizza", result.items)

    def test_place_order_unknown_customer_raises(self):
        """Тест 9: Замовлення від неіснуючого клієнта → ValueError."""
        dto = PlaceOrderDTO(customer_id="ghost-id", dish_ids=[self.did1])
        with self.assertRaises(ValueError) as ctx:
            self.os_.place_order(dto)
        self.assertIn("not found", str(ctx.exception))

    def test_place_order_unknown_dish_raises(self):
        """Тест 10: Замовлення з неіснуючою стравою → ValueError."""
        dto = PlaceOrderDTO(customer_id=self.cid, dish_ids=["ghost-dish-id"])
        with self.assertRaises(ValueError) as ctx:
            self.os_.place_order(dto)
        self.assertIn("not found", str(ctx.exception))

    def test_place_order_empty_dishes_raises(self):
        """Тест 11: Порожній список страв → ValueError."""
        dto = PlaceOrderDTO(customer_id=self.cid, dish_ids=[])
        with self.assertRaises(ValueError):
            self.os_.place_order(dto)

    def test_cancel_order_success(self):
        """Тест 12: Успішне скасування замовлення."""
        dto = PlaceOrderDTO(customer_id=self.cid, dish_ids=[self.did1])
        order = self.os_.place_order(dto)
        cancelled = self.os_.cancel_order(order.order_id)
        self.assertEqual(cancelled.status, "cancelled")

    def test_cancel_already_cancelled_raises(self):
        """Тест 13: Повторне скасування → ValueError."""
        dto = PlaceOrderDTO(customer_id=self.cid, dish_ids=[self.did1])
        order = self.os_.place_order(dto)
        self.os_.cancel_order(order.order_id)
        with self.assertRaises(ValueError) as ctx:
            self.os_.cancel_order(order.order_id)
        self.assertIn("already cancelled", str(ctx.exception))

    def test_bulk_order_applies_discount(self):
        """Тест 14: BulkOrder застосовує 10% знижку."""
        dto = PlaceOrderDTO(
            customer_id=self.cid,
            dish_ids=[self.did1, self.did2],
            order_type="bulk",
        )
        result = self.os_.place_order(dto)
        # Pizza 150 + Pasta 120 = 270; знижка 10% → 243.0
        self.assertAlmostEqual(result.total, 243.0)
        self.assertEqual(result.order_type, "bulk")

    def test_get_customer_orders(self):
        """Тест 15: Отримання всіх замовлень клієнта."""
        self.os_.place_order(PlaceOrderDTO(self.cid, [self.did1]))
        self.os_.place_order(PlaceOrderDTO(self.cid, [self.did2]))
        orders = self.os_.get_customer_orders(self.cid)
        self.assertEqual(len(orders), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
