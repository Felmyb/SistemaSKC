# SmartKitchen Connect - Architecture Specification

## System Overview

SmartKitchen Connect is a Django REST API for restaurant management, providing comprehensive functionality for order management, inventory control, menu management, and user administration.

## Architecture Principles

### Layered Architecture
```
┌─────────────────────────────────────────┐
│         API Layer (REST)                │
│    (ViewSets + Serializers + URLs)     │
├─────────────────────────────────────────┤
│      Business Logic Layer               │
│    (Models + Custom Methods)            │
├─────────────────────────────────────────┤
│      Data Access Layer                  │
│    (Django ORM + Database)              │
└─────────────────────────────────────────┘
```

### App Structure (Bounded Contexts)

1. **usuarios** - User management and authentication (RF-05)
2. **pedidos** - Order management and tracking (RF-01, RF-04)
3. **platos** - Menu and dish management (RF-01)
4. **inventario** - Inventory control (RF-02)

Each app is self-contained with:
- `models.py` - Data models
- `serializers.py` - API serializers (read/write separation)
- `views.py` - ViewSets with business logic
- `permissions.py` - Custom permission classes
- `urls.py` - URL routing
- `tests.py`, `test_*.py` - Test suites

## API Architecture

### Base URL Structure
```
/api/
├── auth/
│   ├── token/              # JWT token obtain
│   ├── token/refresh/      # JWT token refresh
│   ├── token/verify/       # JWT token verify
│   └── users/              # User management
├── orders/                 # Order management
├── menu/dishes/            # Menu management
└── inventory/              # Inventory management
    ├── ingredients/
    ├── stocks/
    └── transactions/
```

### Authentication Flow
```
1. User login → POST /api/auth/token/
2. Receive access + refresh tokens
3. Use access token in Authorization: Bearer <token>
4. When expired → POST /api/auth/token/refresh/
5. Continue with new access token
```

### Authorization Model
```
User Roles:
- CUSTOMER: Can create orders, view own orders
- STAFF: Can view/modify all orders, manage inventory
- ADMIN: Full system access
- COOK: View orders, update order status
- WAITER: Manage orders, view menu
- INVENTORY_MANAGER: Manage inventory, view reports
```

## Domain Models

### usuarios.User
**Purpose**: Extended Django User with role-based access  
**Key Fields**:
- `role`: User role (CUSTOMER, STAFF, ADMIN, etc.)
- `phone_number`: Contact for notifications
- `created_at`, `updated_at`: Audit timestamps

**Relationships**: One-to-many with Order

### pedidos.Order
**Purpose**: Customer orders with items and tracking  
**Key Fields**:
- `customer`: FK to User
- `status`: Order lifecycle (PENDING → CONFIRMED → IN_PROGRESS → READY → DELIVERED)
- `priority`: Kitchen priority (LOW, MEDIUM, HIGH, URGENT)
- `order_type`: DINE_IN, TAKEOUT, DELIVERY
- `total_amount`: Calculated total
- `estimated_time`, `actual_time`: Time tracking

**Relationships**:
- Many-to-one with User (customer)
- One-to-many with OrderItem

**Business Rules**:
- Can only be cancelled if status is PENDING or CONFIRMED
- Total amount auto-calculated from items
- Estimated time based on dish preparation times

### pedidos.OrderItem
**Purpose**: Individual dishes within an order  
**Key Fields**:
- `order`: FK to Order
- `dish`: FK to Dish
- `quantity`: Number of servings
- `unit_price`: Price snapshot at order time
- `subtotal`: Auto-calculated (quantity × unit_price)
- `special_instructions`: Custom requests

### platos.Dish
**Purpose**: Menu items with recipes and metadata  
**Key Fields**:
- `name`, `description`: Display information
- `category`: APPETIZER, MAIN_COURSE, DESSERT, etc.
- `price`: Selling price
- `preparation_time`: Minutes to prepare
- `is_available`: Current availability
- `is_vegetarian`, `is_vegan`: Dietary flags
- `allergens`: Allergen information
- `popularity_score`: For recommendations (RF-03, RF-06)

**Relationships**:
- One-to-many with RecipeItem (ingredients)
- One-to-many with OrderItem

**Business Rules**:
- Can check if in stock based on ingredient availability
- Estimated cost calculated from recipe ingredients

### platos.RecipeItem
**Purpose**: Ingredients needed for a dish  
**Key Fields**:
- `dish`: FK to Dish
- `ingredient`: FK to Ingredient
- `quantity`: Amount needed per serving
- `notes`: Preparation instructions

### inventario.Ingredient
**Purpose**: Raw materials and supplies  
**Key Fields**:
- `name`: Ingredient name
- `category`: VEGETABLES, MEAT, DAIRY, etc.
- `unit`: Measurement unit (KG, L, PC, etc.)
- `cost_per_unit`: For cost analysis
- `supplier`: Primary supplier
- `minimum_stock`: Alert threshold
- `is_active`: Currently in use

**Relationships**:
- One-to-one with InventoryStock
- One-to-many with InventoryTransaction
- One-to-many with RecipeItem

### inventario.InventoryStock
**Purpose**: Current stock levels  
**Key Fields**:
- `ingredient`: One-to-one FK
- `quantity`: Current amount
- `last_restocked`: Last restock date
- `expiration_date`: For perishables

**Business Rules**:
- Alert when quantity < minimum_stock
- Track changes via InventoryTransaction

### inventario.InventoryTransaction
**Purpose**: Audit trail for inventory changes  
**Key Fields**:
- `ingredient`: FK to Ingredient
- `transaction_type`: RESTOCK, USAGE, ADJUSTMENT, WASTE, RETURN
- `quantity`: Change amount (+ or -)
- `balance_after`: Stock level after transaction
- `user`: Who performed the transaction
- `related_order`: If transaction due to order
- `notes`: Transaction details

**Business Rules**:
- Immutable once created (audit trail)
- Automatically created on stock adjustments
- Balance calculated at transaction time

## API Patterns

### List/Retrieve/Create/Update/Delete
Standard REST operations implemented via ModelViewSet

### Custom Actions
- `POST /orders/{id}/cancel/` - Cancel order
- `PATCH /orders/{id}/update_status/` - Update order status
- `GET /orders/active/` - Get active orders
- `GET /orders/history/` - Get completed orders
- `GET /orders/stats/` - Order statistics (staff only)
- `GET /menu/dishes/popular/` - Popular dishes
- `GET /menu/dishes/categories/` - Category summary
- `POST /menu/dishes/{id}/mark_available/` - Toggle availability
- `POST /inventory/stocks/{id}/adjust/` - Adjust stock level
- `GET /inventory/ingredients/low_stock/` - Low stock alerts

### Filtering & Search
- QueryString parameters for filtering
- Search across multiple fields
- Ordering support (e.g., `?ordering=-created_at`)
- Pagination (default 20 items per page)

### Permissions
- `IsAuthenticated`: Base requirement for most endpoints
- `IsStaffOnly`: Staff and admin only
- `IsOwnerOrStaff`: Owner or staff can access
- `IsStaffOrReadOnlyOwn`: Staff full access, customers read own

## Data Flow Examples

### Create Order Flow
```
1. POST /api/orders/
   {
     "order_type": "DINE_IN",
     "table_number": "12",
     "items": [
       {"dish": 1, "quantity": 2, "special_instructions": "No salt"},
       {"dish": 3, "quantity": 1}
     ]
   }

2. Backend validates:
   - User authenticated
   - Dishes exist and available
   - Sufficient inventory

3. Create Order and OrderItems
4. Calculate total_amount and estimated_time
5. Return 201 Created with full order details
```

### Inventory Adjustment Flow
```
1. POST /api/inventory/stocks/{id}/adjust/
   {
     "quantity": -5.0,
     "transaction_type": "USAGE",
     "notes": "Used for Order #123"
   }

2. Backend:
   - Validates user has permission (staff only)
   - Creates InventoryTransaction record
   - Updates InventoryStock.quantity
   - Records balance_after for audit

3. Return updated stock details
```

## Integration Points

### Current Integrations
- JWT authentication (djangorestframework-simplejwt)
- Swagger/OpenAPI documentation (drf-yasg)
- File uploads (Django media files)

### Future Integrations (Deferred)
- Order → Inventory automatic deduction
- Real-time notifications (WebSockets)
- Payment processing
- Delivery tracking
- Analytics dashboard

## Performance Considerations

### Database Optimization
- `select_related()` for foreign keys (e.g., Order → Customer)
- `prefetch_related()` for reverse FK (e.g., Order → OrderItems)
- Database indexes on frequently queried fields
- Pagination to limit query size

### Caching Strategy (Future)
- Cache static data (categories, menu items)
- Cache expensive calculations (statistics)
- Invalidate on updates

## Security Architecture

### Authentication
- JWT tokens (access: 1 hour, refresh: 7 days)
- Secure password hashing (PBKDF2)
- Token stored client-side, validated server-side

### Authorization
- Role-based access control at ViewSet level
- Custom permission classes for fine-grained control
- Object-level permissions (e.g., user can only see own orders)

### Input Validation
- Serializer-level validation
- Model-level constraints
- Business logic validation in views

### Audit Trail
- Timestamps on all models (created_at, updated_at)
- User tracking on transactions
- Immutable transaction logs

## Testing Strategy

### Unit Tests
- Model methods and properties
- Serializer validation logic
- Permission classes
- Business logic functions

### API Tests
- Endpoint accessibility
- Request/response formats
- Status codes
- Authentication/authorization
- Error handling

### Coverage
- Current: 100% (enforced in CI/CD)
- Target: Maintain 100% for all business logic

## Deployment Architecture

### Current (Development)
```
SQLite Database → Django App → REST API
```

### Target (Production)
```
PostgreSQL → Django (multiple instances) → Load Balancer → HTTPS
           ↓
       Redis Cache
           ↓
    Celery Workers (future)
```

## Monitoring & Observability (Future)

- Application logs
- Error tracking (Sentry)
- Performance monitoring (APM)
- API usage analytics
- Database query performance

---

**Last Updated**: October 25, 2025  
**Version**: 1.0  
**Status**: In Development
