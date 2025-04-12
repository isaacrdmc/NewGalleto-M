from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from modules.admin.routes.ruta_admin_dashboard import admin_required
from ..services import (
    agregar_usuario, obtener_usuarios, actualizar_usuario,
    eliminar_usuario, obtener_roles
)
from ..forms.usuario import UsuarioForm
from ...admin import bp_admistracion
from werkzeug.security import generate_password_hash
from ...shared.models import User, Rol


@bp_admistracion.route('/usuarios')
@admin_required
def usuarios():
    lista_usuarios = obtener_usuarios()
    roles = obtener_roles()
    form = UsuarioForm()
    form.rol.choices = [(str(rol.idRol), rol.nombreRol) for rol in roles]
    
    return render_template('admin/usuarios.html', usuarios=lista_usuarios, form=form)

@bp_admistracion.route('/usuarios/agregar', methods=['POST'])
@admin_required
def agregar_usuario_route():
    try:
        data = request.get_json()
        
        # Validación de datos mínimos
        if not all(key in data for key in ['username', 'password', 'rol', 'estado']):
            return jsonify({'error': 'Datos incompletos'}), 400
            
        # Validar fortaleza de contraseña
        if len(data['password']) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
            
        nuevo_usuario = agregar_usuario(
            username=data['username'],
            password=data['password'],
            idRol=data['rol'],
            estado=data['estado']
        )
        
        return jsonify({
            "mensaje": "Usuario agregado correctamente",
            "usuario": {
                "idUser": nuevo_usuario.idUser,
                "username": nuevo_usuario.username,
                "rol": nuevo_usuario.rol.nombreRol,
                "estado": nuevo_usuario.estado
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp_admistracion.route('/usuarios/editar/<int:id>', methods=['POST'])
@admin_required
def editar_usuario(id):
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['username', 'rol', 'estado']):
            return jsonify({'error': 'Datos requeridos faltantes'}), 400
            
        usuario = actualizar_usuario(
            user_id=id,
            username=data['username'],
            idRol=data['rol'],
            estado=data['estado'],
            password=data.get('password')
        )
        
        return jsonify({
            "mensaje": "Usuario actualizado correctamente",
            "usuario": {
                "id": usuario.idUser,
                "username": usuario.username,
                "rol": usuario.rol.nombreRol
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_usuario_route(id):
    try:
        if id == current_user.idUser:
            return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400
            
        usuario = eliminar_usuario(id)
        return jsonify({
            "mensaje": "Usuario eliminado correctamente",
            "usuario": {
                "id": usuario.idUser,
                "username": usuario.username
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/usuarios/obtener/<int:id>', methods=['GET'])
@admin_required
def obtener_usuario(id):
    try:
        usuario = User.query.get_or_404(id)
        if usuario.rol.nombreRol == 'Cliente':
            return jsonify({"error": "No se puede editar clientes aquí"}), 400
            
        return jsonify({
            "id": usuario.idUser,
            "username": usuario.username,
            "rol": usuario.rol.idRol,
            "estado": usuario.estado
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp_admistracion.route('/usuarios/listar')
@admin_required
def listar_usuarios():
    try:
        usuarios = obtener_usuarios()
        usuarios_data = []
        
        for u in usuarios:
            usuarios_data.append({
                "idUser": u.idUser,
                "username": u.username,
                "rol": {
                    "idRol": u.rol.idRol,
                    "nombreRol": u.rol.nombreRol
                },
                "fechaRegistro": u.fechaRegistro.isoformat() if u.fechaRegistro else None,
                "ultimoAcceso": u.ultimoAcceso.isoformat() if u.ultimoAcceso else None,
                "estado": u.estado
            })
            
        return jsonify(usuarios_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500