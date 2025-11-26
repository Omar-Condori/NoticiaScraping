# 📘 MANUAL DE USUARIO - Sistema de Scraping de Noticias

Bienvenido al manual de usuario de **NoticiaScraping**. Este documento le guiará paso a paso en el uso de todas las funcionalidades del sistema, desde el registro hasta la exportación de noticias y gestión de planes.

---

## 📑 Índice

1. [Introducción](#1-introducción)
2. [Primeros Pasos](#2-primeros-pasos)
   - [Acceso al Sistema](#acceso-al-sistema)
   - [Registro de Cuenta](#registro-de-cuenta)
   - [Inicio de Sesión](#inicio-de-sesión)
3. [Panel Principal (Dashboard)](#3-panel-principal-dashboard)
4. [Gestión de Fuentes de Noticias](#4-gestión-de-fuentes-de-noticias)
   - [Agregar Nueva Fuente](#agregar-nueva-fuente)
   - [Editar y Eliminar Fuentes](#editar-y-eliminar-fuentes)
5. [Obtención de Noticias (Scraping)](#5-obtención-de-noticias-scraping)
   - [Scraping Manual](#scraping-manual)
   - [Scraping Automático (Programado)](#scraping-automático-programado)
6. [Visualización y Búsqueda](#6-visualización-y-búsqueda)
   - [Filtrado de Noticias](#filtrado-de-noticias)
   - [Búsqueda Avanzada](#búsqueda-avanzada)
   - [Exportar Datos](#exportar-datos)
7. [Estadísticas](#7-estadísticas)
8. [Planes y Pagos](#8-planes-y-pagos)
   - [Tipos de Planes](#tipos-de-planes)
   - [Realizar un Pago](#realizar-un-pago)
9. [Asistente IA (Chatbot)](#9-asistente-ia-chatbot)
10. [Configuración y Perfil](#10-configuración-y-perfil)
11. [Solución de Problemas](#11-solución-de-problemas)

---

## 1. Introducción

**NoticiaScraping** es una herramienta potente que le permite recolectar noticias automáticamente de sus sitios web favoritos. Con este sistema, usted puede centralizar la información de múltiples diarios y blogs en un solo lugar, buscar contenido específico y analizar tendencias.

**Características principales:**
*   Recolección automática de noticias (título, imagen, resumen, fecha).
*   Organización por categorías y fuentes.
*   Búsqueda inteligente.
*   Exportación a Excel (CSV), JSON y Texto.
*   Asistente virtual para responder preguntas sobre las noticias.

---

## 2. Primeros Pasos

### Acceso al Sistema
Para acceder al sistema, abra su navegador web (Chrome, Firefox, Edge, Safari) e ingrese la dirección proporcionada por su administrador (por ejemplo: `http://localhost:5173` si está en local).

### Registro de Cuenta
Si es la primera vez que ingresa:
1.  Haga clic en el enlace **"Registrarse"** en la pantalla de inicio de sesión.
2.  Complete el formulario con:
    *   **Nombre de usuario**: Un nombre único para identificarse.
    *   **Email**: Su correo electrónico personal o corporativo.
    *   **Contraseña**: Una clave segura.
3.  Haga clic en el botón **"Registrarse"**.
4.  El sistema iniciará sesión automáticamente y le llevará al Panel Principal.

### Inicio de Sesión
Si ya tiene cuenta:
1.  Ingrese su **Email** y **Contraseña**.
2.  Haga clic en **"Iniciar Sesión"**.

---

## 3. Panel Principal (Dashboard)

Al ingresar, verá el **Dashboard**, que es su centro de control. Aquí encontrará:
*   **Resumen Rápido**: Tarjetas con el total de noticias, fuentes activas y tareas programadas.
*   **Acciones Rápidas**: Botones para "Ejecutar Scraping" inmediatamente o "Agregar Fuente".
*   **Gráficos Recientes**: Visualización rápida de la actividad de recolección de noticias en los últimos días.

---

## 4. Gestión de Fuentes de Noticias

Esta es la parte más importante: definir de dónde quiere sacar las noticias.

### Agregar Nueva Fuente
1.  Vaya a la sección **"Fuentes"** en el menú lateral izquierdo.
2.  Haga clic en el botón **"Nueva Fuente"** (arriba a la derecha).
3.  Complete los datos básicos:
    *   **Nombre**: El nombre del diario o blog (ej. "El Comercio", "BBC Mundo").
    *   **URL**: La dirección web exacta de la sección de noticias (ej. `https://www.bbc.com/mundo`).
    *   **Categoría**: Seleccione una categoría (Política, Deportes, Tecnología, etc.) o cree una nueva.
4.  **Configuración Avanzada (Opcional)**: El sistema intenta detectar automáticamente cómo leer la página. Si sabe de tecnología, puede ajustar los "Selectores CSS", pero normalmente **no es necesario**.
5.  Haga clic en **"Guardar Fuente"**.

### Editar y Eliminar Fuentes
*   **Editar**: En la lista de fuentes, haga clic en el icono de lápiz ✏️ para cambiar el nombre o la URL.
*   **Eliminar**: Haga clic en el icono de basura 🗑️ para borrar una fuente. **Cuidado**: Esto no borra las noticias ya descargadas, solo la configuración.

---

## 5. Obtención de Noticias (Scraping)

Hay dos formas de obtener noticias: manual y automática.

### Scraping Manual
Ideal para obtener las últimas noticias en este momento.
1.  Vaya al **Dashboard** o a la sección **"Fuentes"**.
2.  Haga clic en el botón **"Ejecutar Scraping"**.
3.  Verá una barra de progreso. Espere a que termine.
4.  El sistema le avisará cuántas noticias nuevas se encontraron.

### Scraping Automático (Programado)
Ideal para que el sistema trabaje por usted mientras duerme o trabaja.
1.  Vaya a la sección **"Scheduler"** (Programador) en el menú.
2.  Haga clic en **"Nueva Tarea"**.
3.  Configure la tarea:
    *   **Nombre**: Ej. "Noticias Mañana".
    *   **Frecuencia**: Cada hora, cada día, o días específicos de la semana.
    *   **Hora**: A qué hora debe ejecutarse.
4.  Active la tarea y guarde. El sistema recolectará noticias automáticamente según su configuración.

---

## 6. Visualización y Búsqueda

Para leer y gestionar lo que ha recolectado, vaya a la sección **"Noticias"**.

### Filtrado de Noticias
Use la barra superior para filtrar:
*   **Por Fuente**: Vea solo noticias de "CNN" o "El País".
*   **Por Categoría**: Vea solo "Deportes" o "Economía".
*   **Por Fecha**: Seleccione un rango de fechas.

### Búsqueda Avanzada
1.  Escriba palabras clave en la barra de búsqueda (ej. "elecciones", "inteligencia artificial").
2.  El sistema buscará en el título y en el resumen de todas las noticias guardadas.

### Exportar Datos
¿Necesita los datos para un reporte?
1.  En la sección de Noticias, busque el botón **"Exportar"**.
2.  Seleccione el formato:
    *   **CSV**: Para abrir en Excel o Google Sheets.
    *   **JSON**: Para uso técnico o integración con otros sistemas.
    *   **TXT**: Texto simple.
3.  El archivo se descargará automáticamente a su computadora.

---

## 7. Estadísticas

Vaya a la sección **"Estadísticas"** para ver análisis visuales:
*   **Tendencias**: ¿Cuándo se publican más noticias?
*   **Top Fuentes**: ¿Qué sitio web genera más contenido?
*   **Distribución por Categoría**: Gráfico de pastel mostrando sus temas más frecuentes.

---

## 8. Planes y Pagos

El sistema funciona con un modelo de créditos o límites según su plan.

### Tipos de Planes
*   **Gratuito**: Ideal para probar. Límite de 3 fuentes y 30 noticias al día.
*   **Básico**: Para uso personal regular. 10 fuentes, 100 noticias/día.
*   **Premium**: Para usuarios intensivos. 50 fuentes, 500 noticias/día.
*   **Empresarial**: Sin límites.

### Realizar un Pago
Si necesita más capacidad:
1.  Vaya a **"Planes"** o **"Suscripción"**.
2.  Seleccione el plan deseado.
3.  Elija el método de pago:
    *   **Yape (Perú)**: Escanee el código QR mostrado, realice el pago y suba la captura de pantalla. Un administrador aprobará su plan en breve.
    *   **PayPal / Stripe**: Pago inmediato con tarjeta o cuenta PayPal. La activación es automática.

---

## 9. Asistente IA (Chatbot)

El sistema incluye una inteligencia artificial para ayudarle.
1.  Busque el icono de chat (usualmente en la esquina inferior derecha).
2.  Escriba preguntas en lenguaje natural, por ejemplo:
    *   *"¿Qué noticias hay sobre fútbol hoy?"*
    *   *"Hazme un resumen de las noticias de política de esta semana."*
3.  La IA leerá sus noticias guardadas y le dará una respuesta resumida.

---

## 10. Configuración y Perfil

En su **Perfil** (icono de usuario arriba a la derecha) puede:
*   Cambiar su contraseña.
*   Ver su plan actual y límites de uso.
*   Cambiar entre **Modo Claro** y **Modo Oscuro** (icono de sol/luna) para descansar la vista.

---

## 11. Solución de Problemas

**Problema: No se descargan noticias.**
*   **Solución**: Verifique que la URL de la fuente sea correcta y siga activa. A veces los sitios web cambian su diseño; intente editar la fuente y guardar de nuevo para que el sistema recalcule los selectores.

**Problema: Las imágenes no cargan.**
*   **Solución**: Algunos sitios bloquean la carga de imágenes externas. Esto es normal y depende de la fuente original.

**Problema: Olvidé mi contraseña.**
*   **Solución**: Contacte al administrador del sistema para que restablezca su acceso.

**Problema: Mi pago de Yape no se activa.**
*   **Solución**: Los pagos manuales requieren verificación humana. Espere unas horas o contacte a soporte si demora más de 24 horas.

---

*Manual generado para NoticiaScraping v3.0 - 2025*
