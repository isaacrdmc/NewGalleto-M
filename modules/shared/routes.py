# routes.py
from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Rol
from database.conexion import db
from datetime import datetime, timedelta
import re
from flask_login import login_user, logout_user, current_user, login_required
from . import bp_shared
from sqlalchemy.exc import SQLAlchemyError
from flask import abort
from urllib.parse import urlparse, urljoin

# Configuración de seguridad
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
MAX_LOGIN_ATTEMPTS = 3
SESSION_INACTIVITY_TIMEOUT = timedelta(minutes=30)

def is_safe_url(target):
    """Verifica que la URL de redirección sea segura"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@bp_shared.before_app_request
def check_session_timeout():
    """Verifica el tiempo de inactividad de la sesión"""
    if current_user.is_authenticated:
        last_activity = session.get('last_activity')
        if last_activity and datetime.now() - datetime.fromisoformat(last_activity) > SESSION_INACTIVITY_TIMEOUT:
            logout_user()
            flash('Tu sesión ha expirado por inactividad', 'warning')
            return redirect(url_for('shared.login'))
        session['last_activity'] = datetime.now().isoformat()

@bp_shared.route('/')
def index():
    """Redirige al usuario según su rol"""
    if current_user.is_authenticated:
        # Registrar actividad
        session['last_activity'] = datetime.now().isoformat()
        
        # Redirigir según rol
        role_redirects = {
            'Administrador': 'admin.dashboard_admin',
            'Produccion': 'production.dashboard_produccion',
            'Ventas': 'ventas.ventas',
            'Cliente': 'cliente.portal_cliente'
        }
        
        redirect_view = role_redirects.get(current_user.rol.nombreRol)
        if redirect_view:
            return redirect(url_for(redirect_view))
        
        logout_user()  # Si el rol no es reconocido, cerrar sesión
        flash('Rol no reconocido', 'danger')
    
    # Redirigir a login si no está autenticado o rol no reconocido
    return redirect(url_for('shared.login'))

@bp_shared.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('shared.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        next_url = request.args.get('next')
        
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'danger')
            return render_template('shared/login.html', page_title='Iniciar Sesión')
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                flash('Usuario y/o contraseña incorrectos', 'danger')
                return render_template('shared/login.html', page_title='Iniciar Sesión')
            
            # Verificar bloqueo temporal primero
            if user.esta_bloqueado_temporalmente():
                tiempo_restante = (user.bloqueoTemporal - datetime.now()).seconds
                flash(f'Cuenta bloqueada temporalmente por seguridad. Intenta nuevamente en {tiempo_restante} segundos.', 'warning')
                return render_template('shared/login.html', page_title='Iniciar Sesión')
            
            # Verificar bloqueo permanente
            if user.estado == 'Bloqueado':
                flash('Tu cuenta está bloqueada. Contacta al administrador.', 'danger')
                return render_template('shared/login.html', page_title='Iniciar Sesión')
            
            if user.check_password(password):
                # Login exitoso - resetear contadores
                login_user(user)
                user.ultimoAcceso = datetime.now()
                user.intentosFallidos = 0
                user.bloqueoTemporal = None
                db.session.commit()
                
                session['last_activity'] = datetime.now().isoformat()
                flash('¡Has iniciado sesión correctamente!', 'success')
                
                if next_url and is_safe_url(next_url):
                    return redirect(next_url)
                return redirect(url_for('shared.index'))
            else:
                # Login fallido
                user.intentosFallidos += 1
                
                if user.intentosFallidos >= MAX_LOGIN_ATTEMPTS:
                    # Bloquear temporalmente por 30 segundos
                    user.bloqueoTemporal = datetime.now() + timedelta(seconds=30)
                    flash('Demasiados intentos fallidos. Tu cuenta estará bloqueada temporalmente por 30 segundos.', 'danger')
                else:
                    flash(f'Usuario y/o contraseña incorrectos. Intentos restantes: {MAX_LOGIN_ATTEMPTS - user.intentosFallidos}', 'danger')
                
                db.session.commit()
                
        except SQLAlchemyError as e: 
            db.session.rollback()
            current_app.logger.error(f'Error de base de datos en login: {str(e)}')
            flash('Error al procesar la solicitud. Intente nuevamente.', 'danger')
    
    return render_template('shared/login.html', page_title='Iniciar Sesión')

@bp_shared.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario"""
    logout_user()
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('shared.login'))

@bp_shared.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de nuevos usuarios (clientes)"""
    if current_user.is_authenticated:
        return redirect(url_for('shared.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        # Validaciones
        if not username or not password or not confirm_password:
            errors.append('Todos los campos son obligatorios')
        elif len(username) < 4:
            errors.append('El nombre de usuario debe tener al menos 4 caracteres')
        elif password != confirm_password:
            errors.append('Las contraseñas no coinciden')
        elif not PASSWORD_REGEX.match(password):
            errors.append('La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('shared.register'))
        
        try:
            # Verificar si el usuario ya existe
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya está registrado', 'danger')
                return redirect(url_for('shared.register'))
            
            # Obtener o crear rol de cliente
            rol_cliente = Rol.query.filter_by(nombreRol='Cliente').first()
            if not rol_cliente:
                rol_cliente = Rol(nombreRol='Cliente', descripcion='Usuario cliente de la plataforma')
                db.session.add(rol_cliente)
                db.session.commit()
            
            # Crear nuevo usuario
            new_user = User(
                username=username,
                idRol=rol_cliente.idRol,
                estado='Activo'
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('shared.login'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Error en registro: {str(e)}')
            flash('Error al registrar el usuario. Por favor, intenta nuevamente.', 'danger')
    
    return render_template('shared/register.html', page_title='Registro')

@bp_shared.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Maneja las solicitudes de restablecimiento de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('shared.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Por favor ingresa tu nombre de usuario', 'danger')
            return redirect(url_for('shared.reset_password_request'))
        
        try:
            user = User.query.filter_by(username=username).first()
            
            # Siempre mostrar el mismo mensaje por seguridad
            flash('El usuario existe, se enviarán instrucciones', 'info')
            
            if user:
                # Generar token de recuperación
                token = user.generate_reset_token()
                
                # En desarrollo: Mostrar el enlace en pantalla
                reset_url = url_for('shared.reset_password', token=token, _external=True)
                flash(f'Enlace de recuperación (DEBUG): {reset_url}', 'info')
                
                # En producción aquí iría el envío real del correo
                # send_password_reset_email(user, reset_url)
            
            return redirect(url_for('shared.login'))
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error en reset_password_request: {str(e)}')
            flash('Error al procesar la solicitud. Intente nuevamente.', 'danger')
    
    return render_template('shared/reset_pass.html', page_title='Recuperar Contraseña')


@bp_shared.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Maneja el formulario de nueva contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('shared.index'))
    
    # Verificar el token
    user = User.verify_reset_token(token)
    if not user:
        flash('El enlace de recuperación es inválido o ha expirado', 'danger')
        return redirect(url_for('shared.reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(request.url)
        
        try:
            # Actualizar la contraseña
            user.set_password(password)
            db.session.commit()
            
            flash('Tu contraseña ha sido actualizada correctamente', 'success')
            return redirect(url_for('shared.login'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Error al resetear password: {str(e)}')
            flash('Error al actualizar la contraseña. Intente nuevamente.', 'danger')
    
    return render_template('shared/new_password.html', token=token)