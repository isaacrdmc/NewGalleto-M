from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, blueprints
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
from datetime import datetime, timedelta


# TODO __init__.py principal de la app, es odnde creamos y configuramos la APP de flask

# ? Definimos una función que es donde iran todos los brueprint del sistio

def crearApp():
    # * Creamos una variable para instanciar Flask
    app = Flask(__name__)


    # ? Importamos los Blueprints de cada módulo
    from modules.admin import bp_admistracion
    from modules.client import models
    from modules.production import models
    from modules.ventas import models

    # ? Registramos los bluebrints de cada módulo importado
    app.register_blueprint(bp_admistracion)



    # * Ahora los utilizamos
