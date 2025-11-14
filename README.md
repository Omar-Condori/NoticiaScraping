# 📰 Sistema de Scraping de Noticias

Sistema completo de scraping de noticias con backend en Flask (Python) y frontend en React. Permite agregar fuentes de noticias, hacer scraping automático, programar tareas, buscar noticias y exportar datos.

## 🚀 Características

- ✅ Scraping automático de noticias de múltiples fuentes
- ✅ Autenticación JWT
- ✅ Programación de tareas de scraping (Scheduler)
- ✅ Búsqueda avanzada de noticias
- ✅ Estadísticas y análisis
- ✅ Exportación de datos (CSV, JSON, TXT)
- ✅ Paginación de noticias
- ✅ Filtrado por fuente y categoría
- ✅ Extracción robusta de títulos, imágenes, descripciones y fechas

## 📋 Requisitos Previos

### Backend
- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

### Frontend
- Node.js 18 o superior
- npm o yarn

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd NOTICIA
```

### 2. Configurar Base de Datos PostgreSQL

1. **Instalar PostgreSQL** (si no lo tienes):
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   
   # Windows
   # Descargar desde https://www.postgresql.org/download/windows/
   ```

2. **Crear la base de datos**:
   ```bash
   # Conectar a PostgreSQL
   psql -U postgres
   
   # Crear base de datos
   CREATE DATABASE noticias_db;
   
   # Salir
   \q
   ```

3. **Configurar credenciales** en `scraping-noticias-backend/database.py`:
   
   Abre el archivo `scraping-noticias-backend/database.py` y busca la sección `__init__` de la clase `Database`. Modifica las credenciales:
   
   ```python
   self.config = {
       'host': 'localhost',
       'user': 'postgres',  # Tu usuario de PostgreSQL
       'password': 'tu_password',  # ⚠️ CAMBIA ESTO con tu contraseña
       'database': 'noticias_db',
       'port': 5432
   }
   ```
   
   **Nota**: Si no tienes contraseña configurada en PostgreSQL, déjala como string vacío: `'password': ''`

### 3. Configurar Backend (Python/Flask)

1. **Navegar al directorio del backend**:
   ```bash
   cd scraping-noticias-backend
   ```

2. **Crear entorno virtual** (recomendado):
   ```bash
   python3 -m venv venv
   
   # Activar entorno virtual
   # macOS/Linux:
   source venv/bin/activate
   
   # Windows:
   venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar que PostgreSQL esté corriendo**:
   ```bash
   # macOS/Linux
   pg_isready
   
   # O verificar el servicio
   brew services list  # macOS
   sudo systemctl status postgresql  # Linux
   ```

5. **Ejecutar el backend**:
   ```bash
   python app.py
   # o
   python3 app.py
   ```

   El servidor se iniciará en `http://localhost:8001`
   La documentación Swagger estará en `http://localhost:8001/docs`
   
   **Primera ejecución**: El sistema creará automáticamente las tablas necesarias en la base de datos.

### 4. Configurar Frontend (React)

1. **Abrir una nueva terminal** y navegar al directorio del frontend:
   ```bash
   cd news-scraper-frontend
   ```

2. **Instalar dependencias**:
   ```bash
   npm install
   # o
   yarn install
   ```

3. **Verificar configuración de API** en `src/services/api.js`:
   ```javascript
   const API_URL = 'http://localhost:8001/api/v1';
   ```
   Asegúrate de que la URL coincida con la del backend.

4. **Ejecutar el frontend**:
   ```bash
   npm run dev
   # o
   yarn dev
   ```

   La aplicación se abrirá en `http://localhost:5173` (o el puerto que Vite asigne)
   
   **Nota**: Si el puerto 5173 está ocupado, Vite usará el siguiente disponible (5174, 5175, etc.)

## 📝 Uso Inicial

### 1. Crear un Usuario

1. Abre `http://localhost:5173/register`
2. Completa el formulario de registro:
   - Nombre de usuario
   - Email
   - Contraseña
3. Serás redirigido automáticamente al dashboard

### 2. Agregar una Fuente de Noticias

1. Ve a la sección **"Fuentes"** en el menú lateral
2. Haz clic en **"Nueva Fuente"**
3. Completa:
   - **Nombre**: Nombre de la fuente (ej: "RPP Noticias")
   - **URL**: URL del sitio web (ej: "https://rpp.pe")
4. Haz clic en **"Agregar Fuente"**

   ⚠️ **Nota**: Los selectores CSS se asignan automáticamente. Si el scraping no funciona correctamente, puedes editar los selectores manualmente.

### 3. Ejecutar Scraping

1. Ve a la sección **"Dashboard"**
2. Haz clic en **"Ejecutar Scraping"**
3. Espera a que termine el proceso
4. Las noticias aparecerán en la sección **"Noticias"**

### 4. Ver Noticias

1. Ve a la sección **"Noticias"**
2. Usa los filtros para:
   - Filtrar por fuente
   - Filtrar por categoría
   - Cambiar el número de noticias por página
3. Navega entre páginas usando los controles de paginación

## 🔧 Solución de Problemas

### Backend no se conecta a PostgreSQL

**Error**: `❌ Error conectando a PostgreSQL: ...`

**Solución**:
1. Verifica que PostgreSQL esté corriendo:
   ```bash
   pg_isready
   ```
2. Verifica las credenciales en `database.py`
3. Verifica que la base de datos `noticias_db` exista:
   ```bash
   psql -U postgres -l | grep noticias_db
   ```

### Frontend no se conecta al Backend

**Error**: `Failed to fetch` o errores de CORS

**Solución**:
1. Verifica que el backend esté corriendo en `http://localhost:8001`
2. Verifica la URL en `src/services/api.js`
3. Verifica que CORS esté habilitado en el backend (ya está configurado por defecto)

### No se encuentran noticias después del scraping

**Posibles causas**:
1. Los selectores CSS no son correctos para la fuente
2. La estructura HTML del sitio cambió
3. El sitio bloquea el scraping
4. No se encontraron artículos con el selector configurado

**Solución**:
1. Revisa los logs del backend para ver errores
2. El sistema intenta automáticamente selectores alternativos si no encuentra artículos
3. Edita los selectores de la fuente manualmente desde la sección "Fuentes"
4. Verifica que la URL de la fuente sea correcta y accesible

### El filtro por fuente no muestra noticias

**Causa**: El filtro puede no estar aplicándose correctamente

**Solución**:
1. Verifica en los logs del backend que el `fuente_id` se esté recibiendo correctamente
2. Asegúrate de que las noticias tengan el `fuente_id` correcto en la base de datos
3. Recarga la página después de cambiar el filtro
4. Verifica que la fuente seleccionada tenga noticias asociadas

### Las imágenes no se muestran

**Causa**: Las URLs de imágenes pueden estar bloqueadas por CORS o ser inválidas

**Solución**:
1. El sistema hace scraping profundo automáticamente cuando faltan imágenes
2. Verifica los logs del backend para ver si se están extrayendo imágenes
3. Algunas imágenes pueden requerir configuración CORS en el servidor de origen

### Error "Cannot read properties of undefined"

**Causa**: Datos no inicializados correctamente

**Solución**:
1. Recarga la página
2. Verifica que el backend esté respondiendo correctamente
3. Revisa la consola del navegador para más detalles

## 📁 Estructura del Proyecto

```
NOTICIA/
├── scraping-noticias-backend/    # Backend Flask
│   ├── app.py                     # Aplicación principal
│   ├── scraper.py                 # Lógica de scraping
│   ├── database.py                # Conexión y operaciones BD
│   ├── auth.py                    # Autenticación
│   ├── scheduler.py               # Programación de tareas
│   ├── busqueda.py                # Búsqueda avanzada
│   ├── estadisticas.py            # Estadísticas
│   ├── exportar.py                # Exportación de datos
│   ├── requirements.txt            # Dependencias Python
│   └── venv/                      # Entorno virtual (no incluir en git)
│
└── news-scraper-frontend/          # Frontend React
    ├── src/
    │   ├── components/            # Componentes React
    │   ├── pages/                 # Páginas
    │   ├── hooks/                 # Custom hooks
    │   ├── services/              # Servicios API
    │   └── context/               # Context API
    ├── package.json               # Dependencias Node
    └── vite.config.js             # Configuración Vite
```

## 🔐 Variables de Entorno (Opcional)

Para mayor seguridad, puedes usar variables de entorno:

### Backend

Crea un archivo `.env` en `scraping-noticias-backend/`:

```env
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=tu_password
DB_NAME=noticias_db
DB_PORT=5432
JWT_SECRET_KEY=tu-super-secreto-cambiar-en-produccion-2025
```

Luego modifica `database.py` para leer estas variables.

### Frontend

Crea un archivo `.env` en `news-scraper-frontend/`:

```env
VITE_API_URL=http://localhost:8001/api/v1
```

## 🚀 Despliegue en Producción

### Backend

1. **Usar un servidor WSGI** como Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8001 app:app
   ```

2. **Usar Nginx como proxy reverso** (recomendado)

3. **Configurar HTTPS** con Let's Encrypt

### Frontend

1. **Construir para producción**:
   ```bash
   npm run build
   ```

2. **Servir con Nginx o similar**:
   ```bash
   # Los archivos estarán en dist/
   # Configurar Nginx para servir desde dist/
   ```

## 📚 Endpoints de la API

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/perfil` - Obtener perfil (requiere JWT)

### Scraping
- `POST /api/v1/scraping/ejecutar` - Ejecutar scraping (requiere JWT)
  - Query params: `limite` (opcional), `fuente_id` (opcional), `guardar` (opcional)

### Noticias
- `GET /api/v1/noticias` - Listar noticias con paginación
  - Query params: `limite`, `offset`, `fuente_id` (opcional), `categoria` (opcional)
- `GET /api/v1/noticias/contar` - Contar noticias
- `DELETE /api/v1/noticias` - Eliminar todas las noticias
- `GET /api/v1/noticias/buscar` - Búsqueda avanzada
- `POST /api/v1/noticias/buscar/palabras-clave` - Búsqueda por palabras clave
- `GET /api/v1/noticias/exportar` - Exportar noticias (CSV, JSON, TXT)

### Fuentes
- `GET /api/v1/fuentes` - Listar fuentes
  - Query params: `activas` (true/false)
- `POST /api/v1/fuentes` - Agregar fuente (solo requiere `nombre` y `url`)
- `GET /api/v1/fuentes/{id}` - Obtener fuente específica
- `PUT /api/v1/fuentes/{id}` - Actualizar fuente
- `DELETE /api/v1/fuentes/{id}` - Eliminar fuente

### Scheduler
- `GET /api/v1/scheduler/tareas` - Listar tareas programadas
- `POST /api/v1/scheduler/tareas` - Crear tarea programada
- `GET /api/v1/scheduler/tareas/{nombre}` - Obtener tarea específica
- `DELETE /api/v1/scheduler/tareas/{nombre}` - Eliminar tarea
- `POST /api/v1/scheduler/tareas/{nombre}/pausar` - Pausar tarea
- `POST /api/v1/scheduler/tareas/{nombre}/reanudar` - Reanudar tarea

### Estadísticas
- `GET /api/v1/estadisticas` - Estadísticas generales
- `GET /api/v1/estadisticas/tendencias?dias=7` - Tendencias por día
- `GET /api/v1/estadisticas/top-fuentes?limite=5` - Top fuentes

### Categorías
- `GET /api/v1/categorias` - Listar todas las categorías

### Documentación Completa
Visita `http://localhost:8001/docs` cuando el backend esté corriendo para ver la documentación interactiva de Swagger.

## 🐛 Reportar Problemas

Si encuentras algún problema:

1. **Revisa los logs del backend** en la terminal donde ejecutaste `python app.py`
2. **Revisa la consola del navegador** (F12 → Console)
3. **Verifica que todas las dependencias estén instaladas**:
   ```bash
   # Backend
   pip list | grep -E "flask|psycopg2|beautifulsoup4"
   
   # Frontend
   npm list react react-dom
   ```
4. **Verifica que PostgreSQL esté corriendo**:
   ```bash
   pg_isready
   ```
5. **Verifica la conexión a la base de datos**:
   ```bash
   psql -U postgres -d noticias_db -c "SELECT COUNT(*) FROM noticias;"
   ```

### Problemas Comunes

#### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

#### Error: "Connection refused" en PostgreSQL
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

#### Error: "Cannot read properties of undefined"
- Recarga la página (F5)
- Verifica que el backend esté respondiendo
- Revisa la consola del navegador para más detalles

#### Las noticias no se filtran por fuente
- Verifica que el `fuente_id` se esté enviando correctamente
- Revisa los logs del backend para ver los parámetros recibidos
- Asegúrate de que las noticias tengan el `fuente_id` correcto

## 📄 Licencia

Este proyecto es de código abierto.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📖 Guía Rápida de Uso

### Primeros Pasos

1. **Iniciar PostgreSQL**:
   ```bash
   # macOS
   brew services start postgresql
   
   # Linux
   sudo systemctl start postgresql
   ```

2. **Iniciar Backend** (Terminal 1):
   ```bash
   cd scraping-noticias-backend
   source venv/bin/activate  # Si usas entorno virtual
   python app.py
   ```

3. **Iniciar Frontend** (Terminal 2):
   ```bash
   cd news-scraper-frontend
   npm run dev
   ```

4. **Abrir en el navegador**: `http://localhost:5173`

5. **Registrarse**: Crear una cuenta nueva

6. **Agregar fuente**: Ir a "Fuentes" → "Nueva Fuente"

7. **Ejecutar scraping**: Ir a "Dashboard" → "Ejecutar Scraping"

8. **Ver noticias**: Ir a "Noticias"

## 🔍 Verificación de Instalación

### Backend
```bash
cd scraping-noticias-backend
python -c "import flask, psycopg2, bs4; print('✅ Todas las dependencias instaladas')"
```

### Frontend
```bash
cd news-scraper-frontend
npm list react react-dom react-router-dom
```

### Base de Datos
```bash
psql -U postgres -d noticias_db -c "\dt"
# Deberías ver las tablas: usuarios, fuentes, noticias
```

## 📝 Notas Importantes

- ⚠️ **Cambiar JWT_SECRET_KEY en producción**: Edita `app.py` línea 20
- ⚠️ **Configurar contraseña de PostgreSQL**: Edita `database.py` línea 13
- ✅ El sistema crea las tablas automáticamente en la primera ejecución
- ✅ Los selectores CSS se asignan automáticamente al agregar fuentes
- ✅ El scraping profundo se ejecuta automáticamente cuando faltan datos

## 🎯 Próximos Pasos

Después de la instalación:
1. Agrega tus fuentes de noticias favoritas
2. Configura tareas programadas en "Scheduler"
3. Explora las estadísticas en "Estadísticas"
4. Usa la búsqueda avanzada para encontrar noticias específicas

---

**Desarrollado con ❤️ usando Flask, React y PostgreSQL**

**Versión**: 3.0.0  
**Última actualización**: 2025

