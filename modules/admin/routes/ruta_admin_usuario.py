from flask import current_app, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..services import (
    agregar_usuario, obtener_usuarios, actualizar_usuario,
    eliminar_usuario, obtener_roles
)
from ..forms.usuario import UsuarioForm
from ...admin import bp_admistracion
from werkzeug.security import generate_password_hash
from ...shared.models import User, Rol

@bp_admistracion.route('/usuarios')
@login_required
def usuarios():
    if current_user.rol.nombreRol != 'Administrador':
        current_app.logger.warning(f'Acceso denegado a {current_user.username} a la ruta para intractuar con los datos de los usuarios')
        return redirect(url_for('shared.login'))
    
    lista_usuarios = obtener_usuarios()
    roles = obtener_roles()
    form = UsuarioForm()
    form.rol.choices = [(str(rol.idRol), rol.nombreRol) for rol in roles]
    
    current_app.logger.info(f'Acceso a la ruta para intractuar con los datos de los usuaios por {current_user.username}')
    return render_template('admin/usuarios.html', usuarios=lista_usuarios, form=form)
 
@bp_admistracion.route('/usuarios/agregar', methods=['POST'])
@login_required
def agregar_usuario_route():
    try:
        data = request.get_json()
        
        nuevo_usuario = agregar_usuario(
            username=data['username'],
            password=data['password'],
            idRol=data['rol'],
            estado=data['estado']
        )
        
        current_app.logger.info(f'Usuario {nuevo_usuario.username} agregado por {current_user.username}')

        return jsonify({
            "mensaje": "Usuario agregado correctamente",
            "usuario": {
                "idUser": nuevo_usuario.idUser,
                "username": nuevo_usuario.username,
                "rol": {
                    "idRol": nuevo_usuario.rol.idRol,
                    "nombreRol": nuevo_usuario.rol.nombreRol
                },
                "fechaRegistro": nuevo_usuario.fechaRegistro.isoformat(),
                "ultimoAcceso": nuevo_usuario.ultimoAcceso.isoformat() if nuevo_usuario.ultimoAcceso else None,
                "estado": nuevo_usuario.estado
            }
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error al agregar usuario: {str(e)}')
        return jsonify({"error": str(e)}), 500
    

@bp_admistracion.route('/usuarios/editar/<int:id>', methods=['POST'])
@login_required
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

        current_app.logger.info(f'Usuario {usuario.username} editado por {current_user.username}')
        
        return jsonify({
            "mensaje": "Usuario actualizado correctamente",
            "usuario": {
                "id": usuario.idUser,
                "username": usuario.username,
                "rol": usuario.rol.nombreRol
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error al editar usuario: {str(e)}')
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario_route(id):
    try:
        if id == current_user.idUser:
            current_app.logger.warning(f'Intento de eliminar su propio usuario por {current_user.username}')
            return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400
        
        current_app.logger.info(f'Usuario {id} eliminado por {current_user.username}')
            
        usuario = eliminar_usuario(id)
        return jsonify({
            "mensaje": "Usuario eliminado correctamente",
            "usuario": {
                "id": usuario.idUser,
                "username": usuario.username
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error al eliminar usuario: {str(e)}')
        return jsonify({"error": str(e)}), 500

@bp_admistracion.route('/usuarios/obtener/<int:id>', methods=['GET'])
@login_required
def obtener_usuario(id):
    try:
        usuario = User.query.get_or_404(id)
        if usuario.rol.nombreRol == 'Cliente':
            current_app.logger.warning(f'Intento de editar cliente por {current_user.username}')
            return jsonify({"error": "No se puede editar clientes aquí"}), 400
        
        current_app.logger.info(f'Usuario {usuario.username} obtenido po {current_user.username}')
            
        return jsonify({
            "id": usuario.idUser,
            "username": usuario.username,
            "rol": usuario.rol.idRol,
            "estado": usuario.estado
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error al obtener usuario: {str(e)}')
        return jsonify({"error": str(e)}), 500
    

@bp_admistracion.route('/usuarios/listar')
@login_required
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

            current_app.logger.info(f'Lista de usuario obtenida por {current_user.username}')
            
        return jsonify(usuarios_data), 200
    except Exception as e:
        current_app.logger.error(f'Error al listar usuarios: {str(e)}')
        return jsonify({"error": str(e)}), 500