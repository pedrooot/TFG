# TFG - Vigilancia sobre pacientes diabéticos que usan un sistema de monitorización continua de glucosa
En este repositorio comienzo a trabajar sobre el TFG de ingeniería informática.
Autor: Pedro Martín González
Título: Vigilancia sobre pacientes diabéticos que usan un sistema de monitorización continua de glucosa

Para instalar los requerimientos:
`pip install -r requirements.txt`
o
`poetry install`

Cuando ejecutes la aplicación:
`python3 application.py`

Se abrirá el portal de acceso a GlucoseBot.

Este proyecto está hecho para hostearse en el servicio EC2 de AWS y a su vez hace uso de servicios como RDS para la base de datos, VPC para la red y Secrets Manager para la gestión de las credenciales por lo que ejecutar este proyecto localmente requiere de severas modificaciones en el código.
