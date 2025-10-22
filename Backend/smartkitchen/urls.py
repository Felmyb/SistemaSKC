"""
SmartKitchen Connect - URL Configuration
========================================
Standard: IEEE 830
Requirements: RNF-04 (API documentation and traceability)

Main URL router for the SmartKitchen Connect API.

Design Thinking:
    - Ideare: RESTful API design for clarity
    - Evaluate: Well-documented endpoints with OpenAPI
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# OpenAPI/Swagger Schema Configuration (RNF-04)
schema_view = get_schema_view(
    openapi.Info(
        title="SmartKitchen Connect API",
        default_version='v1',
        description="""
        # SmartKitchen Connect API Documentation
        
        **Standard:** IEEE 830  
        **Methodology:** Design Thinking
        
        ## Overview
        RESTful API for restaurant management system providing:
        - User authentication and authorization (RF-05)
        - Order management and tracking (RF-01, RF-04)
        - Inventory control (RF-02)
        - AI-powered analytics (RF-03)
        - Reporting dashboard (RF-06)
        
        ## Authentication
        This API uses JWT (JSON Web Token) authentication.
        
        1. Obtain tokens: `POST /api/auth/token/`
        2. Use access token in header: `Authorization: Bearer <token>`
        3. Refresh token: `POST /api/auth/token/refresh/`
        
        ## Requirements Traceability
        Every endpoint is linked to a functional requirement (RF) or 
        non-functional requirement (RNF) from the IEEE 830 specification.
        
        ## Design Thinking
        This API was designed following Design Thinking principles:
        - **Empathize:** Understanding user needs
        - **Define:** Clear problem statements
        - **Ideare:** Creative solutions
        - **Prototype:** Iterative development
        - **Evaluate:** User testing and feedback
        """,
        terms_of_service="https://smartkitchen.com/terms/",
        contact=openapi.Contact(email="contact@smartkitchen.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin interface (RF-05, RF-06)
    path('admin/', admin.site.urls),
    
    # API Documentation (RNF-04)
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # JWT Authentication (RNF-03)
    path('api/auth/', include('apps.usuarios.urls')),
    
    # Application APIs (modular routing)
    # path('api/', include('apps.orders.urls')),  # RF-01, RF-04
    # path('api/', include('apps.inventory.urls')),  # RF-02
    # path('api/', include('apps.dishes.urls')),
    # path('api/', include('apps.analytics.urls')),  # RF-03
    # path('api/', include('apps.notifications.urls')),  # RF-04
    # path('api/', include('apps.reports.urls')),  # RF-06
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuración del sitio de administración (RF-06)
admin.site.site_header = "Administración - SmartKitchen Connect"
admin.site.site_title = "SmartKitchen Administración"
admin.site.index_title = "Sistema de Gestión de Restaurante"
