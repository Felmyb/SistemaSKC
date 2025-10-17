# 🚀 SmartKitchen Connect - Guía de Inicio Rápido

**Estándar:** IEEE 830 | **Metodología:** Design Thinking  
**Fecha:** 17 de Octubre, 2025

---

## ✨ Lo Que Se Ha Creado

### 📂 Estructura del Proyecto
✅ Estructura de carpetas modular completa  
✅ Configuración del Backend con Django REST Framework  
✅ Configuración de Docker & Docker Compose  
✅ Infraestructura como Código (IAC)  
✅ Documentación completa  
✅ Scripts automatizados  

### 🎯 Módulos Implementados

| Módulo | Requisitos | Estado | Descripción |
|--------|-------------|--------|-------------|
| **Usuarios** | RF-05, RNF-03 | ✅ **Completo** | Autenticación, roles, permisos |
| **Pedidos** | RF-01, RF-04 | 🟡 **Parcial** | Modelos, interfaz de administración |
| **Inventario** | RF-02 | 🟡 **Parcial** | Modelos para ingredientes y stock |
| **Platillos** | RF-01, RF-02 | 🟡 **Parcial** | Gestión de menú y recetas |

### 📋 Documentación Creada

- ✅ Especificación de Requisitos de Software IEEE 830
- ✅ Documentación del Proceso de Design Thinking
- ✅ Guía de Estructura del Proyecto
- ✅ README del Backend
- ✅ Documentación de IAC
- ✅ Plantillas de Configuración de Entorno

---

## 🏃 Comenzando

### Opción 1: Desarrollo Local (Recomendado para Desarrollo)

#### Paso 1: Prerrequisitos

Asegúrate de tener instalado:
- Python 3.11 o superior
- PostgreSQL 14+ (o usar Docker)
- Git

#### Paso 2: Configuración Inicial

```powershell
# Navegar a la raíz del proyecto
cd C:\Users\coteh\SmartKitchenConnect

# Ejecutar script de configuración automatizado
.\Scripts\setup.ps1
```

Este script hará lo siguiente:
- ✅ Verificar instalación de Python
- ✅ Crear entorno virtual
- ✅ Instalar dependencias
- ✅ Crear archivo .env desde la plantilla
- ✅ Ejecutar migraciones de base de datos
- ✅ Solicitar creación de superusuario

#### Paso 3: Configurar Entorno

Edita `Backend\.env` con tu configuración:

```env
# Configuración esencial
DEBUG=True
SECRET_KEY=tu-clave-secreta-cambiar-esto
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (usar PostgreSQL en producción)
DATABASE_URL=sqlite:///db.sqlite3

# Para PostgreSQL:
# DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/smartkitchen_db
```

#### Paso 4: Iniciar Servidor de Desarrollo

```powershell
cd Backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

#### Paso 5: Acceder a la Aplicación

- 🌐 **Documentación API (Swagger):** http://localhost:8000/api/docs/
- 🔐 **Panel de Administración:** http://localhost:8000/admin/
- 📘 **ReDoc:** http://localhost:8000/api/redoc/

---

### Opción 2: Docker (Recomendado para Entorno Similar a Producción)

#### Paso 1: Prerrequisitos

Asegúrate de tener instalado:
- Docker Desktop para Windows
- Docker Compose

#### Paso 2: Configurar Entorno

```powershell
# Copiar plantilla de entorno
cd Backend
Copy-Item .env.example .env
# Editar .env con tu configuración
```

#### Paso 3: Construir e Iniciar Contenedores

```powershell
# Desde la raíz del proyecto
docker-compose up --build -d
```

Esto iniciará:
- 🐘 Base de datos PostgreSQL (puerto 5432)
- 🔴 Caché Redis (puerto 6379)
- 🐍 Backend Django (puerto 8000)
- 🌐 Proxy inverso Nginx (puerto 80)
- 👷 Trabajador Celery (tareas en segundo plano)
- ⏰ Celery beat (tareas programadas)

#### Paso 4: Crear Superusuario

```powershell
docker-compose exec backend python manage.py createsuperuser
```

#### Paso 5: Acceder a la Aplicación

- 🌐 **API:** http://localhost/api/docs/
- 🔐 **Admin:** http://localhost/admin/

---

## 🧪 Ejecutar Pruebas

### Pruebas Locales

```powershell
# Ejecutar script automatizado de pruebas
.\Scripts\run_tests.ps1
```

Esto hará:
- ✅ Verificar cumplimiento de PEP8 (flake8)
- ✅ Verificar formato de código (black)
- ✅ Ejecutar todas las pruebas con cobertura
- ✅ Generar reporte HTML de cobertura

### Pruebas Manuales

```powershell
cd Backend
.\venv\Scripts\Activate.ps1

# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=apps --cov-report=html

# Ejecutar archivo de prueba específico
pytest apps/users/tests.py

# Ejecutar prueba específica
pytest apps/users/tests.py::TestUserModel::test_create_user
```

---

## 🛠️ Flujo de Trabajo de Desarrollo

### 1. Formateo de Código

```powershell
# Formatear código automáticamente
.\Scripts\format_code.ps1
```

### 2. Crear Nuevas Apps de Django

```powershell
cd Backend
python manage.py startapp nombre_nueva_app apps/nombre_nueva_app
```

Recuerda:
- ✅ Agregar a `INSTALLED_APPS` en `settings.py`
- ✅ Incluir docstrings con trazabilidad de requisitos
- ✅ Escribir pruebas (cobertura mínima 80%)
- ✅ Actualizar enrutamiento de URLs

### 3. Migraciones de Base de Datos

```powershell
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver SQL de migración
python manage.py sqlmigrate nombre_app numero_migracion
```

### 4. Crear Endpoints de API

Sigue este patrón (ejemplo en `apps/users/views.py`):

```python
"""
Docstring del módulo con trazabilidad IEEE 830
Requisitos: RF-XX, RNF-XX
"""

@swagger_auto_schema(
    operation_summary="Descripción del endpoint",
    operation_description="Descripción detallada con enlaces a requisitos",
    # ... Configuración OpenAPI
)
def mi_endpoint(self, request):
    """
    Docstring explicando el endpoint.
    
    Requisitos:
        - RF-XX: Descripción del requisito
    
    Design Thinking:
        - Fase: Cómo esto aborda las necesidades del usuario
    """
    # Implementación
```

---

## 📚 Referencia de Comandos Clave

### Gestión de Django

```powershell
# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver

# Shell de Django
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic

# Verificar problemas
python manage.py check
```

### Comandos de Docker

```powershell
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f backend

# Reconstruir contenedores
docker-compose up --build

# Ejecutar comandos en contenedor
docker-compose exec backend python manage.py migrate

# Eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v
```

### Flujo de Trabajo Git

```powershell
# Crear rama de funcionalidad
git checkout -b feature/RF-XX-descripcion

# Preparar cambios
git add .

# Commit con mensaje descriptivo
git commit -m "feat(modulo): Descripción (RF-XX, RNF-XX)"

# Enviar a remoto
git push origin feature/RF-XX-descripcion
```

---

## 📖 Enlaces de Documentación

| Documento | Ubicación | Propósito |
|----------|----------|---------|
| **README Principal** | `/README.md` | Visión general del proyecto |
| **IEEE 830 SRS** | `/Docs/requirements/SRS_IEEE830.md` | Especificación de requisitos |
| **Design Thinking** | `/Docs/design-thinking/process.md` | Documentación de metodología |
| **Estructura del Proyecto** | `/PROJECT_STRUCTURE.md` | Estructura completa de archivos |
| **Guía Backend** | `/Backend/README.md` | Documentación específica del backend |
| **Guía IAC** | `/IAC/README.md` | Documentación de infraestructura |
| **Docs API** | `http://localhost:8000/api/docs/` | Documentación interactiva de API |

---

## 🎯 Próximos Pasos de Desarrollo

### Tareas Inmediatas (Semana 1-2)

1. **Completar Módulo de Pedidos**
   - [ ] Crear serializers (`apps/orders/serializers.py`)
   - [ ] Crear vistas (`apps/orders/views.py`)
   - [ ] Crear enrutamiento URL (`apps/orders/urls.py`)
   - [ ] Escribir pruebas unitarias
   - [ ] Probar con Postman/Swagger

2. **Completar Módulo de Inventario**
   - [ ] Crear interfaz de administración
   - [ ] Crear serializers y vistas
   - [ ] Implementar señales de deducción automática
   - [ ] Crear sistema de alertas de bajo stock

3. **Completar Módulo de Platillos**
   - [ ] Crear interfaz de administración
   - [ ] Crear serializers y vistas
   - [ ] Vincular recetas con inventario

### Tareas a Corto Plazo (Semana 3-4)

4. **Módulo de Analítica** (RF-03)
   - [ ] Configurar pipeline de ML
   - [ ] Crear modelos de predicción
   - [ ] Endpoints de API para pronósticos

5. **Módulo de Notificaciones** (RF-04)
   - [ ] Configuración de WebSocket
   - [ ] Integración de email
   - [ ] Integración de SMS (opcional)

6. **Módulo de Reportes** (RF-06)
   - [ ] API de dashboard
   - [ ] Endpoints de agregación de datos
   - [ ] Funcionalidad de exportación (PDF, Excel)

### Tareas a Mediano Plazo (Semana 5-8)

7. **Desarrollo Frontend**
   - [ ] Inicializar proyecto React
   - [ ] Configurar autenticación
   - [ ] Crear interfaces específicas por rol
   - [ ] Implementar actualizaciones en tiempo real

---

## ❓ Solución de Problemas

### Problema: Errores de importación en VS Code

**Solución:** Configurar intérprete de Python
1. Presiona `Ctrl+Shift+P`
2. Escribe "Python: Select Interpreter"
3. Elige el entorno virtual: `.\Backend\venv\Scripts\python.exe`

### Problema: Errores de migración de base de datos

**Solución:** Reiniciar base de datos (⚠️ solo desarrollo)
```powershell
rm Backend\db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Problema: Puerto ya en uso

**Solución:** Cambiar puerto o terminar proceso
```powershell
# Usar puerto diferente
python manage.py runserver 8080

# O encontrar y terminar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <id_proceso> /F
```

### Problema: Los contenedores Docker no inician

**Solución:** Verificar logs y reconstruir
```powershell
docker-compose logs
docker-compose down
docker-compose up --build
```

---

## 🤝 Estándares de Desarrollo

### Calidad de Código (RNF-02)

- ✅ **Cumplimiento PEP8** - Ejecutar flake8 antes de hacer commit
- ✅ **Docstrings** - Todas las funciones/clases deben tener docstrings
- ✅ **Type hints** - Usar anotaciones de tipo de Python cuando sea aplicable
- ✅ **Comentarios** - Explicar lógica compleja con enlaces a requisitos
- ✅ **Pruebas** - Cobertura mínima del 80%

### Formato de Mensajes de Commit

```
<tipo>(<alcance>): <asunto> (<requisitos>)

<cuerpo>

<pie>
```

**Tipos:** feat, fix, docs, style, refactor, test, chore

**Ejemplo:**
```
feat(orders): Agregar listado de pedidos basado en prioridad (RF-01)

Implementado sistema de prioridad visual con codificación por colores.
El personal de cocina ahora puede identificar fácilmente pedidos urgentes.

Closes #123
```

---

## 📞 Soporte y Recursos

### Documentación
- **Django:** https://docs.djangoproject.com/
- **DRF:** https://www.django-rest-framework.org/
- **Docker:** https://docs.docker.com/

### Estándar IEEE 830
- El proyecto sigue el estándar IEEE 830-1998 SRS
- Todos los requisitos documentados en `/Docs/requirements/SRS_IEEE830.md`

### Design Thinking
- Metodología de 5 fases aplicada en todo el proyecto
- Proceso documentado en `/Docs/design-thinking/process.md`

---

## ✅ Lista de Verificación para Nuevos Desarrolladores

- [ ] Leer `/README.md`
- [ ] Leer `/Docs/requirements/SRS_IEEE830.md`
- [ ] Leer `/Docs/design-thinking/process.md`
- [ ] Ejecutar `.\Scripts\setup.ps1`
- [ ] Crear cuenta de superusuario
- [ ] Acceder a Swagger UI en http://localhost:8000/api/docs/
- [ ] Explorar Django admin en http://localhost:8000/admin/
- [ ] Ejecutar pruebas con `.\Scripts\run_tests.ps1`
- [ ] Leer código backend en `apps/users` como ejemplo
- [ ] Configurar IDE (intérprete Python, linting)
- [ ] Revisar flujo de trabajo Git y estándares de commit

---

**🎉 ¡Felicidades! ¡Estás listo para comenzar a desarrollar SmartKitchen Connect!**

**Recuerda:** Cada funcionalidad debe ser:
- 📋 Vinculada a un requisito (RF o RNF)
- 🎨 Diseñada con empatía (Design Thinking)
- 📝 Bien documentada (IEEE 830)
- ✅ Probada exhaustivamente (cobertura 80%+)
- 🔒 Segura por diseño (RNF-03)

**¡Feliz codificación! 🚀**

---

*Última Actualización: 17 de Octubre, 2025*  
*Equipo de Desarrollo SmartKitchen Connect*
