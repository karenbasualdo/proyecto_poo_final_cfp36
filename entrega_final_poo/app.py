from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "sakura13sql"
app.config["MYSQL_DB"] = "cafeteria_online_retiro"

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('listado'))
# Registro de cliente haber si funciona
@app.route('/registrar', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'GET':
            return render_template('registro_cliente.html')
        elif request.method == 'POST':
            Cliente= request.form['id_cliente']
            Nombre = request.form['nombre']
            Apellido = request.form['apellido']
            Email = request.form['email']
            Telefono = request.form['telefono']
            Direccion = request.form['direccion']
            barrio = request.form['barrio']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO clientes (id_cliente, nombre, apellido, email, telefono, direccion, barrio) VALUES (%s, %s, %s, %s, %s, %s, %s)', (Cliente, Nombre, Apellido, Email, Telefono, Direccion, barrio))
            mysql.connection.commit()
        #  Redirigir a la página de registro de producto
            return redirect(url_for('listado_cliente'))
    except Exception as error:
        return f'Error al registrar el cliente: {error}'
#  registro de productos funciona
@app.route('/productos', methods=['GET', 'POST'])
def registro_producto():
    try:
        if request.method == 'GET':
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_tamanio, nombre_tamanio FROM tamanios")
            tamanios = cur.fetchall()
            cur.close()
            return render_template('productos.html', tamanios=tamanios)
        elif request.method == 'POST':
            Producto = request.form['id_producto']
            Nombre = request.form['nombre']
            Descripcion = request.form['descripcion']
            Precio = request.form['precio']
            Categoria = request.form['id_categoria']
            Tamanio = request.form['id_tamanio']   
            Stock = request.form['stock']
            cur = mysql.connection.cursor()
            cur.execute(
                '''INSERT INTO productos (id_producto, nombre, descripcion, precio, id_categoria, id_tamanio, stock)
                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (Producto, Nombre, Descripcion, Precio, Categoria, Tamanio, Stock))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('listado_productos'))

    except Exception as error:
        return f'Error al registrar el producto: {error}'


# ***********************prueba
@app.route('/agregar_orden_compra', methods=['GET', 'POST'])
def agregar_orden_compra():
    try:
        cur = mysql.connection.cursor()
        # Traer pedidos y productos para mostrar en el formulario
        cur.execute("SELECT id_pedido FROM pedidos")
        pedidos = cur.fetchall()
        cur.execute("SELECT id_producto, nombre FROM productos")
        productos = cur.fetchall()

        if request.method == 'POST':
            id_pedido = request.form['id_pedido']
            id_producto = request.form['id_producto']
            cantidad = int(request.form['cantidad'])
            
            # Obtener precio del producto para calcular subtotal
            cur.execute("SELECT precio FROM productos WHERE id_producto = %s", (id_producto,))
            precio = cur.fetchone()[0]
            subtotal = precio * cantidad

            cur.execute('''INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, subtotal)
                        VALUES (%s, %s, %s, %s)''',
                        (id_pedido, id_producto, cantidad, subtotal))
            mysql.connection.commit()
            return redirect(url_for('listado_orden_compra'))
        else:
            return render_template('agregar_orden_compra.html', pedidos=pedidos, productos=productos)
    except Exception as e:
        return f"Error al agregar orden de compra: {e}"
# **********************

# ======================= CREAR PEDIDO ==========================


@app.route('/crear_pedido', methods=['GET', 'POST'])
def crear_pedido():
    try:
        cur = mysql.connection.cursor()

        # Traer clientes y empleados para el formulario
        cur.execute("SELECT id_cliente, nombre, apellido FROM clientes")
        clientes = cur.fetchall()

        cur.execute("SELECT id_empleado, nombre FROM empleados")
        empleados = cur.fetchall()

        # Fecha de hoy para el HTML
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        # Si solo mostramos el formulario
        if request.method == 'GET':
            return render_template(
                'registro_nuevo_pedido.html',
                clientes=clientes,
                empleados=empleados,
                fecha_hoy=fecha_hoy
            )

        # Si se envía el formulario (POST)
        elif request.method == 'POST':
            id_pedido = request.form['id_pedido']
            id_cliente = request.form['id_cliente']
            id_empleado = request.form['id_empleado']
            fecha = request.form['fecha']

            # Estado siempre "Pendiente"
            estado = "Pendiente"

            # Total empieza en 0
            total = 0

            cur.execute("""
                INSERT INTO pedidos (id_pedido, id_cliente, id_empleado, fecha, total, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_pedido, id_cliente, id_empleado, fecha, total, estado))

            mysql.connection.commit()
            cur.close()

            # 🔥 OPCIÓN 1: Volver al listado (flujo normal)
            return redirect(url_for('listado'))

            # 🔥 OPCIÓN 2: Ir directo a agregar productos (si querés este flujo)
            # return redirect(url_for('agregar_orden_compra', id_pedido=id_pedido))

    except Exception as error:
        return f"Error al crear pedido: {error}"





@app.route('/pago', methods=['GET', 'POST'])
def registro_pago():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_pedido, id_cliente FROM pedidos")
        pedidos = cur.fetchall()
        cur.execute("SELECT id_medio_pago, tipo, descripcion FROM medios_pago")
        medios_pago = cur.fetchall()
        if request.method == 'GET':
            return render_template('pago.html', pedidos=pedidos, medios_pago=medios_pago)
        elif request.method == 'POST':
            Pago = request.form['id_pago']
            Ppedido = request.form['id_pedido']
            Medio_pago = request.form['id_medio_pago']
            Monto = request.form['monto']
            Fecha_pago = request.form['fecha_pago']
            Estado_pago = request.form['estado_pago']
            cur.execute('''INSERT INTO pago (id_pago, id_pedido, id_medio_pago, monto, fecha_pago, estado_pago) VALUES (%s, %s, %s, %s, %s, %s)''', (Pago, Ppedido, Medio_pago, Monto, Fecha_pago, Estado_pago))
            mysql.connection.commit()
            return redirect(url_for('listado_pagos'))
    except Exception as e:
        return f"Error al registrar el pago: {e}"

# Listado de productos 
@app.route('/listado_productos')
def listado_productos():
    try:
        cur = mysql.connection.cursor()
        cur.execute('select * from productos')
        resultado = cur.fetchall()
        return render_template('listado_productos.html', datos=resultado)
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'  


# Listado de pedidos funciona
@app.route('/listado')
def listado():
    try:
        cur = mysql.connection.cursor()
        cur.execute('select * from pedidos')
        resultado = cur.fetchall()
        return render_template('listado.html', datos=resultado)
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'  

# listado pago corrobar
@app.route('/listado_pago')
def listado_pago():
    try:
        cur = mysql.connection.cursor()
        cur.execute('select * from pago')
        resultado = cur.fetchall()
        return render_template('listado_pago.html', datos=resultado)
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'  

# Listado de detalle pedidos para pedir 
@app.route('/listado_orden_compra')
def listado_orden_compra():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.id_detalle, d.id_pedido, p.nombre AS producto, d.cantidad, d.subtotal
            FROM detalle_pedido d
            JOIN productos p ON d.id_producto = p.id_producto
        """)
        resultado = cur.fetchall()
        return render_template('listado_orden_compra.html', datos=resultado)
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'


@app.route('/editar_producto/<id>')
def editar_producto(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cur.fetchone()

    cur.execute("SELECT id_tamanio, nombre_tamanio FROM tamanios")
    tamanios = cur.fetchall()

    return render_template('editar_producto.html', datos=producto, tamanios=tamanios)



# Edición de pedidos funciona
@app.route('/editar/<id>')
def obtenerDatos(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('select * from pedidos where id_pedido = "%s"'% (id))
        resultado = cur.fetchall()
        return render_template('editar.html', datos=resultado[0])
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'
    
# Listado de clientes  funciona
@app.route('/listado_clientes')
def listado_cliente():
    try:
        cur = mysql.connection.cursor()
        cur.execute('select * from clientes')
        resultado = cur.fetchall()
        return render_template('listado_cliente.html', datos=resultado)
    except Exception as error:
        return f'Error al conectar a la base de datos para listar cliente: {error}'  
    

    
# Edición de clientes mirar doble
@app.route('/editar_cliente/<id>')
def obtenerDatosCliente(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('select * from clientes where id_cliente = "%s"'% (id))
        resultado = cur.fetchall()
        return render_template('editar_cliente.html', datos=resultado[0])
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'


# ************************************prueba
@app.route('/editar_orden_compra/<id>', methods=['GET'])
def editar_orden_compra(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT d.id_detalle, d.id_pedido, p.nombre AS producto, d.cantidad, d.subtotal
            FROM detalle_pedido d
            JOIN productos p ON d.id_producto = p.id_producto
            WHERE d.id_detalle = %s
        """, (id,))
        detalle = cur.fetchone()
        return render_template('editar_orden_compra.html', datos={
            'id_detalle': detalle[0],
            'id_pedido': detalle[1],
            'producto': detalle[2],
            'cantidad': detalle[3],
            'subtotal': detalle[4]
        })
    except Exception as e:
        return f"Error al cargar orden de compra: {e}"

# ****************************





######ver mas tarde no sirve para pedido
@app.route('/eliminar/<string:id_pedido>')
def eliminar(id_pedido):
    try:
        cur = mysql.connection.cursor()
        cur.execute('Delete from pedidos where id_pedido = "{0}"'.format(id_pedido))
        mysql.connection.commit()
        return redirect(url_for('listado'))
    except Exception as error:
        return f'Error al conectar a la base de datos: {error}'

# eliminar cliente con confirmación
@app.route('/eliminar_cliente/<string:id_cliente>')
def eliminar_cliente(id_cliente):
    try:
        cur = mysql.connection.cursor()
        cur.execute('Delete from clientes WHERE id_cliente = "{0}"'.format( id_cliente))
        mysql.connection.commit()
        return redirect(url_for('listado_cliente'))
    except Exception as error:
        return f'Error al eliminar cliente: {error}'
#eliminar producto bien
@app.route('/eliminar_producto/<string:id_producto>')
def eliminar_producto(id_producto):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM productos WHERE id_producto = "{0}"'.format(id_producto))
        mysql.connection.commit()
        return redirect(url_for('listado_productos'))
    except Exception as error:
        return f"Error al eliminar producto: {error}"
# eliminaer orden de compra en proceso""*************************
@app.route('/eliminar_orden_compra/<string:id_detalle>')
def eliminar_orden_compra(id_detalle):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM detalle_pedido WHERE id_detalle = "{0}"'.format(id_detalle))
        mysql.connection.commit()
        return redirect(url_for('listado_orden_compra'))
    except Exception as error:
        return f"Error al eliminar producto: {error}"

# Actualizar pedido corriendo
@app.route('/actualizar/<id>', methods=['POST'])
def actualizar(id):
    try:
        if request.method == 'GET':
            return render_template('registro.html')
        elif request.method == 'POST':
            Cliente = request.form['id_cliente']
            Empleado = request.form['id_empleado']
            Fecha = request.form['fecha']
            Total = request.form['total']
            Estado = request.form['estado']
            cur = mysql.connection.cursor()
            cur.execute('''update pedidos set id_cliente = %s, id_empleado = %s, fecha = %s, total = %s,  estado = %s where id_pedido = %s''', (Cliente, Empleado, Fecha, Total, Estado, id))
            mysql.connection.commit()
            return redirect(url_for('listado'))

    except Exception as error:
        return f'Error de conexión con la base de datos: {error}'


# Actualizar clientemirar
@app.route('/actualizar_cliente/<id>', methods=['POST'])
def actualizar_cliente(id):
    try:
        Nombre = request.form['nombre']
        Apellido = request.form['apellido']
        Email = request.form['email']
        Telefono = request.form['telefono']
        Direccion = request.form['direccion']
        Barrio = request.form['barrio']
        cur = mysql.connection.cursor()
        sql = '''
            UPDATE clientes
            SET nombre = %s,
                apellido = %s,
                email = %s,
                telefono = %s,
                direccion = %s,
                barrio = %s
            WHERE id_cliente = %s
        '''
        cur.execute(sql, (Nombre, Apellido, Email, Telefono, Direccion, Barrio, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('listado_cliente'))  

    except Exception as error:
        return f'Error de conexión con la base de datos al actualizar cliente: {error}'

@app.route('/actualizar_productos/<id>', methods=['POST'])
def actualizar_productos(id):
    try:
        Nombre = request.form['nombre']
        Descripcion = request.form['descripcion']
        Precio = request.form['precio']
        Categoria = request.form['id_categoria']
        Tamanio = request.form['id_tamanio']   
        Stock = request.form['stock']
        cur = mysql.connection.cursor()
        cur.execute('''
        UPDATE productos
        SET nombre = %s,
            descripcion = %s,
            precio = %s,
            id_categoria = %s,
            id_tamanio = %s,
            stock = %s
        WHERE id_producto = %s 
        ''', (Nombre, Descripcion, Precio, Categoria, Tamanio, Stock, id))
        mysql.connection.commit()
        return redirect(url_for('listado_productos'))

    except Exception as error:
        return f'Error de conexión con la base de datos: {error}'

# *************************** prueba
@app.route('/actualizar_orden_compra/<id_detalle>', methods=['POST'])
def actualizar_orden_compra(id_detalle):
    cantidad = request.form['cantidad']

    conexion = get_db()
    cursor = conexion.cursor()

    # 1️⃣ Obtener precio y el id del pedido
    cursor.execute("""
        SELECT precio, id_pedido
        FROM detalle_pedido
        WHERE id_detalle = %s
    """, (id_detalle,))
    precio, id_pedido = cursor.fetchone()

    # 2️⃣ Calcular nuevo subtotal
    nuevo_subtotal = float(precio) * int(cantidad)

    # 3️⃣ Actualizar el detalle
    cursor.execute("""
        UPDATE detalle_pedido
        SET cantidad = %s, subtotal = %s
        WHERE id_detalle = %s
    """, (cantidad, nuevo_subtotal, id_detalle))

    # 4️⃣ Recalcular el total SOLO DEL PEDIDO ACTUAL
    cursor.execute("""
        UPDATE pedidos
        SET total = (
            SELECT SUM(subtotal)
            FROM detalle_pedido
            WHERE id_pedido = %s
        )
        WHERE id_pedido = %s
    """, (id_pedido, id_pedido))

    conexion.commit()
    return redirect(url_for('listado_orden_compra'))

# ****************************


if __name__ == '__main__':
    app.run(debug=True)

