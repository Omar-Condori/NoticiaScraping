# 📋 Implementación Completa: Roles, Multitenancy y Dark Mode

## ✅ Funcionalidades Implementadas

### 1. **Sistema de Roles de Usuario**

#### Backend
- ✅ Campo `rol` agregado a tabla `usuarios` (default: 'usuario')
- ✅ Registro automático asigna rol 'usuario' por defecto
- ✅ JWT incluye rol en `additional_claims`
- ✅ Middleware `admin_required` creado en `middleware.py`
- ✅ Endpoint `/api/v1/auth/perfil` retorna rol del usuario

#### Frontend
- ✅ `AuthContext` y `AppContext` incluyen rol del usuario
- ✅ Badge "Admin" visible en Layout para usuarios admin
- ✅ Rol visible en sidebar y top bar

#### Archivos Modificados:
- `scraping-noticias-backend/database.py`: Tabla usuarios con rol
- `scraping-noticias-backend/auth.py`: Retorna rol en autenticación
- `scraping-noticias-backend/app.py`: JWT con rol, endpoints actualizados
- `scraping-noticias-backend/middleware.py`: **NUEVO** - Decorador `admin_required`
- `news-scraper-frontend/src/context/AppContext.jsx`: Incluye rol
- `news-scraper-frontend/src/components/Layout/Layout.jsx`: Muestra rol y badge admin

---

### 2. **Separación de Noticias por Usuario (Multitenancy)**

#### Backend
- ✅ Campo `user_id` agregado a tabla `noticias`
- ✅ Constraint único: `UNIQUE(url, user_id)` (misma URL puede existir para diferentes usuarios)
- ✅ `guardar_noticia()` ahora requiere `user_id`
- ✅ `obtener_noticias()` filtra por `user_id` (admin ve todas)
- ✅ `contar_noticias()` filtra por `user_id` (admin cuenta todas)
- ✅ `obtener_categorias()` filtra por `user_id` (admin ve todas)
- ✅ `limpiar_noticias()` elimina solo del usuario (admin elimina todas)
- ✅ Scraping guarda noticias con `user_id` del usuario autenticado

#### Frontend
- ✅ Todas las peticiones API incluyen token JWT automáticamente
- ✅ El backend filtra automáticamente por usuario
- ✅ Admin ve todas las noticias automáticamente

#### Archivos Modificados:
- `scraping-noticias-backend/database.py`: 
  - Tabla noticias con `user_id`
  - `guardar_noticia()` con `user_id`
  - `obtener_noticias()` con filtro por usuario
  - `contar_noticias()` con filtro por usuario
  - `obtener_categorias()` con filtro por usuario
  - `limpiar_noticias()` con filtro por usuario
- `scraping-noticias-backend/scraper.py`:
  - `scrape_fuente()` acepta `user_id`
  - `scrape_todas_fuentes()` acepta `user_id`
  - `obtener_noticias_guardadas()` con filtros de usuario
- `scraping-noticias-backend/app.py`:
  - Endpoint scraping pasa `user_id`
  - Endpoint noticias filtra por usuario
  - Endpoint exportar filtra por usuario
- `news-scraper-frontend/src/services/api.js`: Todas las peticiones incluyen JWT

---

### 3. **Modo Día/Noche (Dark Mode)**

#### Frontend
- ✅ `ThemeContext` creado con persistencia en localStorage
- ✅ Botón toggle de tema en sidebar y top bar
- ✅ Iconos Sun/Moon según tema
- ✅ Tailwind configurado con `darkMode: 'class'`
- ✅ Colores light/dark definidos en `tailwind.config.js`
- ✅ Estilos aplicados globalmente con clases `dark:`

#### Archivos Creados/Modificados:
- `news-scraper-frontend/src/context/ThemeContext.jsx`: **NUEVO** - Contexto de tema
- `news-scraper-frontend/src/App.jsx`: Incluye `ThemeProvider`
- `news-scraper-frontend/tailwind.config.js`: Dark mode y colores light
- `news-scraper-frontend/src/index.css`: Estilos base con soporte dark
- `news-scraper-frontend/src/components/Layout/Layout.jsx`: Botón toggle y estilos

---

## 🔧 Migraciones de Base de Datos

Las migraciones se ejecutan automáticamente al iniciar el backend:

1. **Columna `rol` en `usuarios`**:
   ```sql
   ALTER TABLE usuarios 
   ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'usuario';
   ```

2. **Columna `user_id` en `noticias`**:
   ```sql
   ALTER TABLE noticias 
   ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE;
   ```

3. **Índice único compuesto**:
   ```sql
   CREATE UNIQUE INDEX IF NOT EXISTS idx_noticias_url_user 
   ON noticias(url, user_id);
   ```

4. **Índice para rendimiento**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_noticias_user_id 
   ON noticias(user_id);
   ```

---

## 🚀 Cómo Probar

### 1. Crear Usuario Administrador

```bash
cd scraping-noticias-backend
python crear_admin.py
```

Esto creará un usuario:
- **Usuario**: `admin`
- **Email**: `admin@noticias.com`
- **Contraseña**: `admin123`
- **Rol**: `admin`

⚠️ **IMPORTANTE**: Cambia la contraseña después del primer login.

### 2. Probar Roles y Aislamiento

#### Paso 1: Registrar Usuario Normal
1. Abre `http://localhost:5173/register`
2. Crea un usuario (ej: `usuario1`, `usuario1@test.com`, `pass123`)
3. Verifica que el rol sea "usuario" (visible en sidebar)

#### Paso 2: Hacer Scraping como Usuario Normal
1. Ve a Dashboard
2. Haz clic en "Scrapear Ahora"
3. Espera a que termine
4. Ve a "Noticias" - deberías ver solo las noticias que acabas de scrapear

#### Paso 3: Registrar Segundo Usuario
1. Cierra sesión
2. Registra otro usuario (ej: `usuario2`, `usuario2@test.com`, `pass123`)
3. Haz scraping
4. Verifica que veas solo las noticias de `usuario2`

#### Paso 4: Login como Admin
1. Cierra sesión
2. Login con `admin` / `admin123`
3. Verifica que veas badge "Admin" en la interfaz
4. Ve a "Noticias" - deberías ver **TODAS** las noticias de todos los usuarios

### 3. Probar Dark Mode

1. Haz clic en el botón de sol/luna en el sidebar o top bar
2. Verifica que los colores cambien:
   - **Dark**: Fondos oscuros, texto claro
   - **Light**: Fondos claros, texto oscuro
3. Recarga la página - el tema debe persistir
4. Verifica en `localStorage` que `theme` esté guardado

---

## 📝 Cambios Detallados por Archivo

### Backend

#### `database.py`
- ✅ Tabla `usuarios`: Campo `rol` con default 'usuario'
- ✅ Tabla `noticias`: Campo `user_id` con foreign key
- ✅ `crear_usuario()`: Asigna rol 'usuario' automáticamente
- ✅ `guardar_noticia()`: Requiere `user_id` como parámetro
- ✅ `obtener_noticias()`: Filtra por `user_id` (admin ve todas)
- ✅ `contar_noticias()`: Filtra por `user_id`
- ✅ `obtener_categorias()`: Filtra por `user_id`
- ✅ `limpiar_noticias()`: Elimina solo del usuario (admin elimina todas)

#### `auth.py`
- ✅ `autenticar_usuario()`: Retorna rol en respuesta
- ✅ `registrar_usuario()`: Usuario recibe rol 'usuario' automáticamente

#### `app.py`
- ✅ Login: JWT incluye `additional_claims={'rol': ...}`
- ✅ Registro: JWT incluye rol
- ✅ `/api/v1/auth/perfil`: Retorna rol del usuario
- ✅ `/api/v1/scraping/ejecutar`: Pasa `user_id` al scraper
- ✅ `/api/v1/noticias`: Filtra por usuario (admin ve todas)
- ✅ `/api/v1/noticias/contar`: Filtra por usuario
- ✅ `/api/v1/noticias/exportar`: Filtra por usuario
- ✅ `/api/v1/categorias`: Filtra por usuario
- ✅ `/api/v1/noticias` (DELETE): Elimina solo del usuario

#### `scraper.py`
- ✅ `scrape_fuente()`: Acepta `user_id`, lo guarda en `_current_user_id`
- ✅ `scrape_todas_fuentes()`: Acepta `user_id`
- ✅ `guardar_noticia()`: Usa `_current_user_id` para guardar
- ✅ `obtener_noticias_guardadas()`: Pasa `user_id` y `es_admin` a BD
- ✅ `contar_noticias()`: Pasa `user_id` y `es_admin` a BD
- ✅ `obtener_categorias()`: Pasa `user_id` y `es_admin` a BD
- ✅ `limpiar_noticias()`: Pasa `user_id` y `es_admin` a BD

#### `middleware.py` (NUEVO)
- ✅ Decorador `@admin_required` para proteger endpoints
- ✅ Función `get_user_info()` para obtener info del usuario

#### `crear_admin.py` (NUEVO)
- ✅ Script para crear primer usuario administrador
- ✅ Verifica si ya existe admin
- ✅ Permite actualizar usuario existente a admin

### Frontend

#### `context/ThemeContext.jsx` (NUEVO)
- ✅ Contexto para manejar tema (dark/light)
- ✅ Persistencia en localStorage
- ✅ Aplica clase `dark` al `documentElement`

#### `context/AppContext.jsx`
- ✅ Ya incluye `user` con rol (sin cambios necesarios)

#### `App.jsx`
- ✅ Envuelto con `ThemeProvider`

#### `components/Layout/Layout.jsx`
- ✅ Importa `useTheme`
- ✅ Muestra badge "Admin" si `user.rol === 'admin'`
- ✅ Muestra rol del usuario
- ✅ Botón toggle de tema en sidebar y top bar
- ✅ Estilos con soporte dark/light

#### `services/api.js`
- ✅ Todas las peticiones incluyen `getAuthHeaders()` con JWT
- ✅ `noticiasAPI.obtener()`: Incluye JWT
- ✅ `fuentesAPI.listar()`: Incluye JWT
- ✅ `categoriasAPI.obtener()`: Incluye JWT
- ✅ `noticiasAPI.exportar()`: Incluye JWT

#### `tailwind.config.js`
- ✅ `darkMode: 'class'` habilitado
- ✅ Colores `light` agregados (bg, card, hover, border)

#### `index.css`
- ✅ Estilos base con soporte dark/light
- ✅ Scrollbar con estilos para ambos temas

---

## 🔐 Seguridad

### JWT con Rol
Los tokens JWT ahora incluyen el rol en `additional_claims`:
```python
access_token = create_access_token(
    identity=usuario_id,
    additional_claims={'rol': 'usuario'}  # o 'admin'
)
```

### Filtrado Automático
- Todos los endpoints que retornan noticias filtran automáticamente por `user_id`
- Los admins ven todas las noticias (`es_admin = True` omite el filtro)
- El frontend no necesita hacer nada especial - el backend maneja todo

---

## 🧪 Casos de Prueba

### Caso 1: Usuario Normal
1. ✅ Registro → Rol 'usuario'
2. ✅ Scraping → Noticias guardadas con su `user_id`
3. ✅ Ver noticias → Solo ve sus propias noticias
4. ✅ Exportar → Solo exporta sus noticias
5. ✅ Contar → Solo cuenta sus noticias
6. ✅ Categorías → Solo ve categorías de sus noticias

### Caso 2: Usuario Admin
1. ✅ Login → Badge "Admin" visible
2. ✅ Ver noticias → Ve todas las noticias de todos los usuarios
3. ✅ Exportar → Exporta todas las noticias
4. ✅ Contar → Cuenta todas las noticias
5. ✅ Categorías → Ve todas las categorías

### Caso 3: Aislamiento
1. ✅ Usuario A scrapea → Noticias con `user_id = A`
2. ✅ Usuario B scrapea → Noticias con `user_id = B`
3. ✅ Usuario A no ve noticias de B
4. ✅ Usuario B no ve noticias de A
5. ✅ Admin ve noticias de A y B

### Caso 4: Dark Mode
1. ✅ Cambio de tema → Persiste en localStorage
2. ✅ Recarga página → Tema se mantiene
3. ✅ Estilos aplicados → Todos los componentes respetan el tema

---

## ⚠️ Notas Importantes

1. **Primer Admin**: Debes ejecutar `crear_admin.py` para crear el primer administrador
2. **Migraciones**: Se ejecutan automáticamente al iniciar el backend
3. **Compatibilidad**: Las noticias existentes (sin `user_id`) no se mostrarán hasta que se re-scrapeen
4. **JWT**: Todos los endpoints que requieren usuario ahora necesitan JWT (opcional en algunos casos)
5. **Frontend**: El token se envía automáticamente en todas las peticiones

---

## 🐛 Solución de Problemas

### Error: "No se muestran noticias antiguas"
- Las noticias creadas antes de esta implementación no tienen `user_id`
- Solución: Re-scrapear las noticias con un usuario autenticado

### Error: "Admin no ve todas las noticias"
- Verifica que el token JWT incluya `rol: 'admin'`
- Verifica que `es_admin = True` se esté pasando correctamente

### Error: "Dark mode no funciona"
- Verifica que `tailwind.config.js` tenga `darkMode: 'class'`
- Verifica que `ThemeProvider` esté en `App.jsx`
- Verifica que la clase `dark` se esté aplicando al `documentElement`

### Error: "Usuario ve noticias de otros"
- Verifica que el JWT se esté enviando correctamente
- Verifica que `user_id` se esté extrayendo del token
- Revisa los logs del backend para ver qué `user_id` se está usando

---

## 📊 Resumen de Cambios

- **Archivos Backend Modificados**: 5
- **Archivos Backend Nuevos**: 2 (`middleware.py`, `crear_admin.py`)
- **Archivos Frontend Modificados**: 6
- **Archivos Frontend Nuevos**: 1 (`ThemeContext.jsx`)
- **Migraciones SQL**: 4 (automáticas)
- **Endpoints Modificados**: 8
- **Nuevos Decoradores**: 1 (`@admin_required`)

---

**Implementación completada** ✅

