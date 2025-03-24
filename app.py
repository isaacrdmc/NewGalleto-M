"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
from datetime import datetime, timedelta
"""

# TODO archvio de ejecución de la APP
from __init__ import create_app         # ? De la acrpeta de APP importamos la carpeta app

app = create_app()

# * Ejecutar la aplicación en su totalidad
if __name__ == '__main__':
    app.run(debug=True)




# app = Flask(__name__)
# app.secret_key = 'mySecretKey'  # Necesario para manejar las sesiones
