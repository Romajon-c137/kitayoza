# MASTER PROMPT FOR CODEX
## Wholesale Inventory, Sales & POS Management System

Ты выступаешь как **Senior Full-Stack Engineer / Software Architect / Product Engineer**.

Необходимо спроектировать и реализовать production-ready систему учета товаров, склада, оптовых продаж, прибыли и отчетности для компании, которая занимается преимущественно оптовой продажей сантехнических и строительных товаров.

Основные категории товаров:

- унитазы;
- раковины;
- смесители;
- душевые трапы;
- сливные системы;
- кафель;
- керамогранит;
- ванны;
- душевые системы;
- трубы;
- фитинги;
- аксессуары;
- другие сантехнические и строительные товары.

Система не должна быть перегруженной как полноценная ERP.

Главные цели:

1. Максимально простой учет прихода товара.
2. Максимально быстрая работа оператора при продаже.
3. Точный складской остаток.
4. Точный расчет выручки.
5. Точный расчет себестоимости проданного товара.
6. Точный расчет валовой прибыли.
7. История всех операций.
8. Удобная административная панель.
9. Удобные отчеты.
10. Разделение прав доступа.
11. Надежность финансовых и складских расчетов.
12. Возможность дальнейшего расширения системы.

---

# 1. TECHNOLOGY STACK

Использовать следующий стек.

## Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- Django Unfold для административной панели
- JWT или secure cookie based authentication
- Django permissions / groups
- Decimal для всех денежных вычислений
- database transactions
- row-level locking там, где требуется

## Frontend POS

- Next.js
- TypeScript
- App Router
- React
- современный UI
- responsive layout
- быстрый интерфейс кассы
- API integration с Django REST API

Для UI можно использовать качественную современную библиотеку компонентов, если это действительно упрощает разработку.

Предпочтительно:

- Tailwind CSS;
- shadcn/ui или аналогичное решение.

Но UI не должен выглядеть как перегруженный SaaS dashboard.

Главный приоритет:

> простота, скорость работы и минимальное количество действий оператора.

---

# 2. HIGH LEVEL ARCHITECTURE

Архитектура:

```text
                ┌──────────────────────┐
                │      Next.js POS     │
                │   Operator / Admin   │
                └──────────┬───────────┘
                           │
                        REST API
                           │
                ┌──────────▼───────────┐
                │        Django        │
                │ Django REST Framework│
                ├──────────────────────┤
                │    Django Unfold     │
                │    Admin Portal      │
                └──────────┬───────────┘
                           │
                    PostgreSQL
```

Backend является единственным источником истины.

Next.js не должен самостоятельно рассчитывать или изменять складские данные без проверки backend.

Все критические операции:

- продажа;
- возврат;
- приход;
- списание;
- корректировка;
- изменение исторической продажи;

должны валидироваться и проводиться на backend.

---

# 3. PROJECT STRUCTURE

Разделить Django-проект минимум на логические приложения:

```text
apps/
    accounts/
    products/
    inventory/
    purchases/
    sales/
    reports/
    audit/
```

При необходимости можно добавить:

```text
customers/
suppliers/
payments/
core/
```

Не создавать чрезмерное количество приложений без необходимости.

---

# 4. USERS AND ROLES

Минимальные роли:

## OPERATOR

Оператор работает преимущественно через Next.js POS.

Может:

- войти в систему;
- открыть кассу;
- искать товары;
- видеть доступный остаток;
- добавлять товары в продажу;
- менять количество;
- указывать фактическую цену продажи;
- указывать общую сумму позиции;
- создавать продажу;
- просматривать разрешенную историю продаж;
- видеть результат текущей продажи в рамках своих разрешений.

Не может:

- создавать пользователей;
- менять права;
- управлять системными настройками;
- создавать или изменять приход товара;
- произвольно менять склад;
- удалять продажи;
- менять старые продажи;
- редактировать себестоимость товара;
- управлять административной частью системы.

---

## ADMIN

Администратор имеет доступ:

- к Django Unfold;
- товарам;
- категориям;
- складским остаткам;
- приходам;
- продажам;
- отчетам;
- пользователям в рамках разрешений;
- возвратам;
- списаниям;
- складским корректировкам;
- себестоимости;
- прибыли;
- аудит-логу.

Администратор может корректировать исторические записи, если это действительно необходимо.

ВАЖНО:

История по умолчанию считается неизменяемой.

Любое административное изменение исторической продажи должно:

1. быть разрешено только пользователю с соответствующим permission;
2. сохранять старые значения;
3. сохранять новые значения;
4. сохранять пользователя, выполнившего изменение;
5. сохранять дату и время;
6. желательно требовать причину изменения;
7. корректно пересчитывать связанные складские и финансовые показатели.

Нельзя просто молча изменить старую продажу.

---

## SUPERADMIN

Полный системный доступ.

Может:

- управлять администраторами;
- управлять ролями;
- управлять permissions;
- выполнять системные административные операции.

---

# 5. AUTHENTICATION AND AUTHORIZATION

Backend должен проверять permissions самостоятельно.

Нельзя полагаться только на скрытие элементов frontend.

Даже если пользователь вручную отправит API request, backend обязан проверить права.

Реализовать:

- authentication;
- role-based access control;
- permissions;
- protected API routes;
- protected Next.js routes.

Пример:

```text
/operator/*
```

доступно оператору и администратору.

Административная Django-панель доступна только соответствующим пользователям.

---

# 6. PRODUCT MODEL

Создать качественную модель товара.

Минимальные поля:

```text
Product
- id
- sku
- name
- category
- brand
- model
- size
- color
- unit
- description
- image
- cost_price
- sale_price
- minimum_stock
- is_active
- created_at
- updated_at
```

Допускается адаптация структуры, если архитектурно это будет правильнее.

---

# 7. SKU

SKU должен быть уникальным.

Например:

```text
WC-MONACO-WHITE
TILE-CALACATTA-60120
DRAIN-CHROME-600
```

Если SKU не указан вручную, можно предусмотреть генерацию.

Не использовать название товара как уникальный идентификатор.

---

# 8. PRODUCT IMAGE

Каждый товар должен иметь возможность загрузки фотографии.

Фото используется:

- в Django Admin;
- в POS;
- в отчетах.

Если фото отсутствует, показывать placeholder.

Продумать:

- media storage;
- thumbnail;
- оптимизацию отображения.

---

# 9. PRODUCT UNIT

Не привязывать систему исключительно к штукам.

Предусмотреть единицы измерения:

```text
pcs
m2
meter
box
set
```

Отображаемые названия:

```text
шт.
м²
м
коробка
комплект
```

Количество должно поддерживать Decimal, потому что некоторые товары могут продаваться дробными значениями.

Например:

```text
12.5 м²
```

Не использовать IntegerField для количества во всей системе.

---

# 10. PRODUCT VARIANTS

Архитектура должна позволять в будущем нормально работать с вариантами.

Пример:

```text
Calacatta Gold

60x60
60x120
120x120
```

Если ProductVariant значительно усложняет MVP, допустимо на первом этапе создавать каждый вариант как отдельную складскую позицию.

Например:

```text
Calacatta Gold 60x60
Calacatta Gold 60x120
```

Но архитектура должна позволять перейти на Product + Variant.

Главное правило:

каждая складская позиция должна иметь собственные:

- SKU;
- остаток;
- себестоимость;
- цену продажи.

---

# 11. COST PRICE

На текущем этапе используется упрощенная модель себестоимости.

## Правило

У каждого товара есть:

```text
cost_price
```

Это текущая актуальная себестоимость одной единицы товара.

Например:

```text
Product:
Унитаз Monaco

cost_price = 800
sale_price = 1200
```

При создании продажи текущая себестоимость обязательно копируется в SaleItem.

Например:

```text
SaleItem.cost_price = 800
```

После сохранения продажи изменение `Product.cost_price` НЕ должно изменять старую продажу.

---

# 12. HISTORICAL COST SNAPSHOT

Это критически важное правило.

Допустим:

1 августа товар имел:

```text
cost_price = 800
```

Была совершена продажа.

После этого администратор поменял:

```text
Product.cost_price = 900
```

Старая продажа должна продолжать показывать:

```text
cost_price = 800
```

Поэтому SaleItem обязан содержать snapshot себестоимости.

---

# 13. FUTURE COST MODEL

Не реализовывать сейчас сложную партийную себестоимость:

- FIFO;
- LIFO;
- weighted average.

Но архитектуру не следует делать такой, чтобы дальнейшее добавление подобного учета потребовало полного переписывания sales subsystem.

На текущем этапе всегда используется актуальная единая себестоимость Product на момент проведения продажи.

---

# 14. DEFAULT SALE PRICE

Product содержит:

```text
sale_price
```

Это рекомендуемая / стандартная цена продажи.

Но фактическая цена продажи может отличаться.

Пример:

```text
sale_price = 1200
```

Оператор имеет право фактически продать товар:

```text
1000
```

В отчет должна попасть цена:

```text
1000
```

а не 1200.

---

# 15. INVENTORY ACCOUNTING

Не строить складской учет только на прямом изменении:

```text
product.quantity
```

Создать журнал движений товара.

Например:

```text
InventoryMovement
```

Минимальные поля:

```text
id
product
movement_type
quantity
reference_type
reference_id
user
comment
created_at
```

Типы:

```text
RECEIPT
SALE
SALE_RETURN
SUPPLIER_RETURN
WRITE_OFF
ADJUSTMENT_IN
ADJUSTMENT_OUT
SALE_CANCEL
```

Можно использовать более надежную модель связей вместо generic relation, если это архитектурно лучше.

---

# 16. STOCK BALANCE

Фактический остаток должен изменяться только через контролируемые складские операции.

Пример:

```text
Приход +100
Продажа -20
Возврат +3
Списание -2

Остаток = 81
```

Для производительности допустимо хранить cached current_stock.

Но источник изменений обязан быть аудируемым.

Если используется поле текущего остатка, оно должно обновляться атомарно одновременно с InventoryMovement.

---

# 17. NO DIRECT STOCK EDITING

Не позволять администратору просто открыть Product и произвольно поменять:

```text
stock = 500
```

Для ручного исправления использовать отдельную операцию:

```text
Stock Adjustment
```

Например:

```text
Текущий остаток: 100
Фактический остаток: 97

Корректировка: -3
Причина: инвентаризация
```

В audit log должно быть понятно:

- кто;
- когда;
- почему;
- какой товар;
- какое количество изменил.

---

# 18. STOCK RECEIPTS

Создать сущность:

```text
StockReceipt
```

или:

```text
PurchaseReceipt
```

Документ прихода товара.

Поля:

```text
id
number
supplier
status
date
comment
created_by
created_at
updated_at
```

Строки:

```text
StockReceiptItem
- product
- quantity
- cost_price
- total_cost
```

---

# 19. RECEIPT STATUS

Использовать статусы:

```text
DRAFT
POSTED
CANCELLED
```

## DRAFT

Не влияет на склад.

## POSTED

Увеличивает склад.

## CANCELLED

Создает корректное обратное движение.

Нельзя физически удалять проведенный приход без соответствующей административной процедуры.

---

# 20. COST PRICE WHEN RECEIVING PRODUCTS

Так как сейчас действует единая текущая себестоимость:

при проведении нового прихода можно обновлять `Product.cost_price` на себестоимость из последнего прихода.

Но эту бизнес-логику оформить отдельно и понятно, чтобы ее было легко изменить позже.

Не связывать исторические продажи с текущей Product.cost_price.

---

# 21. SALES

Создать модель:

```text
Sale
```

Поля примерно:

```text
id
number
status
operator
customer
subtotal
discount
total
total_cost
profit
payment_method
comment
created_at
updated_at
completed_at
```

Часть полей может быть добавлена позже.

---

# 22. SALE NUMBER

Каждая продажа получает человекочитаемый уникальный номер.

Например:

```text
SALE-2026-000001
SALE-2026-000002
```

Генерация должна быть безопасной при параллельных запросах.

---

# 23. SALE ITEM

Каждая строка продажи должна быть snapshot.

Пример модели:

```text
SaleItem
- id
- sale
- product
- product_name
- product_sku
- product_size
- product_unit
- quantity
- cost_price
- regular_sale_price
- actual_unit_price
- line_total
- line_cost
- line_profit
```

При необходимости добавить:

```text
product_image_snapshot
```

Но физически копировать изображение необязательно.

---

# 24. WHY SALE ITEM MUST STORE SNAPSHOT

Допустим через полгода товар изменили:

```text
Название:
WC Monaco
→
Monaco Premium WC
```

или:

```text
cost_price:
800
→
950
```

или:

```text
sale_price:
1200
→
1400
```

Старая продажа не должна автоматически пересчитываться.

Поэтому ключевые финансовые значения сохраняются непосредственно внутри SaleItem.

---

# 25. POS SALES SCENARIO

Основной пользовательский сценарий.

Оператор:

1. Открывает кассу.
2. Находит товар.
3. Добавляет его в текущую продажу.
4. Указывает количество.
5. Видит стандартную цену.
6. Может указать фактическую цену за единицу.
7. Или может указать общую сумму позиции.
8. Система автоматически пересчитывает показатели.
9. Оператор добавляет другие товары.
10. Проверяет итог.
11. Нажимает завершить продажу.
12. Backend повторно проверяет остатки и цены.
13. Создается Sale.
14. Создаются SaleItems.
15. Создаются складские движения.
16. Склад уменьшается.
17. Продажа становится COMPLETED.

Все это должно выполняться атомарно.

---

# 26. CRITICAL SALE CALCULATION

Пример:

```text
Товар: Унитаз ABC
Количество: 100
Себестоимость 1 шт: 800
Стандартная цена: 1200
```

Оператор указывает общую сумму:

```text
100000
```

Backend должен рассчитать:

```text
actual_unit_price =
100000 / 100
= 1000
```

Далее:

```text
line_total =
100 × 1000
= 100000
```

Себестоимость:

```text
line_cost =
100 × 800
= 80000
```

Прибыль:

```text
line_profit =
100000 - 80000
= 20000
```

Прибыль с единицы:

```text
unit_profit =
1000 - 800
= 200
```

Margin:

```text
profit_margin =
profit / revenue * 100

20000 / 100000 × 100
= 20%
```

---

# 27. UNIT PRICE VS TOTAL PRICE

В POS строка товара должна позволять редактировать:

```text
quantity
unit_price
total_price
```

Если пользователь меняет:

```text
unit_price
```

пересчитать:

```text
total_price = quantity × unit_price
```

Если пользователь меняет:

```text
total_price
```

пересчитать:

```text
unit_price = total_price / quantity
```

Не допускать:

```text
quantity <= 0
total_price < 0
```

Все вычисления backend должен повторить самостоятельно.

Нельзя доверять расчетам frontend.

---

# 28. DECIMAL CALCULATIONS

Категорически запрещено использовать float для:

- money;
- quantity;
- cost;
- price;
- profit;
- financial totals.

Backend:

```python
Decimal
DecimalField
```

Продумать единые правила округления.

Например денежные значения:

```text
2 decimal places
```

Но архитектура должна позволять использовать валюты без копеек / тыйынов при необходимости.

---

# 29. SERVER-SIDE CALCULATIONS

Frontend может показывать preview расчетов.

Но финальные значения:

```text
line_total
line_cost
line_profit
sale_total
sale_cost
sale_profit
```

должны рассчитываться backend.

Frontend не должен иметь возможность отправить:

```json
{
  "profit": 1000000
}
```

и заставить backend это сохранить.

Backend принимает исходные данные и самостоятельно вычисляет derived fields.

---

# 30. MULTIPLE PRODUCTS IN ONE SALE

Поддерживать сколько угодно строк.

Пример:

```text
10 × Унитаз
40 × Трап
100 м² × Кафель
```

По каждой строке считать:

```text
quantity
unit cost
total cost
actual unit price
revenue
profit
margin
```

По продаже считать:

```text
total revenue
total cost
total gross profit
```

---

# 31. SALE STATUS

Использовать статусы.

Например:

```text
DRAFT
COMPLETED
CANCELLED
PARTIALLY_RETURNED
RETURNED
```

Допускается адаптация модели.

Ключевое:

не удалять завершенные продажи физически.

---

# 32. STOCK VALIDATION

Нельзя завершить продажу, если товара недостаточно.

Пример:

```text
requested = 25
available = 20
```

API:

```text
Недостаточно товара.
Доступно: 20.
Запрошено: 25.
```

На текущем этапе отрицательные остатки запрещены.

---

# 33. CONCURRENT SALES

Критически важный кейс.

Есть:

```text
Остаток = 1
```

Оператор A открывает товар.

Оператор B тоже открывает товар.

Оба видят:

```text
1
```

Оба одновременно нажимают:

```text
Продать
```

Система должна завершить только одну продажу.

Вторая должна получить ошибку:

```text
Товар уже был продан другим оператором.
Текущий остаток: 0.
```

Реализовать через:

- database transaction;
- select_for_update;
- atomic stock validation/update;
- либо другой корректный PostgreSQL подход.

Не решать эту проблему только frontend проверкой.

---

# 34. IDEMPOTENCY / DOUBLE CLICK PROTECTION

Оператор может дважды нажать кнопку:

```text
Завершить продажу
```

Из-за медленного интернета.

Система не должна создать две одинаковые продажи.

Реализовать защиту:

- disabled state на frontend;
- backend idempotency;
- уникальный request key или аналогичный механизм.

---

# 35. BELOW COST SALES

Архитектурно предусмотреть случай:

```text
cost price = 800
sale price = 700
```

На первом этапе система должна как минимум:

- определить отрицательную прибыль;
- визуально предупредить пользователя;
- сохранить фактический результат.

Правило полного запрета продажи ниже себестоимости не хардкодить глубоко в архитектуру.

Сделать его configurable business rule, чтобы позже можно было выбрать:

```text
allow
warn
admin-only
deny
```

---

# 36. RETURNS

Предусмотреть возвраты покупателей.

Создать отдельную сущность, связанную с исходной продажей.

Например:

```text
SaleReturn
SaleReturnItem
```

Возврат должен ссылаться на исходный SaleItem.

Нельзя вернуть больше, чем было куплено с учетом предыдущих возвратов.

---

# 37. RETURN EXAMPLE

Продано:

```text
100 units
```

Уже возвращено:

```text
20
```

Максимально доступно для нового возврата:

```text
80
```

Если пользователь пытается вернуть:

```text
90
```

операция запрещается.

---

# 38. RETURN STOCK EFFECT

Возврат:

```text
+ quantity на склад
```

и создает:

```text
SALE_RETURN
```

InventoryMovement.

Финансовые отчеты должны учитывать возвраты.

---

# 39. CANCELLING SALES

Не удалять завершенную продажу.

При отмене:

```text
COMPLETED
→
CANCELLED
```

Создать компенсирующие складские движения.

Сохранить:

```text
cancelled_by
cancelled_at
cancel_reason
```

Отмена доступна только пользователю с соответствующим permission.

---

# 40. ADMIN EDITING HISTORICAL SALES

По бизнес-требованию административный пользователь может изменить историческую продажу.

Но реализация должна быть безопасной.

Не разрешать редактировать SaleItem как обычную строку напрямую без бизнес-логики.

Создать service layer, например:

```python
SaleCorrectionService
```

Он должен:

1. загрузить исходную продажу;
2. получить lock;
3. сохранить old snapshot;
4. проверить права;
5. проверить корректность новой продажи;
6. определить разницу по товарам;
7. корректно изменить склад;
8. пересчитать все totals;
9. записать audit log;
10. сохранить причину;
11. завершить все одной transaction.atomic.

---

# 41. EXAMPLE OF ADMIN CORRECTION

Исходная продажа:

```text
Product A
quantity = 10
price = 1000
```

Администратор обнаружил ошибку:

```text
quantity должно быть 8
```

Нельзя просто изменить:

```text
10 → 8
```

Нужно также вернуть:

```text
2 units
```

на склад.

И обновить:

```text
revenue
cost
profit
```

Audit log:

```text
Admin: admin@example
Date: ...
Sale: SALE-2026-000123
Reason: Ошибочно указано количество

quantity:
10 → 8

revenue:
10000 → 8000

stock correction:
+2
```

---

# 42. AUDIT LOG

Создать полноценный AuditLog.

Минимум:

```text
id
user
action
entity_type
entity_id
old_data
new_data
reason
ip_address
created_at
```

Особенно логировать:

- изменение себестоимости;
- изменение стандартной цены;
- складскую корректировку;
- отмену продажи;
- возврат;
- административное изменение продажи;
- изменение прихода;
- изменение permissions.

---

# 43. SOFT DELETE / ARCHIVE

Не удалять критичные сущности физически.

Для Product использовать:

```text
is_active
```

Если товар больше не продается:

```text
is_active = false
```

Исторические продажи продолжают отображаться.

---

# 44. CATEGORIES

Создать Category.

Поля:

```text
id
name
slug
parent
is_active
```

Поддержать вложенность, если это не создает лишнюю сложность.

Пример:

```text
Сантехника
    Унитазы
    Раковины
    Смесители

Плитка
    Кафель
    Керамогранит
```

---

# 45. SEARCH

POS должен иметь быстрый поиск товара.

Поиск минимум по:

- name;
- SKU;
- model;
- brand.

По возможности сделать tolerant partial search.

Например:

```text
monac
```

находит:

```text
Monaco Rimless WC
```

---

# 46. POS PRODUCT CARD

Карточка товара в кассе:

```text
[PHOTO]

Monaco Rimless
SKU: WC-001
Размер: ...
Остаток: 124 шт.

Цена: 1 200
```

Добавление товара должно занимать минимум действий.

---

# 47. CURRENT SALE UI

Основная область POS:

```text
------------------------------------------------
Товар       Кол-во   Цена   Сумма
------------------------------------------------
Унитаз A      10     1000   10000
Трап B        20      500   10000
------------------------------------------------
Итого:                      20000
------------------------------------------------
```

Каждую строку можно быстро редактировать.

---

# 48. POS PROFIT INFORMATION

Архитектура должна поддерживать отображение:

```text
Revenue
Cost
Profit
Margin
```

в текущей продаже.

Видимость этих данных должна зависеть от permissions.

То есть не хардкодить:

```text
operator always sees cost
```

Создать permission, например:

```text
sales.view_cost_price
sales.view_profit
```

Администратор сможет управлять этим правилом.

---

# 49. KEYBOARD UX

POS должен быть удобен для интенсивной работы.

Продумать:

- autofocus поиска;
- Enter для добавления;
- быстрый переход между количеством и ценой;
- keyboard navigation;
- минимальное использование мышки.

Но не создавать чрезмерно сложную hotkey систему.

---

# 50. RESPONSIVE POS

Минимальные платформы:

- desktop;
- laptop;
- tablet.

Телефон может поддерживаться адаптивно, но desktop/tablet имеют приоритет.

---

# 51. ADMIN PANEL WITH DJANGO UNFOLD

Django Unfold должен быть оформлен как основной backoffice.

Не оставлять стандартный сырой Django Admin.

Сделать удобные:

- list display;
- filters;
- search;
- readonly calculated fields;
- thumbnails;
- fieldsets;
- autocomplete;
- date filters;
- inline items там, где это безопасно.

---

# 52. ADMIN NAVIGATION

Пример навигации:

```text
Dashboard

Каталог
    Товары
    Категории

Склад
    Остатки
    Приходы
    Движения
    Корректировки

Продажи
    Все продажи
    Возвраты

Отчеты
    Продажи
    Товары
    Операторы

Управление
    Пользователи
    Audit Log
```

---

# 53. DASHBOARD

Главный административный dashboard.

Показывать данные за сегодня:

```text
Выручка сегодня
Себестоимость проданного
Валовая прибыль
Количество продаж
Количество проданных товарных единиц
Средний чек
```

Дополнительно:

```text
Последние продажи
Товары с низким остатком
Топ товаров сегодня
```

---

# 54. REPORTS

Основной отчет:

```text
Sales Report
```

По умолчанию:

```text
Сегодня
```

Быстрые периоды:

```text
Сегодня
Вчера
Эта неделя
Этот месяц
Прошлый месяц
Произвольный период
```

---

# 55. REPORT DATE RANGE

Позволить указать:

```text
date_from
date_to
```

Корректно учитывать timezone.

Система должна иметь централизованную timezone configuration.

---

# 56. REPORT SUMMARY

В верхней части отчета:

```text
Выручка
Себестоимость
Валовая прибыль
Количество продаж
Количество проданных единиц
Средний чек
Средняя маржа
```

---

# 57. PRODUCT SALES REPORT TABLE

Основная агрегированная таблица.

Колонки:

```text
Фото

SKU

Название товара

Размер / вариант

Единица измерения

Проданное количество

Себестоимость единицы

Общая себестоимость

Средняя фактическая цена продажи

Общая выручка

Валовая прибыль

Маржа
```

---

# 58. REPORT AVERAGE SALE PRICE

Очень важный расчет.

Пример.

Продажа 1:

```text
10 units × 1000
= 10000
```

Продажа 2:

```text
20 units × 900
= 18000
```

Всего:

```text
quantity = 30
revenue = 28000
```

Средняя фактическая цена:

```text
28000 / 30 = 933.33
```

НЕ использовать Product.sale_price для этого показателя.

---

# 59. REPORT FILTERS

Добавить фильтры:

```text
date range
product
category
operator
SKU
```

Архитектура должна позволять добавить позже:

```text
supplier
customer
payment method
brand
```

---

# 60. REPORT SORTING

Поддержать сортировку:

```text
highest revenue
highest profit
highest quantity
lowest margin
highest margin
```

---

# 61. SALES LIST

Администратор должен видеть таблицу продаж:

```text
Sale number
Date
Operator
Items count
Revenue
Cost
Profit
Status
```

По нажатию открывается подробная продажа.

---

# 62. SALE DETAILS

Экран продажи:

```text
SALE-2026-000123

Дата:
Оператор:
Статус:

--------------------------------------------
Товар | Qty | Cost | Price | Revenue | Profit
--------------------------------------------

Итого:
Revenue
Cost
Profit
```

Показывать связанные:

- returns;
- cancellations;
- corrections;
- audit events.

---

# 63. OPERATOR REPORT

Добавить отчет по операторам.

Например:

```text
Оператор
Количество продаж
Продано товаров
Выручка
Себестоимость
Прибыль
Средний чек
```

---

# 64. EXPORT

Предусмотреть экспорт отчетов:

```text
CSV
XLSX
```

Минимум CSV.

Желательно XLSX.

Экспорт должен использовать те же фильтры, которые применены к отчету.

---

# 65. LOW STOCK

Product содержит:

```text
minimum_stock
```

Если:

```text
current_stock <= minimum_stock
```

товар считается low stock.

Показывать в админ dashboard.

---

# 66. CUSTOMER SUPPORT

Не обязательно делать полноценную CRM.

Но архитектура Sale должна позволять добавить customer.

Можно создать простую модель:

```text
Customer
- id
- name
- phone
- company_name
- comment
```

Поле customer в Sale может быть nullable.

Таким образом разрешены анонимные продажи.

---

# 67. SUPPLIERS

Создать базовую модель Supplier:

```text
id
name
phone
contact_person
comment
is_active
```

StockReceipt может ссылаться на Supplier.

Поле может быть optional.

---

# 68. PAYMENT METHOD

Архитектурно предусмотреть:

```text
CASH
CARD
TRANSFER
OTHER
```

Но не строить сейчас полноценную бухгалтерскую систему.

---

# 69. NOT ACCOUNTING SOFTWARE

Важно:

система считает прежде всего:

```text
Sales revenue
Cost of goods sold
Gross profit
```

Формула:

```text
Gross Profit =
Revenue - Cost Of Goods Sold
```

Не смешивать это с чистой прибылью компании.

Не учитывать в gross profit:

- аренду;
- зарплаты;
- коммунальные расходы;
- налоги;
- доставку;

если для них отдельно не реализован expense module.

Во frontend использовать правильное наименование:

```text
Валовая прибыль
```

а не:

```text
Чистая прибыль
```

---

# 70. FINANCIAL INTEGRITY

Все агрегаты должны вычисляться из фактических SaleItem.

Например:

```text
sale.total_cost =
SUM(sale_items.line_cost)
```

```text
sale.total =
SUM(sale_items.line_total)
```

```text
sale.profit =
sale.total - sale.total_cost
```

Если totals кэшируются в Sale — они должны поддерживаться backend и быть консистентными.

---

# 71. DATABASE CONSTRAINTS

Использовать database constraints там, где это уместно.

Например:

```text
quantity > 0
price >= 0
cost_price >= 0
stock >= 0
```

Но учитывать отмененные / технические InventoryMovement, где количество может иметь другую семантику.

---

# 72. DATABASE INDEXES

Добавить индексы минимум для часто используемых запросов:

```text
Product.sku
Product.name
Sale.created_at
Sale.status
Sale.operator
SaleItem.product
InventoryMovement.product
InventoryMovement.created_at
```

Продумать composite indexes для отчетов, если необходимо.

---

# 73. N+1 QUERY PROTECTION

При разработке API и Django Admin использовать:

```python
select_related()
prefetch_related()
```

Не допускать очевидных N+1 запросов.

Особенно:

- sales list;
- reports;
- sale details;
- product list.

---

# 74. PAGINATION

Большие таблицы должны иметь pagination.

Например:

- products;
- sales;
- inventory movements;
- audit logs.

Не загружать тысячи записей сразу.

---

# 75. API DESIGN

Создать понятный API.

Пример:

```text
/api/auth/
/api/products/
/api/products/{id}/
/api/categories/
/api/sales/
/api/sales/{id}/
/api/sales/{id}/cancel/
/api/sales/{id}/return/
/api/inventory/
/api/reports/sales/
/api/reports/products/
/api/reports/operators/
```

Не обязательно строго соблюдать именно эти URL.

Главное — последовательная REST architecture.

---

# 76. SALE CREATION API

Пример запроса:

```json
{
  "items": [
    {
      "product_id": 123,
      "quantity": "100",
      "total_price": "100000"
    }
  ],
  "payment_method": "cash",
  "comment": ""
}
```

Backend получает Product и самостоятельно определяет:

```text
cost_price
regular_sale_price
```

Backend рассчитывает:

```text
actual_unit_price
line_total
line_cost
line_profit
```

---

# 77. NEVER TRUST CLIENT COST

Никогда не принимать от frontend как авторитетные:

```text
cost_price
profit
line_cost
line_profit
stock_after
```

Frontend может показывать данные только как preview.

---

# 78. API ERROR FORMAT

Использовать единый error response.

Например:

```json
{
  "code": "INSUFFICIENT_STOCK",
  "message": "Недостаточно товара на складе.",
  "details": {
    "product_id": 123,
    "available": "20",
    "requested": "25"
  }
}
```

Это упростит POS frontend.

---

# 79. TRANSACTIONS

Использовать:

```python
transaction.atomic()
```

для:

- posting receipt;
- completing sale;
- cancelling sale;
- returning sale;
- admin correction;
- stock adjustment.

Нельзя допустить частичную операцию.

Например:

Sale создана, но склад не уменьшен — недопустимо.

---

# 80. ADMIN CORRECTION TRANSACTION SAFETY

Если административная корректировка не может полностью завершиться:

```text
ROLLBACK EVERYTHING
```

Нельзя оставить:

- измененный SaleItem;
- но старый склад;
- или наоборот.

---

# 81. TESTING

Обязательно написать automated tests.

Минимально:

## Product tests

- создание;
- SKU unique;
- decimal validation.

## Inventory tests

- receipt увеличивает stock;
- sale уменьшает;
- return увеличивает;
- adjustment корректно работает.

## Sale tests

- normal sale;
- custom unit price;
- custom total line price;
- profit calculation;
- insufficient stock;
- multiple products;
- decimal quantities.

## Historical snapshot tests

Проверить:

```text
Product.cost_price = 800

Sale created

Product.cost_price = 900

Old SaleItem.cost_price == 800
```

Это обязательный тест.

---

# 82. CONCURRENCY TESTS

Проверить кейс:

```text
stock = 1

request A buy 1
request B buy 1
```

В результате:

```text
completed sales = 1
stock = 0
```

а не:

```text
completed sales = 2
stock = -1
```

---

# 83. ADMIN CORRECTION TESTS

Проверить:

```text
sale quantity = 10
stock after sale = 90
```

Администратор меняет:

```text
quantity 10 → 8
```

Получаем:

```text
stock = 92
```

и AuditLog содержит изменение.

---

# 84. RETURN TESTS

Проверить:

```text
sold = 10
return 3
return 4
```

available remaining return:

```text
3
```

Попытка вернуть 4 должна быть запрещена.

---

# 85. PERMISSION TESTS

Проверить:

Operator:

```text
cannot edit product cost
cannot change historical sale
cannot access admin reports without permission
```

Admin:

```text
can perform authorized actions
```

Проверять API permissions, а не только UI.

---

# 86. TIMEZONE

Все datetime хранить корректно с timezone awareness.

Backend должен использовать стандартную Django timezone architecture.

Reports:

```text
Сегодня
```

должны определяться по timezone бизнеса, а не случайно по UTC.

Сделать timezone настраиваемой через settings/env.

---

# 87. LOCALIZATION

Основной интерфейс — русский.

Тексты UI:

```text
Товары
Продажи
Склад
Приход
Выручка
Себестоимость
Валовая прибыль
Количество
Цена
Общая сумма
Отчеты
```

Код, class names, variable names, database field names использовать на английском.

---

# 88. UI DESIGN PRINCIPLES

Не делать:

- огромное количество карточек;
- слишком много цветов;
- сложные анимации;
- перегруженные dashboard элементы;
- маленькие кликабельные элементы;
- бессмысленные модальные окна.

Делать:

- чистый интерфейс;
- хорошую типографику;
- четкую hierarchy;
- большие удобные input;
- понятные таблицы;
- sticky totals;
- хороший loading state;
- empty states;
- confirmation для критических операций.

---

# 89. DANGEROUS ACTIONS

Для:

```text
Cancel Sale
Stock Adjustment
Historical Correction
Return
```

требовать confirmation.

Для административного изменения истории желательно:

```text
Reason
```

обязательное поле.

---

# 90. DATA AUDITABILITY

Для каждой важной бизнес-операции пользователь должен иметь возможность понять:

```text
Что произошло?
Когда?
С каким товаром?
Сколько?
Кто это сделал?
Почему?
Из какого документа?
```

Это один из главных принципов системы.

---

# 91. SERVICE LAYER

Не размещать всю сложную бизнес-логику в:

```text
views.py
serializers.py
admin.py
```

Создать service layer.

Например:

```text
sales/services.py

complete_sale()
cancel_sale()
correct_sale()
create_sale_return()
```

```text
inventory/services.py

post_receipt()
adjust_stock()
create_inventory_movement()
```

Serializer отвечает за validation/input-output.

Business rules находятся в services/domain layer.

---

# 92. MODEL METHODS

Не превращать Django models в огромные классы с сотнями строк бизнес-логики.

Модели должны отвечать за:

- данные;
- базовые invariants;
- простые model-level методы.

Сложные multi-model операции выполнять через service layer.

---

# 93. ADMIN ACTION SAFETY

Не использовать unsafe bulk actions типа:

```text
Delete selected sales
```

для критичных сущностей.

Отключить или ограничить Django delete для:

- completed sales;
- posted receipts;
- inventory movements;
- audit logs.

---

# 94. AUDIT LOG IMMUTABILITY

AuditLog не должен редактироваться обычными администраторами.

Желательно сделать его readonly.

Superuser может иметь технический доступ, но даже там не создавать удобного UI для изменения аудита без необходимости.

---

# 95. INVENTORY MOVEMENT IMMUTABILITY

Проведенные InventoryMovement должны рассматриваться как immutable ledger.

Не редактировать старое движение.

Для исправления создавать новое компенсирующее movement.

---

# 96. REPORT RETURNS

При наличии возвратов отчеты должны показывать NET значения.

Например:

Продано:

```text
Revenue = 100000
Cost = 80000
```

Возвращено:

```text
Revenue = 10000
Cost = 8000
```

Итог:

```text
Net Revenue = 90000
Net Cost = 72000
Net Profit = 18000
```

---

# 97. STANDARD PRICE ANALYTICS

Сохранить:

```text
regular_sale_price
```

в SaleItem.

Это позволит позже рассчитывать:

```text
Standard revenue
Actual revenue
Discount amount
```

Пример:

```text
regular = 1200
actual = 1000
quantity = 100
```

Difference:

```text
20000
```

Это не обязательно показывать в MVP, но snapshot сохранить полезно.

---

# 98. PRICE OVERRIDE

Если actual price отличается от regular price, это должно быть видно в деталях продажи.

Например:

```text
Стандартная цена: 1200
Продано по: 1000
Отклонение: -200
```

Позже можно использовать это для отчетов.

---

# 99. PRODUCT CURRENT STOCK VIEW

В карточке Product администратора показывать:

```text
Текущий остаток
Себестоимость
Стандартная цена
Ожидаемая прибыль с единицы
Последний приход
Последняя продажа
```

Expected profit:

```text
sale_price - cost_price
```

Но четко отличать:

```text
Expected profit
```

от фактической прибыли уже совершенных продаж.

---

# 100. PRODUCT INVENTORY HISTORY

Из Product должна быть возможность быстро открыть:

```text
История движения
```

Таблица:

```text
Дата
Тип
Документ
Приход
Расход
Пользователь
Комментарий
```

---

# 101. PRODUCT SALES HISTORY

В карточке товара желательно показывать:

```text
Последние продажи
```

Например:

```text
Дата
Sale #
Quantity
Actual unit price
Revenue
Profit
Operator
```

---

# 102. RECEIPT UI

Django Unfold форма прихода должна быть удобной.

Один документ:

```text
Supplier
Date
Comment
Items
```

Items:

```text
Product
Quantity
Cost Price
Line Total
```

Поддержать добавление нескольких товаров.

---

# 103. RECEIPT CALCULATIONS

Для каждого ReceiptItem:

```text
line_total =
quantity × cost_price
```

И:

```text
receipt.total =
SUM(line_total)
```

---

# 104. POSTING RECEIPT

Нельзя автоматически проводить приход просто после `save()` формы.

Должно быть понятное действие:

```text
Провести приход
```

После проведения:

- создаются stock movements;
- обновляется stock;
- обновляется current cost согласно текущему правилу;
- документ становится POSTED.

---

# 105. CANCEL RECEIPT

Отмена проведенного прихода должна проверять возможность корректного возврата количества.

Например после прихода:

```text
+10
```

пять уже продано.

Прямая отмена всего прихода может сделать stock отрицательным.

Поэтому backend должен:

- проверить бизнес-инварианты;
- либо запретить отмену;
- либо потребовать специальную административную корректировку.

Не делать слепой reverse.

---

# 106. INITIAL STOCK

Предусмотреть начальное внесение остатков при запуске системы.

Не советовать пользователю напрямую редактировать stock.

Создать:

```text
INITIAL_BALANCE
```

или отдельную stock adjustment операцию.

---

# 107. IMPORT PRODUCTS

Архитектурно предусмотреть возможность массового импорта товаров через CSV/XLSX.

MVP может включать CSV import в admin.

Минимальные поля:

```text
SKU
Name
Category
Size
Unit
Cost Price
Sale Price
Initial Stock
```

Импорт должен:

- валидировать данные;
- выдавать понятные ошибки;
- не создавать полусохраненный импорт при критических ошибках.

---

# 108. DATABASE SEED

Создать development seed data.

Например категории:

```text
Унитазы
Смесители
Кафель
Душевые трапы
```

и несколько тестовых Product.

Также:

```text
admin
operator
```

для local development.

Не использовать production passwords в репозитории.

---

# 109. ENVIRONMENT VARIABLES

Пример:

```text
DATABASE_URL
DJANGO_SECRET_KEY
DEBUG
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
TIME_ZONE
MEDIA settings
JWT settings
```

Создать:

```text
.env.example
```

---

# 110. SECURITY

Следовать базовым production security practices:

- secure password hashing;
- CSRF protection, если используется cookie auth;
- CORS only allowed frontend origins;
- no secrets in repository;
- input validation;
- object-level permission checks;
- protected admin;
- secure production settings.

---

# 111. API DOCUMENTATION

Настроить OpenAPI schema.

Например:

```text
drf-spectacular
```

Сгенерировать Swagger / OpenAPI docs.

Документировать основные endpoints.

---

# 112. FRONTEND TYPES

Не дублировать хаотично API types.

Организовать TypeScript types.

Если удобно, генерировать клиент/types из OpenAPI.

---

# 113. FRONTEND API CLIENT

Создать централизованный API client.

Обрабатывать:

- auth;
- API errors;
- unauthorized;
- validation errors;
- loading;
- request cancellation при необходимости.

Не размещать random fetch вызовы по всему UI.

---

# 114. POS STATE

Текущая корзина может храниться в frontend state.

Но после завершения продажи единственным источником истины становится backend.

При reload можно либо очищать незавершенную корзину, либо сохранять локальный draft.

Выбрать простой надежный подход.

---

# 115. SALES PERFORMANCE

POS должен ощущаться быстрым.

Поиск товара не должен каждый раз загружать весь каталог.

Использовать:

- server-side search;
- debounce;
- pagination / limited results;
- кэширование только там, где оно не ломает остатки.

---

# 116. STOCK FRESHNESS

Frontend может показать stock:

```text
10
```

Но перед commit продажи backend обязан получить актуальный stock под lock.

Нельзя считать показанный frontend остаток гарантией.

---

# 117. MONEY DISPLAY

Создать единую функцию форматирования денег.

Например:

```text
100000
→
100 000
```

Если используется KGS:

```text
100 000 сом
```

Но валюту сделать централизованно настраиваемой.

---

# 118. PRODUCT QUANTITY DISPLAY

Пример:

```text
10 шт.
12.5 м²
3 коробки
```

Не вшивать unit вручную по всему frontend.

---

# 119. EMPTY STATES

Продумать:

```text
Товаров пока нет
Продаж за этот период нет
Нет товаров с низким остатком
По запросу ничего не найдено
```

---

# 120. LOADING AND ERROR UX

При создании продажи:

- блокировать повторное нажатие;
- показывать progress;
- при success показывать номер продажи;
- при error не очищать корзину автоматически.

Если stock изменился:

```text
Остаток товара изменился.
Доступно 4 вместо 10.
```

Пользователь должен иметь возможность исправить корзину.

---

# 121. CONFIRM SALE

Перед завершением продажи необязательно показывать модалку каждый раз, если это тормозит работу.

Можно сделать большую понятную кнопку:

```text
Завершить продажу
```

Но если есть критические предупреждения:

- ниже себестоимости;
- сильно измененная цена;
- необычно большое количество;

можно показывать confirmation.

---

# 122. SALES RECEIPT / DOCUMENT

Архитектура должна позволять позже печатать обычную накладную.

Сразу структурировать Sale API так, чтобы можно было сформировать:

```text
Sale #
Date
Seller
Products
Quantity
Price
Total
Grand Total
```

Фискальную кассу сейчас не реализовывать, если специально не запрошено.

---

# 123. REPORT PERFORMANCE

Не рассчитывать огромные отчеты через Python loop с тысячами запросов.

Использовать:

- PostgreSQL aggregation;
- annotate;
- Sum;
- Count;
- F expressions;
- efficient queries.

При сложной логике допустим специализированный reporting service.

---

# 124. DATABASE SOURCE OF TRUTH

Правило:

```text
Product.current_stock
```

если кэшируется, отвечает за быстрый текущий остаток.

```text
InventoryMovement
```

дает историю того, почему остаток такой.

```text
SaleItem
```

дает финансовую историю продажи.

Не смешивать эти ответственности.

---

# 125. ERROR CASES TO HANDLE

Обязательно обработать:

### Sale

- product doesn't exist;
- product inactive;
- quantity = 0;
- quantity < 0;
- price < 0;
- insufficient stock;
- duplicate submit;
- concurrent sale;
- invalid decimal;
- user without permission.

### Receipt

- inactive product;
- quantity <= 0;
- invalid cost;
- already posted;
- double posting.

### Return

- return > sold;
- return > remaining;
- cancelled sale;
- repeated request.

### Admin correction

- insufficient stock after correction;
- permission denied;
- invalid reason;
- stale version / concurrent edit.

---

# 126. OPTIMISTIC LOCKING FOR ADMIN EDITS

Для критических административных изменений предусмотреть защиту от stale data.

Например использовать:

```text
updated_at
version
```

Если Admin A и Admin B одновременно открыли одну продажу и оба изменили ее, второй не должен молча затереть изменения первого.

Можно использовать optimistic locking или explicit row lock в correction flow.

---

# 127. ADMIN HISTORICAL EDIT PHILOSOPHY

Требование бизнеса:

> Историю можно изменить с административным доступом.

Но UX должен давать понять, что это исправление истории, а не обычное редактирование.

Использовать действие вроде:

```text
Исправить продажу
```

а не обычную кнопку:

```text
Edit
```

Показывать предупреждение:

```text
Изменение повлияет на склад, выручку и прибыль.
Операция будет записана в журнал аудита.
```

---

# 128. ADMIN AUDIT VIEW

В Django Unfold создать удобную readonly страницу Audit Log.

Фильтры:

```text
User
Action
Entity type
Date
```

Search:

```text
Sale #
SKU
Entity ID
```

---

# 129. REPORT DEFINITIONS

Четко зафиксировать термины.

## Revenue

Фактическая сумма продажи с учетом возвратов.

## Cost

Snapshot себестоимости фактически проданного количества.

## Gross Profit

```text
Revenue - Cost
```

## Average Sale Price

```text
Revenue / Quantity
```

## Gross Margin %

```text
Gross Profit / Revenue × 100
```

При Revenue = 0 корректно обрабатывать division by zero.

---

# 130. DEVELOPMENT ORDER

Не пытаться реализовать все хаотично.

Следовать этапам.

---

## PHASE 1 — FOUNDATION

Реализовать:

- Django project;
- PostgreSQL;
- settings;
- Docker/local environment;
- users;
- roles;
- permissions;
- base models;
- migrations.

---

## PHASE 2 — PRODUCT CATALOG

Реализовать:

- Category;
- Product;
- SKU;
- images;
- units;
- Django Unfold product management.

---

## PHASE 3 — INVENTORY

Реализовать:

- current stock;
- InventoryMovement;
- stock services;
- stock adjustment;
- inventory history.

Покрыть тестами.

---

## PHASE 4 — RECEIPTS

Реализовать:

- StockReceipt;
- StockReceiptItem;
- DRAFT;
- POSTED;
- CANCEL;
- cost_price update;
- inventory integration.

---

## PHASE 5 — SALES DOMAIN

Реализовать:

- Sale;
- SaleItem;
- sale snapshots;
- server-side calculations;
- stock locking;
- concurrency protection;
- idempotency;
- tests.

Это самый критичный этап.

---

## PHASE 6 — REST API

Реализовать:

- auth;
- products;
- search;
- sales;
- stock;
- reports;
- permissions.

Документировать OpenAPI.

---

## PHASE 7 — NEXT.JS POS

Реализовать:

- login;
- POS page;
- product search;
- cart;
- quantity;
- unit price;
- total line amount;
- real-time calculations;
- checkout;
- errors;
- responsive UX.

---

## PHASE 8 — RETURNS AND CANCELLATIONS

Реализовать:

- sale return;
- partial return;
- cancellation;
- inventory reverse movements;
- financial effects.

---

## PHASE 9 — ADMIN REPORTING

Реализовать:

- today dashboard;
- period report;
- product report;
- operator report;
- filters;
- sorting;
- export.

---

## PHASE 10 — AUDIT AND ADMIN CORRECTIONS

Реализовать:

- AuditLog;
- historical correction service;
- mandatory reason;
- stock recalculation;
- financial recalculation;
- permissions;
- tests.

---

# 131. CODE QUALITY REQUIREMENTS

Код должен быть:

- читаемый;
- типизированный там, где разумно;
- модульный;
- без чрезмерной абстракции;
- без copy-paste business logic;
- покрытый тестами для критических операций.

Следовать:

- Django best practices;
- DRF best practices;
- React/Next.js best practices;
- TypeScript strictness.

---

# 132. DO NOT OVERENGINEER

Не внедрять без необходимости:

- microservices;
- Kafka;
- Kubernetes;
- CQRS framework;
- event sourcing framework;
- Elasticsearch;
- Redis;
- Celery.

Если конкретная функция в будущем действительно потребует Redis/Celery, архитектура должна позволять добавить их позже.

На текущем этапе:

```text
Django + PostgreSQL + Next.js
```

достаточно.

---

# 133. IMPORTANT BUSINESS RULES SUMMARY

Эти правила считаются обязательными.

### Rule 1

У каждого товара сейчас одна актуальная себестоимость.

### Rule 2

При продаже себестоимость копируется в SaleItem.

### Rule 3

Изменение текущей себестоимости Product не изменяет старые продажи.

### Rule 4

Фактическая цена продажи может отличаться от стандартной.

### Rule 5

Пользователь может вводить цену за единицу или общую сумму строки.

### Rule 6

Backend самостоятельно рассчитывает финансовые значения.

### Rule 7

Продажа уменьшает склад.

### Rule 8

Нельзя продавать больше остатка.

### Rule 9

Все складские изменения проходят через ledger / InventoryMovement.

### Rule 10

Completed sales физически не удаляются.

### Rule 11

Администратор может исправить историческую продажу только через контролируемый correction workflow.

### Rule 12

Administrative correction записывается в AuditLog.

### Rule 13

Изменение исторической продажи должно корректно менять склад.

### Rule 14

Изменение исторической продажи должно пересчитывать Revenue / Cost / Profit.

### Rule 15

Продажа должна быть transaction-safe.

### Rule 16

Concurrent sale не может создать отрицательный stock.

### Rule 17

Double submit не должен создать duplicate sale.

### Rule 18

Все money calculations используют Decimal.

### Rule 19

Отчеты используют фактическую продажную цену.

### Rule 20

Profit означает:

```text
Gross Profit = Revenue - Cost
```

---

# 134. EXAMPLE BUSINESS FLOW

Имеем товар:

```text
Product:
Name: Унитаз Monaco
SKU: WC-MONACO
Stock: 150
Cost price: 800
Regular sale price: 1200
```

Оператор продает:

```text
Quantity: 100
Total line price: 100000
```

Расчет:

```text
Actual unit price:
100000 / 100 = 1000

Revenue:
100000

Cost:
100 × 800 = 80000

Gross profit:
100000 - 80000 = 20000

Gross margin:
20%
```

После продажи:

```text
Stock:
150 - 100 = 50
```

Создать:

```text
Sale
SaleItem
InventoryMovement(SALE, -100)
```

SaleItem snapshot:

```text
product_name = "Унитаз Monaco"
product_sku = "WC-MONACO"
quantity = 100
cost_price = 800
regular_sale_price = 1200
actual_unit_price = 1000
line_total = 100000
line_cost = 80000
line_profit = 20000
```

---

# 135. COST CHANGE EXAMPLE

После продажи администратор меняет:

```text
Product.cost_price:
800 → 900
```

Новый Product:

```text
cost_price = 900
```

Старая SaleItem остается:

```text
cost_price = 800
```

Новая продажа будет использовать:

```text
cost_price = 900
```

---

# 136. ADMIN CORRECTION EXAMPLE

Старая продажа:

```text
100 units × 1000
```

Администратор обнаруживает, что фактически продали:

```text
90 units
```

Использует:

```text
Исправить продажу
```

Указывает:

```text
Quantity:
100 → 90

Reason:
Ошибка оператора при вводе количества.
```

Система должна:

```text
1. вернуть 10 единиц на склад;
2. пересчитать line_total;
3. пересчитать line_cost;
4. пересчитать line_profit;
5. пересчитать Sale totals;
6. записать audit event;
7. сохранить old/new values;
8. завершить все атомарно.
```

---

# 137. FINAL IMPLEMENTATION EXPECTATION

Не ограничиваться созданием моделей.

Нужен целостный working product:

```text
Backend
+
Database
+
REST API
+
Django Unfold Admin
+
Next.js POS
+
Permissions
+
Inventory
+
Sales
+
Reports
+
Tests
```

После каждого этапа приложение должно оставаться запускаемым.

---

# 138. BEFORE WRITING CODE

Перед непосредственной реализацией:

1. Проанализируй всю спецификацию.
2. Составь предлагаемую структуру папок.
3. Опиши Django models.
4. Опиши главные database relationships.
5. Отдельно перечисли business invariants.
6. Опиши критические transactions.
7. Опиши API endpoints.
8. Опиши POS screens.
9. Укажи потенциальные архитектурные риски.
10. Только после этого переходи к реализации.

Не задавай вопросы по мелким техническим решениям, если можешь выбрать профессиональное разумное решение самостоятельно.

Если какая-либо бизнес-деталь пока не определена:

- не блокируй разработку;
- выбери консервативный default;
- изолируй это правило;
- оставь возможность легко поменять его позже;
- явно документируй принятое предположение.

---

# 139. PRIORITY ORDER

При конфликте требований приоритет:

```text
1. Data integrity
2. Financial correctness
3. Inventory correctness
4. Security / permissions
5. Auditability
6. Operator speed
7. Admin convenience
8. UI aesthetics
```

Никогда не жертвовать корректностью склада или денег ради красивого интерфейса.

---

# 140. DEFINITION OF DONE

Проект считается готовым для текущего этапа, когда можно выполнить следующий сценарий end-to-end.

Администратор:

```text
1. Создает Category.
2. Создает Product.
3. Задает cost price.
4. Задает standard sale price.
5. Делает приход.
6. Видит увеличенный остаток.
```

Оператор:

```text
7. Входит в Next.js POS.
8. Находит Product.
9. Добавляет его в Sale.
10. Указывает quantity.
11. Указывает total price.
12. Видит рассчитанную unit price.
13. Завершает Sale.
```

Система:

```text
14. Проверяет остаток.
15. Создает Sale.
16. Создает SaleItem snapshot.
17. Уменьшает stock.
18. Сохраняет фактическую цену.
19. Сохраняет себестоимость.
20. Рассчитывает gross profit.
```

Администратор:

```text
21. Открывает Dashboard.
22. Видит сегодняшнюю выручку.
23. Видит сегодняшнюю себестоимость.
24. Видит сегодняшнюю валовую прибыль.
25. Открывает отчет.
26. Выбирает период.
27. Видит агрегированный отчет по товарам.
28. Может открыть конкретную Sale.
29. Видит историю складских движений.
30. Видит Audit Log.
```

После изменения Product.cost_price:

```text
31. Старая Sale остается с прежней себестоимостью.
32. Новая Sale использует новую себестоимость.
```

При административном исправлении Sale:

```text
33. Stock корректируется.
34. Финансовые показатели пересчитываются.
35. Изменение появляется в Audit Log.
```

Все критические сценарии должны быть покрыты automated tests.

---

# 141. FINAL INSTRUCTION TO CODEX

Работай как senior engineer, а не как генератор boilerplate.

Перед каждым архитектурным решением учитывай:

```text
Что произойдет при повторном запросе?
Что произойдет при двух одновременных операторах?
Что произойдет после изменения Product?
Что произойдет при возврате?
Что произойдет при административном исправлении старой записи?
Можно ли восстановить историю действий?
Может ли операция оставить склад и финансовые данные в inconsistent состоянии?
```

Если ответ потенциально опасен — исправь архитектуру до реализации.

Предпочитай простую, хорошо проверяемую бизнес-логику вместо сложной абстракции.

Главный результат проекта:

> надежная, быстрая и понятная система оптового складского учета и продаж, где оператору легко продавать товар, а администратор всегда может понять, что было продано, сколько осталось на складе, какая была себестоимость, по какой фактической цене товар ушел и сколько валовой прибыли принесла каждая продажа.