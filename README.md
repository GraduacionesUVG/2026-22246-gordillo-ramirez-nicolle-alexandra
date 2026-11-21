# Evaluación de la calidad visual y percepción de recursos generados con IA en un videojuego pixel art

## Descripción
Trabajo Profesional de Graduación que compara dos versiones de una misma demo de un videojuego de gestión de una cafetería en estilo pixel art: una con recursos gráficos elaborados de forma tradicional y otra con recursos generados con IA (Pixellab AI). El objetivo es identificar si el rechazo hacia el pixel art generado con IA se asocia con el conocimiento de su uso o con su calidad visual. Participaron 60 estudiantes de la Universidad del Valle de Guatemala, divididos en un grupo informado y un grupo no informado (30 por grupo), que evaluaron ambas versiones con una escala Likert de 1 a 5. La calidad técnica se evaluó con una rúbrica de cuatro criterios y con las métricas SSIM y PSNR.

Versiones jugables en línea:
- Versión tradicional: https://akice.itch.io/uvg-game-tesis-v1
- Versión con IA: https://akice.itch.io/uvg-game-tesis2

## Tecnologías Utilizadas
- Godot Engine 4.7.2 (GDScript)
- Pixilart (recursos tradicionales) y Pixellab AI (recursos con IA)
- Python 3.13, scikit-image, scipy y numpy (SSIM, PSNR y análisis estadístico)
- Google Forms (cuestionario) y LaTeX (informe)

## Requisitos Previos
- Godot Engine 4.7.2 (descarga gratuita en https://godotengine.org)
- Git
- Para reproducir las métricas: Python 3.13+ con `scikit-image`, `scipy` y `numpy`

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/[tu-usuario]/2026-22246-nicolle-alexandra-gordillo-ramirez.git
   cd 2026-22246-nicolle-alexandra-gordillo-ramirez
   ```
2. Instalar dependencias: el videojuego no requiere instalar paquetes (no usa Node.js). Solo para las métricas:
   ```bash
   pip install scikit-image scipy numpy
   ```
3. Configurar variables de entorno: este proyecto no usa variables de entorno ni credenciales. El archivo `src/.env.example` se incluye solo por requisito de la guía de entrega.
4. Ejecutar el proyecto: abrir Godot 4.7.2, elegir **Importar**, seleccionar el `project.godot` de la versión que se quiere probar y presionar **F5**. También puede jugarse en línea con los enlaces de la sección Descripción.
   - Versión tradicional: `src/version-tradicional/project.godot`
   - Versión con IA: `src/version-ia/project.godot`
5. Reproducir las métricas y el análisis: ver la carpeta `src/analisis` (`1_ssim_psnr.py`, `2_rubrica.py`, `3_spearman.py` y `analisis_resultados.py`).

## Estructura del código (`/src`)
- `version-tradicional/`: proyecto de Godot con los recursos gráficos elaborados de forma tradicional (rama `main` del repositorio de desarrollo).
- `version-ia/`: proyecto de Godot con los recursos generados con Pixellab AI y el código asistido por IA (rama `IAG`).
- `analisis/`: scripts de Python para SSIM, PSNR, rúbrica, correlación de Spearman y análisis estadístico de las respuestas.

Repositorio de desarrollo del videojuego (ramas `main` e `IAG`): https://github.com/Jose-Prince/UVG-Tesis-Game

## Capturas
Las capturas de pantalla del sistema se encuentran en [`/capturas`](capturas) (10 capturas).

## Demo
El video demostrativo se encuentra en [`/demo/demo.mp4`](demo/demo.mp4).

## Documentación
El informe final del proyecto está disponible en [`/docs/informe_final.pdf`](docs/informe_final.pdf).

El consentimiento de uso de foto y video firmado se encuentra en [`/docs/consentimiento_firmado.pdf`](docs/consentimiento_firmado.pdf).

## Autores
- Nicolle Alexandra Gordillo Ramírez - 22246

Colaboradores en el desarrollo del videojuego: José Alejandro Prince Martínez, Héctor Daniel Penedo Juarez.

## Licencia
MIT (ver `src/version-tradicional/LICENSE`)
