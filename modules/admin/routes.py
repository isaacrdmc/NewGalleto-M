

# ? Acá es donde crearemos las rutas necesarias para la sección de adminstación 








"""
# ? COmo ejemplo vamos a crear una ruta falsa para un CREATE usuario admin




# ^ Este seria el ejemplo para crear una API con la que podrimos revisarla en postman

@admin.route('/admin/create', methods=['POST'])
def create_admin():
    data = request.get_json()
    new_admin = AdminUser(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"message": "Administrador creado"}), 201




# ^ Este seria el ejemplo para crear des hacer la API de la misma ruta y poderla utilizar dentro dle sistema


from flask import render_template, redirect, url_for, request

@admin.route('/admin/create', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_admin = AdminUser(username=username, email=email, password=password)
        db.session.add(new_admin)
        db.session.commit()

        return redirect(url_for('admin.get_admins'))  # Redirigir a la lista de admins

    return render_template('admin/create_admin.html')

"""





