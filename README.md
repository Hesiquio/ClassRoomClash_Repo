# 🎮 ClassRoom Clash

**ClassRoom Clash** es un toolkit educativo gamificado y una herramienta administrativa para profesores. Diseñado bajo una arquitectura modular limpia en Python (utilizando Tkinter para la interfaz y SQLite para la persistencia de datos), la aplicación permite gestionar grupos de estudiantes y gamificar su participación en clase con una estética moderna y fluida.

---

## 🌟 Características Principales

*   **📂 Gestión de Grupos:** Crea, edita y organiza tus grupos escolares. Incluye un sistema de **Archivado** para ocultar grupos terminados sin perder sus datos.
*   **🎰 Sorteo Champions Style:** Distribuye alumnos en equipos balanceados con animaciones emocionantes. Cuenta con **Modo Automático** (cada 2 segundos) y **Modo Manual**.
*   **🎡 Tómbola de Participación:** Selección aleatoria de alumnos con asignación de puntos instantánea, exclusión de ausentes y registro de participación rápida.
*   **🎲 Tómbola de Equipos:** Herramienta dedicada para definir el orden de participación de los equipos. Permite cargar equipos de sorteos previos o ingresar nombres personalizados.
*   **📋 Control de Actividades:** Monitorea el orden de entrega de tareas en tiempo real. Genera podios automáticos (🥇, 🥈, 🥉) según la velocidad de entrega de los alumnos.
*   **🏆 Leaderboard & Reportes:** Visualiza el ranking global o por grupo. **Exporta reportes profesionales a Excel (.xlsx)** para integrar directamente con tus hojas de cálculo.
*   **❓ Ayuda Integrada:** Cada pantalla principal cuenta con un botón de ayuda contextual que explica las funciones específicas de esa sección.

---

## 🏗️ Arquitectura del Proyecto

El código reside en el paquete `classroomclash/` y utiliza un patrón de *Mixins* para lograr una alta cohesión y bajo acoplamiento:

*   `app.py`: Orquestador principal (`ClassRoomClashApp`) que ensambla los módulos y maneja el estado raíz.
*   `screens.py`: Gestiona el menú principal, configuración de grupos, historial, leaderboard y exportación.
*   `sorteo_screen.py`: Lógica visual y animación de la tómbola para **repartir alumnos en equipos**.
*   `team_raffle_screen.py`: Pantalla dedicada a **sortear el orden de participación de los equipos**.
*   `wheel.py`: Implementa la **ruleta de participación individual** y el sistema de puntos.
*   `activities.py`: Control completo del flujo de entrega de actividades y tareas.
*   `database.py`: `DatabaseManager` encargado de la persistencia en SQLite (`desafio_data.db`).
*   `state.py`: Centraliza el estado efímero (alumnos cargados, flags de animación) desacoplado de la UI.
*   `constants.py`: Sistema de diseño (colores, fuentes, temas) para una apariencia "premium".
*   `widgets.py`: Componentes de UI personalizados (como frames con scroll automático).
*   `launcher.py`: Script de entrada simplificado en la raíz del proyecto.

---

## 🚀 Instalación y Uso

### Ejecución desde Código Fuente
Requiere Python 3.8 o superior. Se recomienda instalar las dependencias necesarias para las funcionalidades de Excel y compilación:

```bash
pip install openpyxl Pillow PyInstaller
python -m classroomclash
```

### Compilación (Generar .exe)
Para generar el archivo ejecutable portátil para Windows:
```bash
python build_exe.py
```
**Resultado:** El script empaquetará todos los módulos e iconos en un único archivo `ClassRoomClash.exe` dentro de la carpeta `/dist`.

### Portabilidad de Datos
La aplicación es 100% portable. El sistema busca o crea automáticamente el archivo `desafio_data.db` en el mismo directorio donde se encuentre el ejecutable. Esto permite llevar la aplicación y la base de datos en una memoria USB sin necesidad de instalación.

---
© 2024 ClassRoom Clash - Toolkit Educativo
