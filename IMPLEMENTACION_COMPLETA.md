# 📚 DOCUMENTACIÓN COMPLETA - Sistema de Scraping de Noticias

## 📖 Índice

1. [Descripción General del Proyecto](#descripción-general-del-proyecto)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)  
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Requisitos del Sistema](#requisitos-del-sistema)
6. [Instalación Completa](#instalación-completa)
7. [Configuración Detallada](#configuración-detallada)
8. [Funcionalidades Principales](#funcionalidades-principales)
9. [API Endpoints](#api-endpoints)
10. [Base de Datos](#base-de-datos)
11. [Autenticación y Seguridad](#autenticación-y-seguridad)
12. [Sistema de Roles](#sistema-de-roles)
13. [Sistema de Planes y Pagos](#sistema-de-planes-y-pagos)
14. [Despliegue](#despliegue)
15. [Solución de Problemas](#solución-de-problemas)

---

## 📝 Descripción General del Proyecto

**NoticiaScraping** es un sistema completo y profesional de web scraping de noticias que permite a los usuarios extraer, almacenar, buscar y exportar noticias de múltiples fuentes web. El sistema está diseñado con una arquitectura moderna de separación entre frontend y backend, implementando las mejores prácticas de desarrollo web.

### Características Principales

- **Web Scraping Automático**: Extracción inteligente de noticias desde múltiples fuentes configurables
- **Autenticación JWT**: Sistema seguro de autenticación basado en tokens
- **Multi-tenant**: Separación completa de datos por usuario
- **Sistema de Roles**: Diferenciación entre usuarios normales y administradores
- **Planes y Suscripciones**: Sistema completo de monetización con límites personalizables
- **Pagos Integrados**: Soporte para Yape, PayPal y Stripe
- **Programación de Tareas**: Scheduler para scraping automático periódico
- **Búsqueda Avanzada**: Motor de búsqueda con filtros múltiples
- **Exportación de Datos**: Exportación en formatos CSV, JSON y TXT
- **Panel de Administración**: Dashboard completo para gestión del sistema
- **Chatbot con IA**: Asistente inteligente powered by Google Gemini
- **Modo Oscuro/Claro**: Interfaz con temas personalizables
- **Responsive Design**: Diseño adaptativo para todo tipo de dispositivos

---

## 🏗️ Arquitectura del Sistema

El proyecto utiliza una **arquitectura cliente-servidor** con separación completa entre frontend y backend:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           React Frontend (Puerto 5173)               │   │
│  │  • React 18 + Vite                                   │   │
│  │  • React Router DOM                                  │   │
│  │  • TailwindCSS                                       │   │
│  │  • Axios para API calls                              │   │
│  │  • Context API para estado global                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/REST API
                           │ JWT Authentication
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       SERVIDOR                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Flask Backend (Puerto 8001)                 │   │
│  │  • Flask 3.1.2                                       │   │
│  │  • Flask-JWT-Extended                                │   │
│  │  • BeautifulSoup4 para scraping                      │   │
│  │  • APScheduler para tareas                           │   │
│  │  • Integración con APIs de pago                      │   │
│  │  • Google Gemini AI para chatbot                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ psycopg2
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   BASE DE DATOS                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         PostgreSQL (Puerto 5432)                     │   │
│  │  • 7 tablas principales                              │   │
│  │  • Relaciones con foreign keys                       │   │
│  │  • Índices para optimización                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Usuario** interactúa con la interfaz React
2. **Frontend** hace peticiones HTTP a la API REST
3. **Backend** procesa las peticiones, valida JWT, ejecuta lógica de negocio
4. **Scraper** extrae datos de sitios web externos cuando se solicita
5. **Base de Datos** almacena y recupera información
6. **Backend** retorna respuesta en formato JSON
7. **Frontend** renderiza los datos en la interfaz

---

## 💻 Tecnologías Utilizadas

### Backend (Python/Flask)

#### Framework Principal
- **Flask 3.1.2**: Microframework web para Python, ligero y extensible
- **Werkzeug 3.1.3**: Biblioteca WSGI utilizada por Flask

#### Autenticación y Seguridad
- **Flask-JWT-Extended 4.6.0**: Manejo de JSON Web Tokens para autenticación
- **PyJWT 2.9.0**: Biblioteca para codificación/decodificación de JWT
- **Werkzeug.security**: Para hash de contraseñas (bcrypt)

#### Base de Datos
- **psycopg2-binary 2.9.11**: Adaptador PostgreSQL para Python
- **PostgreSQL**: Base de datos relacional robusta y escalable

#### Web Scraping
- **BeautifulSoup4 4.14.2**: Parser HTML/XML para extraer datos de páginas web
- **lxml 6.0.2**: Parser rápido y eficiente XML/HTML
- **requests 2.32.5**: Cliente HTTP para realizar peticiones web
- **soupsieve 2.8**: Selectores CSS para BeautifulSoup

#### Programación de Tareas
- **APScheduler 3.10.4**: Scheduler avanzado para programación de tareas periódicas
- **pytz 2025.2**: Manejo de zonas horarias
- **tzlocal 5.3.1**: Detecta zona horaria local del sistema

#### Pagos e Integración
- **stripe 10.12.0**: Integración con Stripe para pagos con tarjeta
- **paypalrestsdk 1.13.1**: SDK oficial de PayPal para procesamiento de pagos
- **qrcode 7.4.2**: Generación de códigos QR para Yape
- **Pillow 10.4.0**: Manipulación de imágenes (para códigos QR)
- **pypng 0.20220715.0**: Manejo de archivos PNG

#### Inteligencia Artificial
- **google-generativeai 0.3.2**: SDK de Google Gemini AI para chatbot
- **google-ai-generativelanguage 0.4.0**: Cliente para API de Google AI
- **protobuf 4.25.8**: Protocol Buffers para comunicación con APIs de Google
- **grpcio 1.76.0**: Framework RPC de Google
- **tqdm 4.67.1**: Barras de progreso para operaciones largas

#### Documentación y CORS
- **flask-swagger-ui 5.21.0**: Interfaz Swagger UI para documentación de API
- **flask-cors 6.0.1**: Manejo de Cross-Origin Resource Sharing

#### Utilidades
- **certifi 2025.10.5**: Certificados SSL root
- **charset-normalizer 3.4.4**: Detección y normalización de encodings
- **urllib3 2.5.0**: Cliente HTTP con pooling
- **idna 3.11**: Soporte para dominios internacionalizados
- **click 8.3.0**: Creación de interfaces de línea de comandos
- **Jinja2 3.1.6**: Motor de templates
- **blinker 1.9.0**: Señales para eventos
- **typing_extensions 4.15.0**: Extensiones de tipado para Python

### Frontend (React/JavaScript)

#### Framework y Build Tool
- **React 18.3.1**: Biblioteca JavaScript para construcción de interfaces de usuario
- **React-DOM 18.3.1**: Package de React para manipulación del DOM
- **Vite 5.3.3**: Build tool moderna y rápida con Hot Module Replacement

#### Enrutamiento
- **React Router DOM 6.26.0**: Enrutamiento declarativo para React

#### Comunicación HTTP
- **Axios 1.7.2**: Cliente HTTP basado en promesas para el navegador

#### UI y Estilos
- **TailwindCSS 3.4.4**: Framework CSS utility-first
- **PostCSS 8.4.39**: Herramienta para transformar CSS
- **Autoprefixer 10.4.19**: Plugin PostCSS para agregar prefijos de vendor automáticamente
- **lucide-react 0.263.1**: Biblioteca de iconos SVG

#### Notificaciones
- **react-hot-toast 2.4.1**: Notificaciones toast elegantes y personalizables

#### Gráficos y Visualización
- **recharts 2.15.4**: Biblioteca de gráficos composables para React

#### Utilidades de Fecha
- **date-fns 3.6.0**: Biblioteca moderna de utilidades para fechas en JavaScript

#### Herramientas de Desarrollo
- **@vitejs/plugin-react 4.3.1**: Plugin oficial de Vite para React
- **@types/react 18.3.3**: Definiciones TypeScript para React
- **@types/react-dom 18.3.0**: Definiciones TypeScript para React-DOM

### Base de Datos

#### PostgreSQL 12+
- Base de datos relacional objeto-relacional de código abierto
- Soporte para JSONB para almacenar selectores CSS
- Triggers y funciones almacenadas
- Índices B-tree y GIN para búsquedas rápidas
- Soporte para transacciones ACID
- Full-text search nativo
- Manejo de conexiones concurrentes

---

## 📁 Estructura del Proyecto

```
NoticiaScraping/
│
├── scraping-noticias-backend/         # Backend Flask
│   ├── venv/                          # Entorno virtual Python (no versionado)
│   ├── __pycache__/                   # Cache de Python (no versionado)
│   │
│   ├── app.py                         # Aplicación principal Flask
│   ├── requirements.txt               # Dependencias Python
│   │
│   ├── database.py                    # Operaciones de base de datos
│   ├── scraper.py                     # Lógica de scraping
│   ├── auth.py                        # Sistema de autenticación
│   ├── scheduler.py                   # Programación de tareas automáticas
│   ├── busqueda.py                    # Motor de búsqueda avanzada
│   ├── estadisticas.py                # Generación de estadísticas
│   ├── exportar.py                    # Exportación de datos
│   ├── payments.py                    # Procesamiento de pagos
│   ├── chatbot.py                     # Chatbot con IA de Google
│   ├── middleware.py                  # Middlewares (admin_required, etc.)
│   │
│   ├── crear_admin.py                 # Script para crear usuario admin
│   ├── agregar_fuentes.py             # Script para agregar fuentes de ejemplo
│   ├── actualizar_paises.py           # Script para actualizar países
│   ├── migrar_bd.py                   # Migraciones de base de datos
│   ├── verificar_db.py                # Verificación de estructura de BD
│   ├── debug_dashboard.py             # Herramientas de debug
│   ├── admin_stats.py                 # Estadísticas administrativas
│   ├── ejecutar_historico.py          # Scraping histórico
│   ├── scraping_historico.py          # Lógica de scraping histórico
│   ├── activar_mi_premium.py          # Activación de planes premium
│   ├── test_rpp.py                    # Tests de scraping
│   │
│   ├── swagger.json                   # Especificación OpenAPI

│
├── news-scraper-frontend/             # Frontend React
│   ├── node_modules/                  # Dependencias npm (no versionado)
│   ├── dist/                          # Build de producción (no versionado)
│   │
│   ├── public/                        # Archivos estáticos públicos
│   │
│   ├── src/                           # Código fuente
│   │   ├── components/                # Componentes React
│   │   │   ├── Layout/                # Layout principal
│   │   │   │   └── Layout.jsx
│   │   │   ├── Dashboard/             # Componentes del dashboard
│   │   │   ├── News/                  # Componentes de noticias
│   │   │   ├── Sources/               # Gestión de fuentes
│   │   │   ├── Scheduler/             # Programador de tareas
│   │   │   ├── Statistics/            # Estadísticas
│   │   │   ├── Plans/                 # Planes y suscripciones
│   │   │   ├── Payments/              # Pagos
│   │   │   └── Admin/                 # Panel de administración
│   │   │
│   │   ├── pages/                     # Páginas principales
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── NewsPage.jsx
│   │   │   ├── SourcesPage.jsx
│   │   │   ├── SchedulerPage.jsx
│   │   │   ├── StatsPage.jsx
│   │   │   ├── PlansPage.jsx
│   │   │   └── AdminPage.jsx
│   │   │
│   │   ├── context/                   # Context API
│   │   │   ├── AppContext.jsx         # Estado global de la app
│   │   │   └── ThemeContext.jsx       # Tema dark/light
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   └── useAuth.js
│   │   │
│   │   ├── services/                  # Servicios de API
│   │   │   └── api.js                 # Cliente Axios con endpoints
│   │   │
│   │   ├── utils/                     # Utilidades
│   │   │   └── formatters.js
│   │   │
│   │   ├── App.jsx                    # Componente principal
│   │   ├── main.jsx                   # Entry point
│   │   └── index.css                  # Estilos globales
│   │
│   ├── index.html                     # HTML principal
│   ├── package.json                   # Dependencias npm
│   ├── package-lock.json              # Lock file de npm
│   ├── vite.config.js                 # Configuración de Vite
│   ├── tailwind.config.js             # Configuración de Tailwind
│   ├── postcss.config.js              # Configuración de PostCSS
│   ├── eslint.config.js               # Configuración de ESLint
│   └── README.md                      # Documentación del frontend
│
├── README.md                          # Documentación principal
├── IMPLEMENTACION_COMPLETA.md         # Este archivo
└── .gitignore                         # Archivos ignorados por Git
```

---

## ⚙️ Requisitos del Sistema

### Sistema Operativo
- **macOS**: 10.15 Catalina o superior
- **Linux**: Ubuntu 20.04+, Debian 10+, RHEL 8+, o equivalente
- **Windows**: Windows 10/11 con WSL2 (recomendado) o nativo

### Software Requerido

#### Backend
- **Python**: 3.11.x o 3.12.x (⚠️ NO usar 3.14, tiene problemas de compatibilidad)
- **PostgreSQL**: 12.x o superior (recomendado 14.x o 15.x)
- **pip**: 21.0 o superior (gestor de paquetes de Python)

#### Frontend
- **Node.js**: 18.x o superior (Requerido solo para desarrollo/build del frontend)
- **npm**: 9.x o superior (incluido con Node.js)

#### Opcional (para despliegue)
- **Nginx**: 1.18 o superior (proxy reverso)
- **Gunicorn**: 20.1 o superior (servidor WSGI para Flask)
- **Docker**: 20.10 o superior (containerización)
- **pm2**: 5.3 o superior (gestor de procesos Node.js)

### Hardware Recomendado

#### Desarrollo
- **CPU**: 2 núcleos o más
- **RAM**: 4 GB mínimo, 8 GB recomendado
- **Disco**: 5 GB de espacio libre
- **Conexión**: Internet estable para scraping

#### Producción
- **CPU**: 4 núcleos o más
- **RAM**: 8 GB mínimo, 16 GB recomendado
- **Disco**: 20 GB de espacio libre (más según volumen de datos)
- **Red**: Conexión de banda ancha estable
- **SSL**: Certificado SSL válido para HTTPS

---

## 🚀 Instalación Completa

### 1. Clonar el Repositorio

Primero, clona el proyecto desde GitHub a tu máquina local:

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/NoticiaScraping.git

# Navegar al directorio del proyecto
cd NoticiaScraping
```

### 2. Instalar PostgreSQL

#### macOS (con Homebrew)
```bash
# Instalar PostgreSQL
brew install postgresql@16

# Iniciar el servicio
brew services start postgresql@16

# Verificar que está corriendo
pg_isready
```

#### Ubuntu/Debian
```bash
# Actualizar repositorios
sudo apt update

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Iniciar el servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar estado
sudo systemctl status postgresql
```

#### Windows
- Descargar el instalador desde: https://www.postgresql.org/download/windows/
- Ejecutar el instalador y seguir las instrucciones
- Recordar la contraseña del usuario `postgres`

### 3. Configurar la Base de Datos

```bash
# Conectar a PostgreSQL como superusuario
psql -U postgres

# Dentro del prompt de psql, ejecutar:
CREATE DATABASE noticias_db;

# Verificar que se creó
\l

# Salir
\q
```

### 4. Configurar el Backend

#### Crear Entorno Virtual

```bash
# Navegar al directorio del backend
cd scraping-noticias-backend

# Crear entorno virtual con Python 3.11
python3.11 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate

# En Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

# En Windows (CMD):
# venv\Scripts\activate.bat
```

#### Instalar Dependencias Python

```bash
# Actualizar pip a la última versión
pip install --upgrade pip

# Instalar todas las dependencias del proyecto
pip install -r requirements.txt
```

Esto instalará las 40+ bibliotecas necesarias incluyendo:
- Flask y extensiones (JWT, CORS, Swagger)
- psycopg2-binary para PostgreSQL
- BeautifulSoup4 y lxml para scraping
- APScheduler para tareas programadas
- Stripe, PayPal SDK para pagos
- Google GenerativeAI para chatbot
- Y todas sus dependencias

#### Configurar Credenciales de Base de Datos

Editar el archivo `database.py` (líneas 10-16):

```python
self.config = {
    'host': 'localhost',
    'user': 'postgres',           # Tu usuario de PostgreSQL
    'password': 'tu_password',     # ⚠️ CAMBIAR ESTO
    'database': 'noticias_db',
    'port': 5432
}
```

**IMPORTANTE**: Si tu usuario de PostgreSQL no tiene contraseña, deja el campo vacío: `'password': ''`

#### Inicializar las Tablas de Base de Datos

```bash
# Las tablas se crean automáticamente al iniciar el backend
# Pero puedes verificar con:
python inicializar_bd.py
```

#### Crear Usuario Administrador

```bash
# Ejecutar script de creación de admin
python crear_admin.py
```

Este script creará un usuario administrador con:
- **Usuario**: admin
- **Email**: admin@noticias.com
- **Contraseña**: admin123
- **Rol**: admin

⚠️ **IMPORTANTE**: Cambiar la contraseña después del primer login por seguridad.

### 5. Configurar el Frontend

#### Instalar Node.js y npm

Si no los tienes instalados:

**macOS (con Homebrew)**:
```bash
brew install node@20
```

**Ubuntu/Debian**:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows**:
- Descargar desde: https://nodejs.org/
- Instalar la versión LTS

#### Instalar Dependencias del Frontend

```bash
# Desde la raíz del proyecto
cd news-scraper-frontend

# Instalar todas las dependencias
npm install
```

Esto instalará aproximadamente 280 paquetes incluyendo:
- React 18 y React-DOM
- React Router DOM para navegación
- Axios para peticiones HTTP
- TailwindCSS para estilos
- Vite para build y desarrollo
- Lucide React para iconos
- Recharts para gráficos
- React Hot Toast para notificaciones
- date-fns para manejo de fechas
- Y todas sus dependencias

#### Verificar Configuración de la API

El archivo `src/services/api.js` debe tener la URL correcta del backend:

```javascript
const API_URL = 'http://localhost:8001/api/v1';
```

Si el backend está en otro host o puerto, modificar esta línea.

### 6. Variables de Entorno (Opcional)

#### Backend (.env)

Crear archivo `.env` en `scraping-noticias-backend/`:

```env
# Base de Datos
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=tu_password
DB_NAME=noticias_db
DB_PORT=5432

# JWT
JWT_SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion

# Google Gemini AI (Chatbot)
GEMINI_API_KEY=tu-api-key-de-google-gemini

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# PayPal
PAYPAL_CLIENT_ID=tu-client-id
PAYPAL_CLIENT_SECRET=tu-client-secret
PAYPAL_MODE=sandbox  # o 'live' en producción

# Flask
FLASK_ENV=development  # o 'production'
FLASK_DEBUG=1          # 0 en producción
```

Para usar las variables de entorno, instalar:
```bash
pip install python-dotenv
```

Y agregar al inicio de `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Frontend (.env)

Crear archivo `.env` en `news-scraper-frontend/`:

```env
VITE_API_URL=http://localhost:8001/api/v1
VITE_APP_NAME=NoticiaScraping
```

---

## ▶️ Ejecución del Proyecto

### Iniciar el Backend

```bash
# Abrir una terminal
cd scraping-noticias-backend

# Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# o
# venv\Scripts\activate    # Windows

# Ejecutar el servidor
python app.py

# El backend estará disponible en:
# http://localhost:8001
# Documentación en: http://localhost:8001/docs
```

### Iniciar el Frontend

```bash
# Abrir una NUEVA terminal (mantener backend corriendo)
cd news-scraper-frontend

# Ejecutar servidor de desarrollo
npm run dev

# El frontend estará disponible en:
# http://localhost:5173
```

### Verificar que Todo Funciona

1. **Backend**: Abrir http://localhost:8001 - Deberías ver un JSON con info de la API
2. **Swagger**: Abrir http://localhost:8001/docs - Documentación interactiva
3. **Frontend**: Abrir http://localhost:5173 - Interfaz de usuario
4. **Base de Datos**: Ejecutar `psql -U postgres -d noticias_db -c "\dt"` - Ver las 7 tablas

---

## 🎯 Configuración Detallada

### Configuración de PostgreSQL

#### Permitir Conexiones Locales

Editar `pg_hba.conf` (ubicación varía según sistema):

```conf
# Agregar o modificar esta línea:
host    all             all             127.0.0.1/32            md5
```

#### Crear Usuario Específico para la App

```sql
-- Conectar como postgres
psql -U postgres

-- Crear usuario
CREATE USER noticiasapp WITH PASSWORD 'password_seguro';

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE noticias_db TO noticiasapp;

-- Conectar a la base de datos
\c noticias_db

-- Dar permisos en el schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO noticiasapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO noticiasapp;
```

Luego actualizar `database.py`:
```python
'user': 'noticiasapp',
'password': 'password_seguro',
```

### Configuración de Google Gemini AI (Chatbot)

El proyecto incluye un chatbot inteligente que usa Google Gemini AI. Para habilitarlo:

1. **Obtener API Key**:
   - Ir a: https://makersuite.google.com/app/apikey
   - Crear un proyecto de Google Cloud si no tienes
   - Generar una API key

2. **Configuración**:

   Opción A - Variable de entorno (recomendado):
   ```bash
   export GEMINI_API_KEY="tu-api-key-aqui"
   ```

   Opción B - Archivo .env:
   ```env
   GEMINI_API_KEY=tu-api-key-aqui
   ```

3. **Reiniciar Backend**:
   ```bash
   python app.py
   ```

4. **Probar Chatbot**:
   - El chatbot estará disponible en `/api/v1/chatbot/preguntar`
   - Puede responder preguntas sobre las noticias almacenadas

### Configuración de Pagos

#### Yape

Para pagos con Yape (Perú):
- No requiere configuración de API
- Se genera un código QR con el monto
- El usuario toma screenshot y lo envía
- El admin verifica manualmente el pago

#### Stripe

1. **Crear cuenta**: https://stripe.com/
2. **Obtener claves de prueba**:
   - Ir a Developers → API keys
   - Copiar Secret key y Publishable key
3. **Configurar**:
   ```env
   STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxx
   STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxx
   ```

#### PayPal

1. **Crear cuenta developer**: https://developer.paypal.com/
2. **Crear aplicación**:
   - Dashboard → My Apps & Credentials
   - Create App
   - Copiar Client ID y Secret
3. **Configurar**:
   ```env
   PAYPAL_CLIENT_ID=xxxxxxxxxxxxx
   PAYPAL_CLIENT_SECRET=xxxxxxxxxxxxx
   PAYPAL_MODE=sandbox  # o 'live' en producción
   ```

### Configuración del Scheduler

El sistema incluye un scheduler para ejecutar scraping automático:

```python
# En scheduler.py, puedes configurar:

# Intervalo por defecto
DEFAULT_INTERVAL = 3600  # segundos (1 hora)

# Días de la semana
DIAS_SEMANA = {
    'lun': 0, 'mar': 1, 'mie': 2, 
    'jue': 3, 'vie': 4, 'sab': 5, 'dom': 6
}
```

Endpoints para gestión:
- `POST /api/v1/scheduler/tareas` - Crear tarea
- `GET /api/v1/scheduler/tareas` - Listar tareas
- `POST /api/v1/scheduler/tareas/{nombre}/pausar` - Pausar
- `POST /api/v1/scheduler/tareas/{nombre}/reanudar` - Reanudar

---

## 🔧 Funcionalidades Principales

### 1. Sistema de Autenticación

#### Registro de Usuarios
- Validación de email único
- Validación de nombre de usuario único
- Hash seguro de contraseñas con bcrypt
- Asignación automática de rol 'usuario'
- Generación de JWT al registrarse

#### Login
- Validación de credenciales
- Generación de JWT con claims personalizados
- Token válido por 24 horas (configurable)
- Incluye rol del usuario en el token

#### Perfil de Usuario
- Consulta de datos del usuario autenticado
- Actualización de información personal
- Cambio de contraseña
- Ver historial de suscripciones y pagos

### 2. Sistema de Roles

#### Usuario Normal ('usuario')
- Puede agregar fuentes (limitado por plan)
- Puede ejecutar scraping (limitado por plan)
- Ve solo sus propias noticias
- Puede exportar sus noticias
- Puede buscar en sus noticias
- Acceso a estadísticas personales

#### Administrador ('admin')
- Todos los permisos de usuario normal
- Ve todas las noticias de todos los usuarios
- Gestiona usuarios (listar, activar, desactivar)
- Gestiona planes y precios
- Aprueba o rechaza pagos
- Acceso a estadísticas globales
- Panel de administración completo

### 3. Web Scraping

#### Características
- Scraping inteligente con fallbacks automáticos
- Extracción de título, resumen, imagen, categoría
- Detección automática de fecha de publicación
- Scraping profundo (deep scraping) cuando falta información
- Manejo de errores robusto
- Límites de rate para no sobrecargar servidores

#### Fuentes Configurables
- Agregar fuentes con solo nombre y URL
- Selectores CSS automáticos con fallbacks
- Posibilidad de personalizar selectores
- Activar/desactivar fuentes
- Editar configuración de fuentes existentes

#### Proceso de Scraping
1. Usuario solicita scraping desde dashboard o API
2. Sistema verifica límites del plan del usuario
3. Se extraen noticias de las fuentes configuradas
4. Se filtran noticias duplicadas (por URL y user_id)
5. Se guardan en base de datos con user_id
6. Se actualiza contador de scraping diario
7. Se retorna resultado al usuario

### 4. Gestión de Noticias

#### Listado con Paginación
- Paginación eficiente con offset y límite
- Filtros por fuente, categoría, país
- Ordenamiento por fecha (más recientes primero)
- Separación por usuario (multi-tenant)
- Carga rápida con índices de base de datos

#### Búsqueda Avanzada
- Búsqueda por palabras clave en título y resumen
- Filtros combinados (fuente + categoría + país)
- Búsqueda full-text en PostgreSQL
- Resultados ordenados por relevancia
- Paginación de resultados de búsqueda

#### Exportación de Datos
- Formatos: CSV, JSON, TXT
- Exportación completa o filtrada
- Incluye todos los campos de noticias
- Descarga directa desde navegador
- Respeta separación por usuario

### 5. Planes y Suscripciones

#### Planes Disponibles (Configurables)
- **Gratuito**: Límites básicos (3 fuentes, 30 scraping/día)
- **Básico**: Límites medios (10 fuentes, 100 scraping/día)
- **Premium**: Límites altos (50 fuentes, 500 scraping/día)
- **Empresarial**: Ilimitado (-1 para fuentes y scraping)

#### Límites Aplicados
- **Límite de Fuentes**: Número máximo de fuentes que puede crear
- **Límite de Scraping Diario**: Cantidad de noticias que puede scrapear por día
- Verificación automática antes de agregar fuente
- Verificación automática antes de ejecutar scraping
- Reset automático del contador diario a medianoche

#### Cambio de Plan
- Usuario puede ver planes disponibles
- Proceso de pago para cambiar de plan
- Activación inmediata o programada
- Desactivación de plan anterior automática
- Historial de cambios de plan

### 6. Sistema de Pagos

#### Métodos Soportados
1. **Yape (Perú)**:
   - Se genera QR con monto
   - Usuario realiza pago y envía comprobante
   - Admin verifica y aprueba/rechaza

2. **PayPal**:
   - Integración completa con SDK
   - Redirect a PayPal para pago
   - Verificación automática de pago
   - Activación automática de suscripción

3. **Stripe**:
   - Pago con tarjeta de crédito/débito
   - Procesamiento seguro PCI-compliant
   - Webhooks para confirmación
   - Activación automática tras pago exitoso

#### Flujo de Pago
1. Usuario selecciona plan
2. Crea intención de pago (registro en BD)
3. Completa pago según método elegido
4. Sistema registra referencia de pago
5. Admin (Yape) o webhook (Stripe/PayPal) confirma
6. Sistema activa suscripción
7. Usuario obtiene nuevos límites

### 7. Scheduler de Tareas

#### Tipos de Tareas
- **Scraping Periódico**: Ejecutar scraping cada X tiempo
- **Scraping en Horario Específico**: Ejecutar a una hora exacta
- **Scraping Semanal**: Ejecutar ciertos días de la semana

#### Gestión de Tareas
- Crear tareas programadas
- Listar tareas activas y pausadas
- Pausar/reanudar tareas
- Eliminar tareas
- Ver próxima ejecución
- Historial de ejecuciones

#### Configuración
```json
{
  "nombre": "scraping_diario",
  "tipo": "interval",
  "intervalo": 86400,  // segundos (24 horas)
  "fuente_id": null,   // null = todas las fuentes
  "activo": true
}
```

### 8. Estadísticas

#### Estadísticas del Usuario
- Total de noticias scrapeadas
- Noticias por fuente
- Noticias por categoría
- Noticias por país
- Tendencias por fecha
- Top fuentes más productivas

#### Estadísticas de Admin
- Total de usuarios registrados
- Usuarios por plan
- Ingresos mensuales
- Pagos pendientes de verificación
- Noticias totales en sistema
- Actividad de scraping global

### 9. Panel de Administración

#### Gestión de Usuarios
- Listar todos los usuarios
- Ver detalles de cada usuario
- Activar/desactivar usuarios
- Cambiar rol de usuario
- Ver suscripciones activas
- Ver historial de pagos

#### Gestión de Pagos
- Ver pagos pendientes de verificación
- Aprobar pagos (activa suscripción)
- Rechazar pagos
- Ver historial completo de pagos
- Filtrar por método de pago

#### Gestión de Planes
- Crear nuevos planes
- Editar límites de planes existentes
- Activar/desactivar planes
- Ver usuarios por plan

### 10. Chatbot con IA

#### Características
- Powered by Google Gemini AI
- Responde preguntas sobre las noticias
- Búsqueda semántica en noticias guardadas
- Conversación natural en español
- Incluye contexto de las noticias

#### Uso
```javascript
POST /api/v1/chatbot/preguntar
{
  "pregunta": "¿Cuáles son las últimas noticias de tecnología?"
}
```

### 11. Modo Oscuro/Claro

#### Características
- Toggle entre dark mode y light mode
- Persistencia en localStorage
- Transiciones suaves
- Todos los componentes soportan ambos temas
- Colores optimizados para legibilidad
- Detección automática de preferencia del sistema

#### Paleta de Colores
**Light Mode**:
- Background: blanco y grises claros
- Text: negro y grises oscuros
- Primarios: azules y verdes

**Dark Mode**:
- Background: grises oscuros y negro
- Text: blanco y grises claros
- Primarios: azules y verdes más brillantes

---

(Continúa en la siguiente parte...)
