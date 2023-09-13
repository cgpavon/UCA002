from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
import pyodbc
import os

app = Flask(__name__)

CORS(app)

# Cadena de conexión
cadena_conexion = "DRIVER={ODBC Driver 17 for SQL Server};Server=.\SQLEXPRESS;Database=master;UID=Mazazo;PWD=Clave52;"
conexion = pyodbc.connect(cadena_conexion)
cursor = conexion.cursor()


# Función para obtener un producto por ID
def obtener_producto_por_id(id_producto):
    cursor.execute('SELECT * FROM Productos WHERE ID = ?', id_producto)
    fila = cursor.fetchone()
    if fila:
        producto = {
            'ID': fila.ID,
            'Descripcion': fila.Descripcion,
            'Precio': fila.Precio,
            'Cantidad': fila.Cantidad
        }
        return producto
    return None

# Ruta para obtener la página defaul (en general se la llama Index.HTML)
@app.route('/')
def index():
    return render_template('Index.html')

# Ruta para obtener todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        cursor.execute('SELECT * FROM Productos')
        productos = []
        for fila in cursor.fetchall():
            producto = {
                'ID': fila.ID,
                'Descripcion': fila.Descripcion,
                'Precio': fila.Precio,
                'Cantidad': fila.Cantidad
            }
            productos.append(producto)
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': 'Error al obtener los productos: ' + str(e)}), 500

# Ruta para obtener un producto por ID
@app.route('/productos/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    try:
        producto = obtener_producto_por_id(id_producto)
        if producto:
            return jsonify(producto)
        return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': 'Error al obtener el producto: ' + str(e)}), 500

# Ruta para agregar un nuevo producto
@app.route('/productos', methods=['POST'])
def agregar_producto():
    try:
        nuevo_producto = request.json
        cursor.execute('INSERT INTO Productos (ID, Descripcion, Precio, Cantidad) VALUES (?, ?, ?, ?)',
                       nuevo_producto['ID'], nuevo_producto['Descripcion'], nuevo_producto['Precio'], nuevo_producto['Cantidad'])
        conexion.commit()
        return jsonify({'mensaje': 'Producto XXXXXXXXXXXX agregado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': 'Error al agregar el producto: ' + str(e)}), 500

# Ruta para actualizar un producto por ID
@app.route('/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    try:
        producto_actualizado = request.json
        cursor.execute('UPDATE Productos SET Descripcion=?, Precio=?, Cantidad=? WHERE ID=?',
                       producto_actualizado['Descripcion'], producto_actualizado['Precio'], producto_actualizado['Cantidad'], id_producto)
        conexion.commit()
        return jsonify({'mensaje': 'Producto actualizado correctamente'})
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el producto: ' + str(e)}), 500

# Ruta para eliminar un producto por ID
@app.route('/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    try:
        producto = obtener_producto_por_id(id_producto)
        if producto:
            cursor.execute('DELETE FROM Productos WHERE ID = ?', id_producto)
            conexion.commit()
            return jsonify({'mensaje': 'Producto eliminado correctamente'})
        return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': 'Error al eliminar el producto: ' + str(e)}), 500

# Ruta para alta masiva de productos
@app.route('/productos/alta-masiva', methods=['POST'])
def alta_masiva_productos():
    try:
        productos_nuevos = request.json
        for nuevo_producto in productos_nuevos:
            cursor.execute('INSERT INTO Productos (ID, Descripcion, Precio, Cantidad) VALUES (?, ?, ?, ?)',
                           nuevo_producto['ID'], nuevo_producto['Descripcion'], nuevo_producto['Precio'], nuevo_producto['Cantidad'])
        conexion.commit()
        return jsonify({'mensaje': 'Alta masiva de productos exitosa'}), 201
    except Exception as e:
        return jsonify({'error': 'Error en la alta masiva de productos: ' + str(e)}), 500

@app.route('/get_imagenes', methods=['GET'])
def get_imagenes():
    archivos_Img = os.listdir('img')
    img_Urls = [f'/img/{img}' for img in archivos_Img]
#    img_Urls = []
#    for img in archivos_Img:
#        img_dict = {"imagen": f'/img/{img}'}
#        img_Urls.append(img_dict)
    return jsonify(img_Urls)

@app.route('/get_imagenes/<nombre>', methods=['GET'])
def get_imagen(nombre):
    try:
        # Construye la ruta completa al archivo de imagen
        ruta_imagen = '/img/' + nombre
        # Utiliza send_from_directory para enviar la imagen al cliente
        return send_from_directory('/img/', nombre)
    except Exception as e:
        # En caso de error, devuelve una respuesta de error con un mensaje
        mensaje_error = "Error al obtener la imagen: " + str(e)
        return Response(mensaje_error, status=500)
    return send_from_directory('/img/', nombre)


if __name__ == '__main__':
    app.run(debug=True, port=4500)