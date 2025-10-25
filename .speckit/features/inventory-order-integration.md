# Feature Specification: Inventory-Order Integration

## Overview
Automatically deduct inventory when orders are confirmed, track ingredient usage, and prevent orders when ingredients are out of stock.

## Requirements Traceability
- **RF-02**: Inventory management with automatic tracking
- **RF-01**: Order processing with stock validation
- **RNF-04**: Audit trail for inventory changes linked to orders

## User Stories

### US-1: Prevent Orders with Insufficient Stock
**As a** customer  
**I want** to see if a dish is available based on current inventory  
**So that** I don't order something that can't be prepared

**Acceptance Criteria**:
- Dish.is_in_stock property checks all recipe ingredients
- API returns clear message if ingredient is missing
- Menu displays real-time availability status

### US-2: Automatic Inventory Deduction
**As a** staff member  
**I want** inventory to automatically decrease when orders are confirmed  
**So that** stock levels stay accurate without manual entry

**Acceptance Criteria**:
- When order status changes to CONFIRMED, system deducts ingredients
- Each deduction creates an InventoryTransaction record
- Transaction links back to the order for traceability

### US-3: Stock Alerts for Kitchen
**As a** cook  
**I want** to receive alerts when ingredients are low during order preparation  
**So that** I can request restocking before running out

**Acceptance Criteria**:
- System checks stock levels when order status changes to IN_PROGRESS
- Alert appears if any ingredient < minimum_stock + buffer
- Kitchen dashboard shows low-stock warnings

## Technical Specification

### Database Changes
**No schema changes required** - existing models already support this feature:
- `InventoryTransaction.related_order` already exists for linking
- `RecipeItem` defines ingredient quantities per dish
- `InventoryStock` tracks current quantities

### API Changes

#### 1. Enhanced Order Creation Endpoint
**Endpoint**: `POST /api/orders/`

**New Behavior**:
```python
# Before creating order:
1. For each OrderItem:
   - Get dish.recipe_items
   - Calculate total ingredient needs (quantity × recipe_quantity)
   - Check if InventoryStock.quantity >= needed
   
2. If ANY ingredient insufficient:
   - Return 400 Bad Request
   - Response: {
       "error": "Insufficient stock",
       "missing_ingredients": [
         {"name": "Tomatoes", "needed": 2.5, "available": 1.0, "unit": "KG"}
       ]
     }

3. If all ingredients sufficient:
   - Create order normally
   - (Inventory deduction happens on status change)
```

#### 2. New Order Confirmation Signal
**Implementation**: Django signal on Order status change

```python
# When order.status changes from PENDING → CONFIRMED:
@receiver(post_save, sender=Order)
def deduct_inventory_on_confirmation(sender, instance, **kwargs):
    if instance.status == OrderStatus.CONFIRMED:
        # For each OrderItem:
        for item in instance.items.all():
            dish = item.dish
            quantity = item.quantity
            
            # Deduct each ingredient:
            for recipe_item in dish.recipe_items.all():
                needed = recipe_item.quantity * quantity
                stock = InventoryStock.objects.get(ingredient=recipe_item.ingredient)
                
                # Create transaction:
                InventoryTransaction.objects.create(
                    ingredient=recipe_item.ingredient,
                    transaction_type='USAGE',
                    quantity=-needed,  # Negative for deduction
                    balance_after=stock.quantity - needed,
                    user=instance.customer,
                    related_order=instance,
                    notes=f'Auto-deducted for Order #{instance.id}'
                )
                
                # Update stock:
                stock.quantity -= needed
                stock.save()
```

#### 3. Enhanced Dish Endpoint Response
**Endpoint**: `GET /api/menu/dishes/`

**Add to response**:
```json
{
  "id": 1,
  "name": "Caesar Salad",
  "is_available": true,
  "is_in_stock": true,  // ✨ NEW
  "missing_ingredients": [],  // ✨ NEW (only if is_in_stock=false)
  "max_servings_available": 12  // ✨ NEW
}
```

**Implementation**:
```python
# DishSerializer
class DishSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.SerializerMethodField()
    missing_ingredients = serializers.SerializerMethodField()
    max_servings_available = serializers.SerializerMethodField()
    
    def get_is_in_stock(self, obj):
        # Check if all ingredients available
        for recipe_item in obj.recipe_items.all():
            stock = recipe_item.ingredient.inventory_stock
            if stock.quantity < recipe_item.quantity:
                return False
        return True
    
    def get_missing_ingredients(self, obj):
        missing = []
        for recipe_item in obj.recipe_items.all():
            stock = recipe_item.ingredient.inventory_stock
            if stock.quantity < recipe_item.quantity:
                missing.append({
                    'name': recipe_item.ingredient.name,
                    'needed': recipe_item.quantity,
                    'available': stock.quantity,
                    'unit': recipe_item.ingredient.unit
                })
        return missing
    
    def get_max_servings_available(self, obj):
        # Calculate max servings based on available ingredients
        max_servings = float('inf')
        for recipe_item in obj.recipe_items.all():
            stock = recipe_item.ingredient.inventory_stock
            servings = stock.quantity / recipe_item.quantity
            max_servings = min(max_servings, int(servings))
        return max_servings if max_servings != float('inf') else 0
```

#### 4. New Low Stock Alert Endpoint
**Endpoint**: `GET /api/inventory/alerts/`

**Response**:
```json
{
  "low_stock": [
    {
      "ingredient": "Tomatoes",
      "current_stock": 1.5,
      "minimum_stock": 5.0,
      "unit": "KG",
      "affected_dishes": ["Caesar Salad", "Margherita Pizza"],
      "recommended_restock": 10.0
    }
  ],
  "out_of_stock": [
    {
      "ingredient": "Mozzarella",
      "minimum_stock": 2.0,
      "unit": "KG",
      "affected_dishes": ["Pizza", "Caprese Salad"]
    }
  ]
}
```

### Error Handling

#### Insufficient Stock on Order Creation
**Status**: 400 Bad Request
```json
{
  "error": "insufficient_stock",
  "message": "No se puede crear el pedido debido a stock insuficiente",
  "details": [
    {
      "dish": "Caesar Salad",
      "ingredient": "Tomatoes",
      "needed": 2.5,
      "available": 1.0,
      "unit": "KG"
    }
  ]
}
```

#### Race Condition (Stock Depleted Between Check and Confirmation)
**Solution**: Use database transaction with SELECT FOR UPDATE
```python
from django.db import transaction

@transaction.atomic
def confirm_order_and_deduct(order):
    # Lock inventory rows
    stocks = InventoryStock.objects.select_for_update().filter(
        ingredient__in=required_ingredients
    )
    
    # Re-check availability
    # Proceed or rollback
```

### Testing Strategy

#### Unit Tests
```python
def test_dish_is_in_stock_when_all_ingredients_available():
    # Create dish with recipe
    # Ensure all ingredients have sufficient stock
    # Assert dish.is_in_stock == True

def test_dish_not_in_stock_when_ingredient_insufficient():
    # Create dish with recipe
    # Set one ingredient stock to 0
    # Assert dish.is_in_stock == False

def test_inventory_deducted_on_order_confirmation():
    # Create order with status=PENDING
    # Record initial stock levels
    # Change order status to CONFIRMED
    # Assert stock levels decreased by recipe amounts
    # Assert InventoryTransaction records created

def test_order_creation_fails_with_insufficient_stock():
    # Set ingredient stock below recipe requirement
    # Attempt to create order
    # Assert 400 Bad Request
    # Assert error message contains ingredient details
```

#### Integration Tests
```python
def test_full_order_flow_with_inventory():
    # 1. Check dish availability (should be in stock)
    # 2. Create order (should succeed)
    # 3. Confirm order (should deduct inventory)
    # 4. Check dish availability (may be out of stock now)
    # 5. Verify transaction audit trail
```

#### Performance Tests
```python
def test_stock_check_performance_with_many_ingredients():
    # Create dish with 20 ingredients
    # Time is_in_stock calculation
    # Assert < 100ms

def test_concurrent_orders_dont_oversell():
    # Create 10 orders simultaneously for same dish
    # Only first N should succeed (based on stock)
    # Others should fail with insufficient stock error
```

### Rollout Plan

#### Phase 1: Read-Only (Week 1)
- Implement is_in_stock calculation
- Add missing_ingredients and max_servings to API
- Deploy to staging
- Test with real data

#### Phase 2: Validation (Week 2)
- Add stock validation on order creation
- Return clear error messages
- Deploy to staging
- User acceptance testing

#### Phase 3: Auto-Deduction (Week 3)
- Implement signal-based inventory deduction
- Add transaction audit trail
- Deploy to staging
- Monitor for data inconsistencies

#### Phase 4: Alerts (Week 4)
- Implement low stock alerts endpoint
- Create kitchen dashboard integration (future)
- Deploy to production

### Monitoring & Alerts

#### Metrics to Track
- Orders failed due to insufficient stock (should be < 5%)
- Average time for stock check (should be < 50ms)
- Inventory transaction creation rate
- Stock level alerts triggered

#### Error Monitoring
- Log all insufficient stock failures
- Alert if > 10 orders fail in 1 hour
- Track race conditions and rollbacks

### Documentation Updates

#### API Documentation
- Update Swagger annotations for all modified endpoints
- Add examples for error responses
- Document new query parameters

#### User Documentation
- Kitchen staff guide for low stock alerts
- Admin guide for inventory monitoring
- FAQ for "dish not available" scenarios

---

**Status**: Specification Complete  
**Next Steps**: Use Spec Kit to implement this feature  
**Estimated Effort**: 2-3 weeks  
**Priority**: High (business requirement)

## How to Implement with Spec Kit

### 1. Review Specification
```bash
# Let Copilot/AI review this spec
/speckit.review
```

### 2. Generate Implementation Plan
```bash
/speckit.plan Implement inventory-order integration as specified in .speckit/features/inventory-order-integration.md
```

### 3. Break Down Tasks
```bash
/speckit.tasks
```

### 4. Execute Implementation
```bash
/speckit.implement
```

### 5. Validate with Spectral
```bash
python manage.py export_openapi --output spec/openapi.json
spectral lint spec/openapi.json -r spec/.spectral.yaml
```
