from flask import Flask, render_template,redirect,request,url_for,flash,session
import requests

app = Flask(__name__)
app.config['SECRET_KEY']="Jose_Miguel7"
USUARIOS_REGISTRADOS ={
    'admin@gmail.com':{
        'password': 'admin123',
        'nombre':'Admistrador',
        'fecha_nacimineto':'2008-04-06'
    }    
}

@app.route('/analizador', methods=['GET', 'POST'])
def analizador():
    
    return render_template('analizador.html', )

# Rutas de la aplicación que no requieren autenticación
@app.route('/inicio')
def inicio():
    return render_template('inicio.html')


@app.route('/consejos')
def consejos():
    return render_template('consejos.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('inicio'))


@app.route("/sesion")
def sesion():
    return render_template("index.html")

@app.route("/otro")
def otro():
    return render_template("sesion.html")

@app.route('/')
def index():
    return render_template('inicio.html')



#Las sieguentes rutas tiene metodo POST y GET 
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

        # 🔴 AQUÍ ES LO IMPORTANTE:
        session['usuario'] = {
            'nombre': usuario['nombre'],
            'email': email
        }
        flash(f'Bienvenido {usuario["nombre"]}!', 'success')
        return redirect(url_for('inicio'))

    return render_template('sesion.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
    
        nombre           = request.form.get('nombre', '').strip()
        apellidos        = request.form.get('apellidos', '').strip()
        email            = request.form.get('email', '').strip()
        password         = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        edad       = request.form.get('edad', '').strip()
        genero     = request.form.get('genero', '').strip()
        altura_cm  = request.form.get('altura_cm', '').strip()
        peso_kg    = request.form.get('peso_kg', '').strip()
        actividad  = request.form.get('actividad', '').strip()
        objetivo   = request.form.get('objetivo', '').strip()
        goals_sel  = request.form.getlist('goals')
        goal_other = request.form.get('goal_other', '').strip()

        errores = []
        if not nombre or not apellidos or not email:
            errores.append("Nombre, apellidos y correo son obligatorios.")
        if '@' not in email:
            errores.append("El correo electrónico no es válido.")
        if len(password) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres.")
        if password != confirm_password:
            errores.append("Las contraseñas no coinciden.")

        try:
            if edad:
                edad_i = int(edad)
                if edad_i < 18 or edad_i > 100:
                    errores.append("La edad debe estar entre 18 y 100.")
            if altura_cm:
                alt_i = int(altura_cm)
                if alt_i < 50 or alt_i > 250:
                    errores.append("La altura debe estar entre 50 y 250 cm.")
            if peso_kg:
                peso_f = float(peso_kg)
                if peso_f < 20 or peso_f > 400:
                    errores.append("El peso debe estar entre 20 y 400 kg.")
        except ValueError:
            errores.append("Verifica que edad, altura y peso sean números válidos.")

        if not actividad:
            errores.append("Selecciona tu nivel de actividad física.")
        if not objetivo:
            errores.append("Selecciona un objetivo nutricional.")

       
        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('registro.html'), 400 

        
        session['usuario'] = {
            'nombre': nombre, 'apellidos': apellidos, 'email': email,
            'edad': edad, 'genero': genero, 'altura_cm': altura_cm, 'peso_kg': peso_kg,
            'actividad': actividad, 'objetivo': objetivo,
            'goals': goals_sel, 'goal_other': goal_other
        }
        flash("Registro exitoso 🎉 Ahora completa tu perfil.", "success")
        return redirect(url_for('perfil')) 

    return render_template('registro.html')

@app.route('/imc', methods=['GET', 'POST'])
def imc():
    resultado = None
    categoria = None
    info = None

    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura']) / 100  
            imc = peso / (altura ** 2)
            resultado = round(imc, 2)

            # Clasificación del IMC
            if imc < 18.5:
                categoria = "Bajo peso"
            elif 18.5 <= imc < 24.9:
                categoria = "Peso normal"
            elif 25 <= imc < 29.9:
                categoria = "Sobrepeso"
            else:
                categoria = "Obesidad"

            # Información nutricional
            info = {
                "titulo": "¿Para qué sirve el IMC?",
                "descripcion": (
                    "El IMC (Índice de Masa Corporal) es una herramienta que ayuda a estimar si "
                    "tu peso está dentro de un rango saludable según tu estatura. No sustituye una "
                    "valoración médica, pero es una referencia rápida sobre tu estado nutricional."
                ),
                "extra": "",
                "imagen": "img/imc_info.png"
            }

            # Mensajes según categoría
            if categoria == "Bajo peso":
                info["extra"] = (
                    "Tu IMC indica bajo peso. Podrías necesitar aumentar tu ingesta calórica con "
                    "alimentos nutritivos y consultar a un profesional de la salud."
                )
            elif categoria == "Peso normal":
                info["extra"] = (
                    "Tu IMC está en un rango saludable. Mantén una alimentación equilibrada y "
                    "actividad física regular."
                )
            elif categoria == "Sobrepeso":
                info["extra"] = (
                    "Tu IMC indica sobrepeso. Podrías beneficiarte de mejorar tus hábitos de "
                    "alimentación y aumentar tu actividad física."
                )
            else:  # Obesidad
                info["extra"] = (
                    "Tu IMC entra en el rango de obesidad. Es recomendable acudir con un profesional "
                    "de la salud para una valoración más completa."
                )

        except Exception as e:
            resultado = "Error"
            categoria = "Verifica los datos"
            info = None

    return render_template('imc.html', resultado=resultado, categoria=categoria, info=info)


@app.route('/tmb', methods=['GET', 'POST'])
def tmb():
    resultado = None
    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']

            
            if sexo == 'masculino':
                tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
            else:
                tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

            resultado = round(tmb, 2)
        except:
            resultado = "Error. Verifica los datos ingresados."

    return render_template('tmb.html', resultado=resultado)

@app.route('/gct', methods=['GET', 'POST'])
def gct():
    gct = None
    if request.method == 'POST':
        
        if all(k in request.form and request.form[k] for k in ['peso', 'altura', 'edad', 'sexo', 'actividad']):
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']
            actividad = float(request.form['actividad'])

            
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad)
            if sexo == 'masculino':
                tmb += 5
            else:
                tmb -= 161

            
            gct = round(tmb * actividad, 2)
        else:
            gct = "Por favor completa todos los campos."

    return render_template('gct.html', gct=gct)

@app.route('/peso_ideal', methods=['GET', 'POST'])
def peso_ideal():
    peso_ideal = None
    if request.method == 'POST':
       
        if all(k in request.form and request.form[k] for k in ['altura', 'edad', 'sexo']):
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']

           
            if sexo == 'masculino':
                peso_ideal = (altura - 100) - ((altura - 150) / 4) + ((edad - 20) / 4)
            else:
                peso_ideal = (altura - 100) - ((altura - 150) / 2.5) + ((edad - 20) / 6)

            peso_ideal = round(peso_ideal, 2)
        else:
            peso_ideal = "Por favor completa todos los campos."

    return render_template('peso_ideal.html', peso_ideal=peso_ideal)

@app.route('/macronutrientes', methods=['GET', 'POST'])
def macronutrientes():
    macros = None
    if request.method == 'POST':
        if all(k in request.form and request.form[k] for k in ['calorias', 'objetivo']):
            calorias = float(request.form['calorias'])
            objetivo = request.form['objetivo']

            
            if objetivo == 'mantener':
                calorias_totales = calorias
            elif objetivo == 'perder':
                calorias_totales = calorias * 0.85  
            else:  # ganar
                calorias_totales = calorias * 1.15  

          
            proteinas = 0.25 * calorias_totales / 4
            carbohidratos = 0.50 * calorias_totales / 4
            grasas = 0.25 * calorias_totales / 9

            macros = {
                'calorias_totales': round(calorias_totales, 2),
                'proteinas': round(proteinas, 1),
                'carbohidratos': round(carbohidratos, 1),
                'grasas': round(grasas, 1)
            }
        else:
            macros = "Por favor completa todos los campos."

    return render_template('macronutrientes.html', macros=macros)

@app.route('/perfil', methods=['GET','POST'])
def perfil():
    if request.method == 'POST':
        alergias        = request.form.getlist('alergias')
        intolerancias   = request.form.getlist('intolerancias')
        dietas          = request.form.getlist('dietas')
        alergia_otra       = (request.form.get('alergia_otra','') or '').strip()
        no_gustan          = (request.form.get('no_gustan','') or '').strip()
        experiencia_cocina = (request.form.get('experiencia_cocina','') or '').strip()
        equipo_disponible  = (request.form.get('equipo_disponible','') or '').strip()

        errores = []
        if not experiencia_cocina:
            errores.append("Selecciona tu nivel de experiencia en cocina.")

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('perfil.html')

        session['perfil'] = {
            'alergias': alergias,
            'alergia_otra': alergia_otra,
            'intolerancias': intolerancias,
            'dietas': dietas,
            'no_gustan': no_gustan,
            'experiencia_cocina': experiencia_cocina,
            'equipo_disponible': equipo_disponible
        }
        flash("Perfil completado ✅", "success")
        return redirect(url_for('inicio'))

    return render_template('perfil.html')

@app.route('/indexforcalculadora', methods=['GET', 'POST'])
def calculadora():
   
    if 'usuario' not in session:
        flash("Debes iniciar sesión para usar la calculadora 🤓", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
       
        resultado = 0 
        return render_template('indexforcalculadora.html', resultado=resultado)

    return render_template('indexforcalculadora.html')






if __name__ == '__main__':
    app.run(debug=True)

