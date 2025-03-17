from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base de datos en memoria (simulación)
proveedores = [
    {"id": "0001", "empresa": "19 Hermanos", "telefono": "477-724-5893", 
     "correo": "queso@gmail.com", "direccion": "Paseo de los Insurgentes 362", 
     "productos": "Leche y queso"},
    {"id": "0002", "empresa": "Skibidi", "telefono": "477-123-4567", 
     "correo": "skibidi@gmail.com", "direccion": "Avenida Central 123", 
     "productos": "Bebidas"}
]

@app.route('/proveedores')
def listar_proveedores():
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/proveedores/agregar', methods=['POST'])
def agregar_proveedor():
    datos = request.get_json()
    nuevo_proveedor = {
        "id": str(len(proveedores) + 1).zfill(4),  # Generar ID automático
        "empresa": datos['empresa'],
        "telefono": datos['telefono'],
        "correo": datos['correo'],
        "direccion": datos['direccion'],
        "productos": datos['productos']
    }
    proveedores.append(nuevo_proveedor)
    return jsonify({"mensaje": "Proveedor agregado", "proveedor": nuevo_proveedor})

@app.route('/proveedores/<id>', methods=['GET'])
def obtener_proveedor(id):
    for proveedor in proveedores:
        if proveedor['id'] == id:
            return jsonify(proveedor)
    return jsonify({"error": "Proveedor no encontrado"}), 404

@app.route('/proveedores/editar/<id>', methods=['POST'])
def editar_proveedor(id):
    for proveedor in proveedores:
        if proveedor['id'] == id:
            proveedor['empresa'] = request.json['empresa']
            proveedor['telefono'] = request.json['telefono']
            proveedor['correo'] = request.json['correo']
            proveedor['direccion'] = request.json['direccion']
            proveedor['productos'] = request.json['productos']
            return jsonify({"mensaje": "Proveedor actualizado correctamente"})
    return jsonify({"error": "Proveedor no encontrado"}), 404

@app.route('/proveedores/eliminar/<id>', methods=['DELETE'])
def eliminar_proveedor(id):
    global proveedores
    proveedores = [p for p in proveedores if p['id'] != id]
    return jsonify({"mensaje": "Proveedor eliminado"})

if __name__ == '__main__':
    app.run(debug=True)
