# 🎮 ClassRoom Clash

![ClassRoom Clash Banner](https://img.shields.io/badge/ClassRoom-Clash-4361EE?style=for-the-badge&logo=python&logoColor=white) 
![Status](https://img.shields.io/badge/Status-Activo-06D6A0?style=flat-square) 
![Python](https://img.shields.io/badge/Python-3.x-3A86FF?style=flat-square&logo=python)

**ClassRoom Clash** es un increíble toolkit educativo desarrollado en Python, diseñado para dinamizar tus clases, fomentar la participación y automatizar la gestión de grupos. Con un diseño plano y moderno ("Flat Design"), animaciones fluidas y persistencia de datos, convierte cualquier clase en una experiencia competitiva y divertida.

---

## ✨ Características Principales

- **🎲 Sorteo Estilo Champions:** Crea equipos de trabajo de forma dinámica usando un algoritmo de "round-robin" con animaciones tipo tómbola llenas de suspenso.
- **🎡 Tómbola de Participación:** Elige estudiantes al azar para participar en clase y asígnales puntos al instante mediante un sistema de ruleta interactiva.
- **🏆 Leaderboard y Ranking:** Fomenta la sana competencia con un sistema de puntos global y por grupo. ¡Premia a tus mejores alumnos con medallas de oro, plata y bronce!
- **📋 Control de Actividades:** Registra la entrega de tareas en tiempo real, guardando el orden exacto en el que los estudiantes terminan sus actividades.
- **📂 Gestión de Grupos Segura:** Toda tu información (estudiantes, equipos, historial) se guarda localmente de forma segura usando SQLite.
- **📊 Exportación a Excel:** Genera reportes profesionales `.xlsx` (o `.csv`) en un solo clic, incluyendo puntajes, posiciones y datos de estudiantes.

---

## 🛠️ Requisitos Previos

Asegúrate de tener instalado Python 3.x en tu sistema. Además, puedes instalar la dependencia opcional para poder exportar reportes en Excel:

```bash
pip install openpyxl
```

---

## 🚀 ¿Cómo empezar?

Clona o descarga este repositorio en tu ordenador. Tienes varias formas de ejecutar la aplicación:

### Opción 1: Ejecutar como paquete (Recomendado)
Abre tu terminal en la carpeta principal del proyecto y ejecuta:
```bash
python -m clashroomclash
```

### Opción 2: Usar el lanzador
Si prefieres un script directo, puedes ejecutar el lanzador:
```bash
python launcher.py
```

### Opción 3: ¡Crear un ejecutable portable! (.exe)
¿Quieres llevarte ClassRoom Clash en un USB sin instalar Python en otras computadoras? Usa el constructor incluido:
```bash
python build_exe.py
```
> **Nota:** Esto generará un archivo `ClassRoomClash.exe` en la carpeta `dist`. Depende de la librería `PyInstaller` (`pip install pyinstaller`).

---

## 🏗️ Arquitectura del Proyecto

El proyecto está diseñado bajo un patrón de "Mixins" para mantener el código base limpio y sumamente escalable. 

- `app.py`: Ensambla todos los mixins en la aplicación principal de Tkinter.
- `screens.py`: Menú, gestión de grupos, y creación de actividades.
- `sorteo_screen.py`: Pantalla con la lógica y animación de la tómbola para sorteos de equipo.
- `wheel.py`: Animación fluida de la ruleta de participación.
- `activities.py`: Rastreo de entregas y rankings.
- `database.py`: Gestor SQLite que guarda absolutamente todo de manera automática.

---

## 🎨 Paleta de Colores y UI

ClassRoom Clash utiliza una paleta moderna, amigable y contrastante para retener la atención del estudiante:
- **Azul Vibrante** y **Header Medianoche** para concentración.
- **Magenta y Dorado** para momentos de "Clímax" (ganadores, ruletas).
- Diseño limpio y libre de distracciones con retroalimentación visual en tiempo real.

---

> *"Dinamiza tu aula, sorprende a tus estudiantes y convierte el aprendizaje en el mejor juego."* 🚀
