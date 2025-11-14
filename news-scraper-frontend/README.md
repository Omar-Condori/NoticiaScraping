# 📰 NewsScraper - Frontend

Frontend moderno desarrollado en React para el sistema de scraping de noticias.

## 🚀 Características

- **Dashboard completo** con métricas y gráficos en tiempo real
- **Gestión de noticias** con búsqueda, filtrado y exportación
- **CRUD de fuentes** con configuración de selectores CSS
- **Scheduler** para automatización de scraping
- **Estadísticas avanzadas** con múltiples visualizaciones
- **Búsqueda avanzada** con filtros personalizados
- **Tema oscuro** con glassmorphism y animaciones fluidas
- **Diseño responsivo** optimizado para móvil y desktop

## 🛠️ Stack Tecnológico

- **React 18** - Framework principal
- **Vite** - Build tool y dev server
- **React Router v6** - Navegación
- **Tailwind CSS** - Estilos y utilidades
- **Axios** - Cliente HTTP
- **Recharts** - Gráficos y visualizaciones
- **React Hot Toast** - Notificaciones
- **Lucide React** - Iconos
- **date-fns** - Manejo de fechas

## 📦 Instalación

### Prerrequisitos

- Node.js 18+ instalado
- Backend Flask corriendo en `http://localhost:8001`

### Pasos de instalación

1. **Clonar o crear el proyecto:**

```bash
# Si empiezas desde cero
npm create vite@latest news-scraper-frontend -- --template react
cd news-scraper-frontend
```

2. **Instalar dependencias:**

```bash
npm install react react-dom react-router-dom axios recharts date-fns react-hot-toast lucide-react
npm install -D tailwindcss postcss autoprefixer
```

3. **Configurar Tailwind CSS:**

```bash
npx tailwindcss init -p
```

4. **Copiar todos los archivos del proyecto** en sus respectivas ubicaciones:

```
news-scraper-frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   └── Layout.jsx
│   │   └── ui/
│   │       ├── Badge.jsx
│   │       ├── Button.jsx
│   │       ├── Card.jsx
│   │       ├── Input.jsx
│   │       ├── Modal.jsx
│   │       └── Skeleton.jsx
│   ├── context/
│   │   └── AppContext.jsx
│   ├── hooks/
│   │   ├── useNoticias.js
│   │   ├── useScraping.js
│   │   └── useScheduler.js
│   ├── pages/
│   │   ├── Busqueda.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Estadisticas.jsx
│   │   ├── Fuentes.jsx
│   │   ├── Noticias.jsx
│   │   └── Scheduler.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── vite.config.js
```

5. **Iniciar el servidor de desarrollo:**

```bash
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
src/
├── components/          # Componentes reutilizables
│   ├── Layout/         # Layout principal con sidebar
│   └── ui/             # Componentes de UI (Button, Card, Modal, etc.)
├── context/            # Context API para estado global
├── hooks/              # Custom hooks para lógica reutilizable
├── pages/              # Páginas de la aplicación
├── services/           # Servicios de API y cliente HTTP
├── App.jsx             # Componente raíz con router
├── main.jsx            # Punto de entrada
└── index.css           # Estilos globales
```

## 🎨 Componentes Principales

### Layout
- Sidebar responsivo con navegación
- Top bar con perfil de usuario
- Diseño adaptable a móvil y desktop

### Páginas

1. **Dashboard** (`/`)
   - Métricas generales del sistema
   - Gráficos de tendencias semanales
   - Top de fuentes más activas
   - Última actualización

2. **Noticias** (`/noticias`)
   - Lista de noticias scrapeadas
   - Filtros por fuente y cantidad
   - Ejecución manual de scraping
   - Exportación en CSV, JSON, TXT

3. **Fuentes** (`/fuentes`)
   - CRUD completo de fuentes
   - Configuración de selectores CSS
   - Activar/desactivar fuentes
   - Vista de tarjetas con detalles

4. **Scheduler** (`/scheduler`)
   - Crear tareas programadas
   - Pausar/reanudar tareas
   - Eliminar tareas
   - Vista del próximo scraping

5. **Estadísticas** (`/estadisticas`)
   - Gráficos de líneas (tendencias)
   - Gráficos de barras (ranking)
   - Gráfico de pastel (distribución)
   - Métricas detalladas por fuente

6. **Búsqueda** (`/busqueda`)
   - Búsqueda simple por texto
   - Búsqueda por palabras clave
   - Filtros por fuente y fecha
   - Resultados paginados

## 🔧 Configuración

### Variables de entorno

El proyecto usa proxy de Vite para conectarse al backend. Si necesitas cambiar la URL del backend, edita `vite.config.js`:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001', // Cambia esto si es necesario
        changeOrigin: true
      }
    }
  }
})
```

### Personalización de colores

Los colores del tema se pueden personalizar en `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      dark: {
        bg: '#0a0a0f',      // Fondo principal
        card: '#121218',    // Fondo de tarjetas
        hover: '#1a1a24',   // Estado hover
        border: '#2a2a35'   // Bordes
      },
      accent: {
        primary: '#6366f1',   // Color primario
        secondary: '#8b5cf6', // Color secundario
        success: '#10b981',   // Verde
        warning: '#f59e0b',   // Amarillo
        danger: '#ef4444'     // Rojo
      }
    }
  }
}
```

## 📱 Responsive Design

El frontend está completamente optimizado para dispositivos móviles:
- Sidebar colapsable en móvil
- Grids responsivos que se adaptan al tamaño de pantalla
- Tablas scrollables horizontalmente
- Botones y formularios optimizados para touch

## 🔐 Manejo de Errores

Todas las llamadas a la API incluyen manejo de errores:
- Interceptores de Axios para errores globales
- Toast notifications para feedback al usuario
- Estados de loading y error en cada componente
- Validación de formularios

## 🚀 Producción

Para generar el build de producción:

```bash
npm run build
```

Los archivos estáticos se generarán en la carpeta `dist/` listos para ser servidos por cualquier servidor web.

Preview del build:

```bash
npm run preview
```

## 📚 Recursos Adicionales

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts](https://recharts.org)
- [React Router](https://reactrouter.com)

## 🐛 Solución de Problemas

### El backend no responde
- Verifica que Flask esté corriendo en `http://localhost:8001`
- Comprueba que CORS esté habilitado en el backend
- Revisa la consola del navegador para errores de red

### Los gráficos no se muestran
- Verifica que haya datos en la base de datos
- Comprueba la respuesta de la API en Network tab
- Asegúrate de que las fechas estén en formato correcto

### Errores de compilación
- Borra `node_modules` y reinstala: `rm -rf node_modules && npm install`
- Limpia la caché de Vite: `rm -rf .vite`
- Verifica que todas las dependencias estén instaladas

## 👨‍💻 Desarrollo

Para contribuir al proyecto:

1. Sigue la estructura de carpetas existente
2. Usa los hooks personalizados para lógica de negocio
3. Mantén los componentes pequeños y reutilizables
4. Documenta funciones complejas con comentarios

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y comerciales.