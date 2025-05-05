# Pokeneas - Taller 02 TEIS

Este proyecto es una aplicación web desarrollada con Flask que presenta criaturas llamadas "Pokeneas", inspiradas en la cultura paisa colombiana.

## Equipo de Trabajo

- Maximiliano Bustamante
- Valeria Hornung Urrego
- Juan Jose Jara

Universidad EAFIT - Tópicos Especializados en Ingeniería de Software

## Descripción

Pokeneas es una plataforma que permite:

- Explorar una colección de Pokeneas (criaturas inspiradas en la cultura paisa)
- Ver un Pokenea aleatorio con su imagen y frase filosófica
- Crear y añadir tu propio Pokenea personalizado
- Acceder a información de Pokeneas mediante una API REST

## Tecnologías Utilizadas

- **Backend:** Flask (Python)
- **Base de datos:** PostgreSQL (NeonDB)
- **Almacenamiento de imágenes:** AWS S3
- **Contenedores:** Docker
- **CI/CD:** GitHub Actions
- **Frontend:** HTML, CSS

## Configuración del Entorno

Para configurar el entorno, cree un archivo `.env` basado en el archivo de ejemplo `.env.example` incluido en este repositorio. Este archivo debe contener las siguientes variables de entorno:

- `AWS_BUCKET`: Nombre del bucket S3 de AWS.
- `AWS_REGION`: Región de AWS donde se encuentra el bucket.
- `SECRET_KEY`: Clave secreta para Flask.
- `DATABASE_URL`: URL de conexión a la base de datos PostgreSQL.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

- `app/`: Contiene el código fuente de la aplicación.
  - `templates/`: Archivos HTML para las vistas.
  - `static/`: Archivos estáticos como CSS e imágenes.
  - `models.py`: Definición de los modelos de datos.
  - `routes.py`: Definición de las rutas de la aplicación.
  - `utils.py`: Funciones auxiliares.
- `requirements.txt`: Dependencias del proyecto.
- `Dockerfile`: Configuración para construir la imagen Docker.
- `.github/workflows/`: Configuración de CI/CD con GitHub Actions.

## Instrucciones para Ejecutar

1. Clone este repositorio.
2. Cree un entorno virtual e instale las dependencias desde `requirements.txt`.
3. Configure el archivo `.env` con las variables necesarias.
4. Ejecute la aplicación con `python run.py`.

## Créditos

Este proyecto fue desarrollado por Maximiliano Bustamante, Valeria Hornung Urrego y Juan Jose Jara como parte del Taller 02 de la materia Tópicos Especializados en Ingeniería de Software en la Universidad EAFIT.
