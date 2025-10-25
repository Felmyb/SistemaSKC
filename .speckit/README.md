# Spec Kit Integration - SmartKitchen Connect

## ¿Qué es Spec-Driven Development?

**Spec-Driven Development** invierte el enfoque tradicional de desarrollo. En lugar de escribir código y luego documentarlo, defines especificaciones ejecutables que guían la implementación directamente.

## Estructura de Spec Kit

```
.speckit/
├── constitution.md              # Principios y estándares del proyecto
├── architecture.md              # Arquitectura actual del sistema
├── features/                    # Especificaciones de features
│   └── inventory-order-integration.md
└── README.md                    # Este archivo
```

## Herramientas Instaladas

### 1. Spec Kit CLI
- **Instalado con**: `uv tool install specify-cli`
- **Comandos disponibles**:
  - `specify init` - Inicializar nuevo proyecto
  - `specify check` - Verificar herramientas instaladas

### 2. Spectral (OpenAPI Linter)
- **Instalado con**: `npm install -g @stoplight/spectral-cli`
- **Configuración**: `Backend/spec/.spectral.yaml`
- **Uso**: Valida la calidad de la documentación OpenAPI

## Workflow Recomendado

### Para Nuevas Features

#### 1. Definir la Especificación
Crea un archivo en `.speckit/features/` con:
- **Overview**: Qué hace la feature y por qué
- **Requirements Traceability**: RF/RNF relacionados
- **User Stories**: Quién, qué, por qué con acceptance criteria
- **Technical Specification**: Cambios en DB, API, lógica
- **Testing Strategy**: Tests unitarios, integración, performance
- **Rollout Plan**: Fases de implementación

Ver ejemplo completo: `.speckit/features/inventory-order-integration.md`

#### 2. Usar Copilot/AI para Implementar
Con la especificación lista, usa comandos de GitHub Copilot:

```
/speckit.review
# Revisa la especificación y sugiere mejoras

/speckit.plan
# Genera un plan técnico de implementación

/speckit.tasks
# Desglosa en tareas accionables

/speckit.implement
# Implementa las tareas una por una
```

#### 3. Validar con Spectral
Después de implementar cambios en la API:

```bash
# Generar OpenAPI spec actualizado
cd Backend
python manage.py export_openapi --output spec/openapi.json

# Validar calidad de la documentación
spectral lint spec/openapi.json -r spec/.spectral.yaml
```

#### 4. Ejecutar Tests
```bash
cd Backend
pytest --cov=apps --cov-report=html
```

#### 5. Commit y Push
```bash
git add .
git commit -m "feat: [descripción de la feature]"
git push origin main
```

### Para Modificaciones de Features Existentes

1. **Actualizar la especificación** en `.speckit/features/`
2. **Revisar con AI**: Pide a Copilot que compare spec vs código actual
3. **Generar plan de cambios**
4. **Implementar**
5. **Validar** con Spectral y tests

## Principios del Proyecto

Revisa `.speckit/constitution.md` para:
- Estándares de código Django
- Requisitos de testing (80% coverage mínimo)
- Patrones de diseño de API
- Seguridad y performance
- Traceability con IEEE 830

## Arquitectura del Sistema

Consulta `.speckit/architecture.md` para entender:
- Estructura de apps (usuarios, pedidos, platos, inventario)
- Modelos de dominio y relaciones
- Patrones de API REST
- Flujos de datos
- Estrategia de testing

## Integración con CI/CD

El pipeline de Azure DevOps automáticamente:

1. **Ejecuta tests** con pytest
2. **Verifica cobertura** (mínimo 80%)
3. **Genera OpenAPI spec** con `export_openapi`
4. **Valida con Spectral** para calidad de documentación
5. **Publica artefactos** (coverage reports, OpenAPI spec)

Ver: `azure-pipelines.yml`

## Comandos Útiles

### Spec Kit
```bash
# Verificar instalación
specify check

# Ver ayuda
specify --help
```

### OpenAPI Management
```bash
# Generar spec desde código Django
cd Backend
python manage.py export_openapi --output spec/openapi.json

# Validar spec con Spectral
spectral lint spec/openapi.json -r spec/.spectral.yaml

# Servir documentación Swagger (Django dev server)
python manage.py runserver
# Visita: http://localhost:8000/api/swagger/
```

### Testing
```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=apps --cov-report=html

# Test específico
pytest apps/inventario/test_endpoints.py -v

# Solo tests rápidos
pytest -m "not slow"
```

### Desarrollo Local
```bash
# Setup completo (Windows PowerShell)
.\Scripts\setup.ps1

# Migrations
python manage.py makemigrations
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Flujo de Trabajo Completo: Ejemplo

### Implementar "Inventory-Order Integration"

#### Paso 1: Revisar la Especificación
Abre `.speckit/features/inventory-order-integration.md` y revísala completamente.

#### Paso 2: Usar Copilot en VS Code
```
# En el chat de Copilot:
@workspace Revisa la especificación en .speckit/features/inventory-order-integration.md 
y genera un plan de implementación detallado.
```

#### Paso 3: Implementar por Fases

**Fase 1: Cálculo de Stock**
```python
# En apps/platos/serializers.py
class DishDetailSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.SerializerMethodField()
    
    def get_is_in_stock(self, obj):
        # Implementar lógica según spec
        pass
```

**Fase 2: Validación en Orden**
```python
# En apps/pedidos/serializers.py
class OrderCreateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        # Verificar stock antes de crear orden
        pass
```

**Fase 3: Auto-Deducción**
```python
# En apps/pedidos/models.py
from django.db.models.signals import post_save

@receiver(post_save, sender=Order)
def deduct_inventory_on_confirmation(sender, instance, **kwargs):
    # Implementar deducción automática
    pass
```

#### Paso 4: Escribir Tests
```python
# En apps/pedidos/test_inventory_integration.py
def test_order_creation_fails_with_insufficient_stock():
    # Test según acceptance criteria
    pass
```

#### Paso 5: Validar
```bash
# Tests
pytest apps/pedidos/test_inventory_integration.py -v

# Cobertura
pytest --cov=apps.pedidos --cov-report=html

# OpenAPI
python manage.py export_openapi --output spec/openapi.json
spectral lint spec/openapi.json -r spec/.spectral.yaml
```

#### Paso 6: Commit
```bash
git add .
git commit -m "feat: Implementa integración inventario-pedidos

- Agrega validación de stock en creación de órdenes
- Implementa deducción automática al confirmar orden
- Añade alertas de stock bajo
- Tests completos con 100% coverage

Refs: RF-01, RF-02, RNF-04"
git push origin main
```

## Beneficios de Este Enfoque

### 1. Especificaciones como Fuente de Verdad
- El código debe coincidir con la spec, no al revés
- Fácil onboarding para nuevos desarrolladores
- Requirements traceability automática

### 2. Calidad Asegurada
- Spectral valida que la API está bien documentada
- Tests verifican que cumple acceptance criteria
- CI/CD previene regresiones

### 3. Mantenimiento Simplificado
- Cambios futuros empiezan con actualizar la spec
- Historia clara de decisiones arquitectónicas
- Documentación siempre actualizada

### 4. Colaboración Mejorada
- Stakeholders revisan specs antes de implementar
- Menos sorpresas en revisión de código
- Discusiones técnicas basadas en especificaciones

## Recursos Adicionales

### Documentación
- **Spec Kit**: https://github.com/github/spec-kit
- **Spectral**: https://stoplight.io/open-source/spectral
- **OpenAPI 3.0**: https://swagger.io/specification/
- **Django REST Framework**: https://www.django-rest-framework.org/

### Proyecto SmartKitchen
- **Requirements**: `Docs/requirements/`
- **Design Thinking**: `Docs/design-thinking/`
- **API Docs**: http://localhost:8000/api/swagger/ (dev server)
- **Pipeline**: `azure-pipelines.yml`

### Estándares
- **IEEE 830**: Documentación de requisitos
- **RESTful API Design**: Best practices aplicadas
- **Django Best Practices**: Seguidas en todo el proyecto

---

**Última Actualización**: Octubre 25, 2025  
**Mantenido por**: Equipo SmartKitchen Connect  
**Standard**: IEEE 830 + Design Thinking + Spec-Driven Development
