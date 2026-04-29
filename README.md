# 🎮 ClassRoom Clash

**ClassRoom Clash** es un toolkit educativo gamificado y una herramienta administrativa para profesores. Diseñado y refactorizado bajo una arquitectura modular limpia en Python (utilizando Tkinter para la interfaz y SQLite para la persistencia de datos), la aplicación permite gestionar grupos de estudiantes y gamificar su participación en clase.

---

## 🌟 Características Principales

*   **📂 Gestión de Grupos:** Crea, edita, renombra y organiza tus grupos escolares. Ahora puedes **Archivar** los grupos (por ejemplo, al terminar el semestre) para limpiar la interfaz sin perder su historial.
*   **🎰 Sorteo Champions Style:** Crea equipos balanceados en clase con un solo clic. Cuenta con un **Modo Automático** (distribuye estudiantes cada 2 segundos) y un **Modo Manual** para inyectar emoción en el aula.
*   **🎡 Tómbola de Participación:** Selecciona aleatoriamente a un alumno para pasar a la pizarra o contestar una pregunta. 
    *   **Puntos:** Asigna puntos positivos o negativos instantáneos que se suman al Ranking.
    *   **0 Puntos (Participó):** Registra que el alumno formó parte de la clase sin afectar su puntaje.
    *   **Exclusión Temporal:** Si el estudiante está ausente o ya pasó, puedes excluirlo (con 🚫) para que la tómbola no lo vuelva a escoger.
*   **📋 Control de Actividades:** Monitorea y registra el orden de entrega de actividades y trabajos en clase. Se genera automáticamente un ranking (oro 🥇, plata 🥈, bronce 🥉) según la velocidad de entrega de los estudiantes. ¡Ahora puedes eliminar actividades por completo o corregir (borrar) una entrega accidental!
*   **🏆 Leaderboard & Reportes:** Visualiza rápidamente a los alumnos más destacados y **exporta el reporte a Excel (.xlsx)** para tener el récord de participación integrado con tu libreta de calificaciones.
*   **❓ Ayuda Integrada Contextual:** En todas las pantallas principales encontrarás un botón azul de **"❓ Ayuda"** que despliega instrucciones instantáneas de cómo utilizar cada ventana.

---

## 🏗️ Arquitectura Modular (Código Fuente)

El código se ubica dentro del paquete `clashroomclash/` y ha sido diseñado usando *mixins* para lograr una escalabilidad óptima y mantener la interfaz separada por dominios lógicos:

*   `app.py`: La clase principal (`ClassRoomClashApp`) que sirve como el contenedor maestro y estado general, inyectando todos los *mixins*. Aquí reside el diálogo global de ayuda contextual.
*   `state.py`: Clase `AppState` que mantiene centralizado el estado efímero (alumnos cargados, nombre de grupo, etc.) desacoplado de la interfaz.
*   `database.py`: Componente `DatabaseManager` con toda la lógica de SQLite (`desafio_data.db`). Ahora implementa las tablas con sus banderas nuevas (ej. `is_archived`).
*   `constants.py`: Sistema de diseño (colores, temas, fuentes) que proporciona una apariencia "premium", moderna y fluida.
*   `screens.py`: El Mixin que renderiza la Gestión de Grupos, Historial, Exportación a Excel y Leaderboard.
*   `sorteo_screen.py`: El Mixin que domina la lógica visual e hilos de animación de los equipos al azar.
*   `wheel.py`: El Mixin de la Tómbola de asignación y sus diálogos flotantes de captura de puntos/exclusión.
*   `activities.py`: Mixin para gestionar el CRUD completo de tareas y el flujo de registro de entregas.
*   `build_exe.py`: Script unificado para empaquetar la aplicación en `.exe`.

---

## 🚀 Compilación y Ejecución (Portable)

La herramienta está construida para correr en Windows de manera nativa sin instalaciones adicionales para el profesor.

### Ejecutar desde Código:
Asegúrate de tener Python instalado y ejecutar:
```bash
python -m clashroomclash
```

### Empaquetado Automático:
Para generar el archivo ejecutable (`.exe`) portable que le puedes compartir a los docentes, se incluye un script empaquetador (`build_exe.py`) que automáticamente usa `PyInstaller`.
```bash
python build_exe.py
```
**Resultado:** El script tomará todos los módulos e imágenes y soltará un único archivo listo para usarse (`ClassRoomClash.exe`) en la carpeta `/dist`.

### Portabilidad de Datos:
El ejecutable y la Base de Datos viven juntos. El sistema buscará (o creará) el archivo `desafio_data.db` en el mismo directorio donde coloques el `.exe`. Esto permite llevar la aplicación y la base de datos de los alumnos en una Memoria USB para uso 100% desconectado en cualquier PC.
