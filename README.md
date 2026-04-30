# Лабораторна робота 5 — Бізнес-логіка, сервіси, unit-тестування

## Структура проєкту

```
lab5/
├── src/
│   ├── models/
│   │   └── entities.py          # Dish, Customer, Order, Enum-и
│   ├── dto/
│   │   └── schemas.py           # DTO (CreateCustomerDTO, PlaceOrderDTO …)
│   ├── repositories/
│   │   └── repositories.py      # Інтерфейси + InMemory-реалізації
│   ├── services/
│   │   └── services.py          # Бізнес-логіка (CustomerService, MenuService, OrderService)
│   └── controllers/
│       └── restaurant_controller.py  # CLI-контролер (точка входу)
└── tests/
    └── test_services.py         # 15 модульних тестів
```

## Запуск тестів

```bash
# з кореня проєкту lab5/
python -m pytest tests/test_services.py -v
```

### Очікуваний результат

```
collected 15 items

tests/test_services.py::TestCustomerService::test_register_customer_success     PASSED
tests/test_services.py::TestCustomerService::test_register_duplicate_email_raises PASSED
tests/test_services.py::TestCustomerService::test_get_customer_not_found_raises  PASSED
tests/test_services.py::TestCustomerService::test_delete_customer_success        PASSED
tests/test_services.py::TestMenuService::test_add_dish_success                   PASSED
tests/test_services.py::TestMenuService::test_search_dishes_partial_match        PASSED
tests/test_services.py::TestMenuService::test_search_empty_query_raises          PASSED
tests/test_services.py::TestOrderService::test_place_order_success               PASSED
tests/test_services.py::TestOrderService::test_place_order_unknown_customer_raises PASSED
tests/test_services.py::TestOrderService::test_place_order_unknown_dish_raises   PASSED
tests/test_services.py::TestOrderService::test_place_order_empty_dishes_raises   PASSED
tests/test_services.py::TestOrderService::test_cancel_order_success              PASSED
tests/test_services.py::TestOrderService::test_cancel_already_cancelled_raises   PASSED
tests/test_services.py::TestOrderService::test_bulk_order_applies_discount       PASSED
tests/test_services.py::TestOrderService::test_get_customer_orders               PASSED

======================== 15 passed in 0.10s ================================
```

## Запуск демо CLI

```bash
cd src
python controllers/restaurant_controller.py
```

## Бізнес-сценарії

| # | Сценарій | Сервіс | Метод |
|---|---|---|---|
| 1 | Реєстрація клієнта | CustomerService | register_customer() |
| 2 | Додавання страви в меню | MenuService | add_dish() |
| 3 | Розміщення замовлення | OrderService | place_order() |
| 4 | Скасування замовлення | OrderService | cancel_order() |
| 5 | Пошук страв | MenuService | search_dishes() |
| 6 | Замовлення клієнта | OrderService | get_customer_orders() |
