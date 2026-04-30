"""
services/ — шар бізнес-логіки.

Реалізовані сценарії:
  1. Реєстрація клієнта        (register_customer)
  2. Додавання страви в меню   (add_dish)
  3. Розміщення замовлення     (place_order)
  4. Скасування замовлення     (cancel_order)
  5. Пошук страв               (search_dishes)
  6. Отримання замовлень клієнта (get_customer_orders)
"""
from __future__ import annotations
from typing import List

from models.entities import Customer, Dish, Order, OrderStatus, OrderType
from src.repositories.repositories import (
    ICustomerRepository,
    IDishRepository,
    IOrderRepository,
)
from dto.schemas import (
    CreateCustomerDTO,
    CreateDishDTO,
    PlaceOrderDTO,
    OrderResponseDTO,
    CustomerResponseDTO,
    DishResponseDTO,
)


class CustomerService:
    """Сценарій 1: Реєстрація та управління клієнтами."""

    def __init__(self, repo: ICustomerRepository) -> None:
        self._repo = repo

    def register_customer(self, dto: CreateCustomerDTO) -> CustomerResponseDTO:
        """Реєструє нового клієнта. Перевіряє унікальність email."""
        if self._repo.find_by_email(dto.email):
            raise ValueError(f"Customer with email '{dto.email}' already exists")

        customer = Customer(name=dto.name, email=dto.email)
        self._repo.save(customer)
        return CustomerResponseDTO(
            customer_id=customer.customer_id,
            name=customer.name,
            email=customer.email,
        )

    def get_customer(self, customer_id: str) -> CustomerResponseDTO:
        customer = self._repo.find_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer '{customer_id}' not found")
        return CustomerResponseDTO(
            customer_id=customer.customer_id,
            name=customer.name,
            email=customer.email,
        )

    def delete_customer(self, customer_id: str) -> bool:
        if not self._repo.find_by_id(customer_id):
            raise ValueError(f"Customer '{customer_id}' not found")
        return self._repo.delete(customer_id)


class MenuService:
    """Сценарій 2: Управління меню."""

    def __init__(self, repo: IDishRepository) -> None:
        self._repo = repo

    def add_dish(self, dto: CreateDishDTO) -> DishResponseDTO:
        """Додає страву до меню."""
        dish = Dish(name=dto.name, price=dto.price)
        self._repo.save(dish)
        return DishResponseDTO(
            dish_id=dish.dish_id,
            name=dish.name,
            price=dish.price,
        )

    def search_dishes(self, query: str) -> List[DishResponseDTO]:
        """Сценарій 5: Пошук страв за назвою (частковий збіг)."""
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        dishes = self._repo.find_by_name(query)
        return [DishResponseDTO(dish_id=d.dish_id, name=d.name, price=d.price)
                for d in dishes]

    def get_all_dishes(self) -> List[DishResponseDTO]:
        return [DishResponseDTO(dish_id=d.dish_id, name=d.name, price=d.price)
                for d in self._repo.find_all()]


class OrderService:
    """Сценарії 3, 4, 6: Розміщення, скасування та перегляд замовлень."""

    def __init__(
        self,
        customer_repo: ICustomerRepository,
        dish_repo: IDishRepository,
        order_repo: IOrderRepository,
    ) -> None:
        self._customers = customer_repo
        self._dishes = dish_repo
        self._orders = order_repo

    def place_order(self, dto: PlaceOrderDTO) -> OrderResponseDTO:
        """
        Сценарій 3: Розміщення замовлення.
        Бізнес-правила:
          - клієнт повинен існувати
          - всі страви повинні існувати
          - замовлення не може бути порожнім
        """
        customer = self._customers.find_by_id(dto.customer_id)
        if not customer:
            raise ValueError(f"Customer '{dto.customer_id}' not found")

        if not dto.dish_ids:
            raise ValueError("Order must contain at least one dish")

        dishes: List[Dish] = []
        for dish_id in dto.dish_ids:
            dish = self._dishes.find_by_id(dish_id)
            if not dish:
                raise ValueError(f"Dish '{dish_id}' not found in menu")
            dishes.append(dish)

        order_type = (OrderType.BULK
                      if dto.order_type == "bulk"
                      else OrderType.REGULAR)

        order = Order(
            customer=customer,
            items=dishes,
            order_type=order_type,
        )
        self._orders.save(order)

        return self._to_response_dto(order)

    def cancel_order(self, order_id: str) -> OrderResponseDTO:
        """
        Сценарій 4: Скасування замовлення.
        Бізнес-правило: не можна скасувати вже скасоване замовлення.
        """
        order = self._orders.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found")
        if order.status == OrderStatus.CANCELLED:
            raise ValueError("Order is already cancelled")

        order.status = OrderStatus.CANCELLED
        self._orders.update(order)
        return self._to_response_dto(order)

    def confirm_order(self, order_id: str) -> OrderResponseDTO:
        """Підтверджує замовлення."""
        order = self._orders.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found")
        if order.status == OrderStatus.CANCELLED:
            raise ValueError("Cannot confirm a cancelled order")

        order.status = OrderStatus.CONFIRMED
        self._orders.update(order)
        return self._to_response_dto(order)

    def get_customer_orders(self, customer_id: str) -> List[OrderResponseDTO]:
        """Сценарій 6: Отримання всіх замовлень клієнта."""
        if not self._customers.find_by_id(customer_id):
            raise ValueError(f"Customer '{customer_id}' not found")
        orders = self._orders.find_by_customer(customer_id)
        return [self._to_response_dto(o) for o in orders]

    def get_order(self, order_id: str) -> OrderResponseDTO:
        order = self._orders.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found")
        return self._to_response_dto(order)

    @staticmethod
    def _to_response_dto(order: Order) -> OrderResponseDTO:
        return OrderResponseDTO(
            order_id=order.order_id,
            customer_name=order.customer.name,
            items=[d.name for d in order.items],
            total=order.total(),
            order_type=order.order_type.value,
            status=order.status.value,
        )
