import re
from flask import render_template, request, Flask, render_template, request, redirect, url_for, session, flash, jsonify
 
from database.conexion import db
#  ~ Importamos el archvio con el nombre del Blueprint para la sección
from flask_login import login_required, current_user
from ...admin import bp_admistracion



# ^ Vamos a crear las rutas para renderizar el HTML y mostrar los logs almacenados en la BD 


# * Renderizar el HTML 
@bp_admistracion.route('/logs')

