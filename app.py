from flask import Flask, render_template,redirect,request,url_for,flash,session

app = Flask(__name__)
app.config['SECRET_KEY']="Jose_Miguel7"
USUARIOS_REGISTRADOS ={
    'admin@gmail.com':{
        'password': 'admin123',
        'nombre':'Admistrador',
        'fecha_nacimineto':'2008-04-06'
    }    
}

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

@app.route('/imc')
def imc():
    return render_template('imc.html')

@app.route('/recetas')
def recetas():
    return render_template('recetas.html')

@app.route('/consejos')
def consejos():
    return render_template('consejos.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('index'))


@app.route("/sesion")
def sesion():
    return render_template("index.html")

@app.route("/otro")
def otro():
    return render_template("sesion.html")

@app.route("/validalogin", methods=['GET', 'POST'])
def validalogin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Por favor ingrese su correo y contraseña.', 'danger')
            return render_template('sesion.html')

        usuario = USUARIOS_REGISTRADOS.get(email)
        if not usuario:
            flash('Usuario no encontrado.', 'danger')
            return render_template('sesion.html')

        if password != usuario['password']:
            flash('Contraseña incorrecta.', 'danger')
            return render_template('sesion.html')

        
        session['usuario_email'] = email
        session['usuario_nombre'] = usuario['nombre']
        session['logueado'] = True
        flash(f'Bienvenido {usuario["nombre"]}!', 'success')
        return redirect(url_for('inicio'))

    
    return render_template('sesion.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    return render_template('registro.html')




if __name__ == '__main__':
    app.run(debug=True)

