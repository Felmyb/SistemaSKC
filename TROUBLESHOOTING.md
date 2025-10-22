# Guía de Solución de Problemas - SmartKitchen Connect

## Errores de Importación en VS Code

### Síntoma
VS Code muestra errores como:
```
Import "pytest" could not be resolved
Import "rest_framework_simplejwt.tokens" could not be resolved
```

### Causa
El analizador de Python (Pylance) está usando un entorno virtual incorrecto o necesita recargar la configuración.

### Solución

#### Opción 1: Recargar VS Code (Recomendado)
1. Presiona `Ctrl+Shift+P` para abrir la paleta de comandos
2. Escribe y selecciona: `Developer: Reload Window`
3. VS Code se recargará y detectará el entorno virtual correcto

#### Opción 2: Seleccionar Intérprete de Python Manualmente
1. Presiona `Ctrl+Shift+P` para abrir la paleta de comandos
2. Escribe y selecciona: `Python: Select Interpreter`
3. Selecciona el intérprete en: `.\venv\Scripts\python.exe`

#### Opción 3: Verificar Configuración
1. Abre el archivo `.vscode/settings.json`
2. Verifica que contenga:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe"
}
```

### Verificación
Para verificar que el entorno está correctamente configurado, ejecuta en la terminal:

```powershell
python -c "import pytest, rest_framework_simplejwt, django; print('✓ OK')"
```

Deberías ver el mensaje `✓ OK` sin errores.

---

## Dependencias Instaladas

El proyecto tiene las siguientes dependencias principales instaladas:

### Core Framework
- Django 5.2.7
- Django REST Framework 3.16.1
- django-cors-headers 4.9.0

### Autenticación
- djangorestframework-simplejwt 5.5.1
- PyJWT 2.10.1

### Documentación API
- drf-yasg 1.21.11

### Testing
- pytest 8.4.2
- pytest-django 4.11.1
- pytest-cov 7.0.0

### Base de Datos
- psycopg2-binary 2.9.11

### Utilidades
- celery 5.5.3
- redis 6.4.0
- pillow 12.0.0
- gunicorn 23.0.0
- whitenoise 6.11.0

---

## Notas sobre Machine Learning (scikit-learn, pandas, numpy)

### Importante
Las bibliotecas de machine learning (scikit-learn, pandas, numpy) **NO están instaladas** por defecto porque requieren Microsoft Visual C++ Build Tools.

### Para Instalar ML Dependencies

#### Paso 1: Instalar Visual C++ Build Tools
1. Descarga desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Ejecuta el instalador
3. Selecciona "Desktop development with C++"
4. Completa la instalación (requiere ~7GB)

#### Paso 2: Instalar Paquetes de ML
```powershell
pip install scikit-learn pandas numpy
```

### Alternativa: Usar Anaconda
Si prefieres no instalar Build Tools, puedes usar Anaconda:
1. Instala Anaconda: https://www.anaconda.com/download
2. Crea un entorno conda:
```powershell
conda create -n smartkitchen python=3.13
conda activate smartkitchen
conda install scikit-learn pandas numpy
pip install -r Backend/requirements.txt
```

---

## Otros Problemas Comunes

### Error: "ModuleNotFoundError"
**Solución:** Asegúrate de haber activado el entorno virtual:
```powershell
.\venv\Scripts\Activate.ps1
```

### Error: "execution of scripts is disabled on this system"
**Solución:** Ejecuta PowerShell como administrador y ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error de Base de Datos PostgreSQL
**Solución:** El proyecto está configurado para usar SQLite3 por defecto en desarrollo. Para usar PostgreSQL:
1. Inicia los servicios Docker:
```powershell
docker-compose up -d
```
2. Configura las variables de entorno en `.env`:
```env
DATABASE_URL=postgresql://smartkitchen:smartkitchen@localhost:5432/smartkitchen
```

---

## Contacto y Soporte

Si encuentras otros problemas:
1. Revisa la documentación en `GETTING_STARTED.md`
2. Verifica la estructura del proyecto en `PROJECT_STRUCTURE.md`
3. Consulta los requisitos en `Docs/requirements/SRS_IEEE830.md`

**Última actualización:** Enero 2025
