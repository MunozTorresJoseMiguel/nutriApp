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

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

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

@app.route('/imc', methods=['GET', 'POST'])
def imc():
    resultado = None
    categoria = None

    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura']) / 100  # convertir a metros
            imc = peso / (altura ** 2)
            resultado = round(imc, 2)

            if imc < 18.5:
                categoria = "Bajo peso"
            elif 18.5 <= imc < 24.9:
                categoria = "Peso normal"
            elif 25 <= imc < 29.9:
                categoria = "Sobrepeso"
            else:
                categoria = "Obesidad"
        except:
            resultado = "Error"
            categoria = "Verifica los datos"

    return render_template('imc.html', resultado=resultado, categoria=categoria)

@app.route('/tmb', methods=['GET', 'POST'])
def tmb():
    resultado = None
    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']

            # Fórmula de Mifflin-St Jeor
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
        # Verifica que todos los campos estén presentes y no vacíos
        if all(k in request.form and request.form[k] for k in ['peso', 'altura', 'edad', 'sexo', 'actividad']):
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']
            actividad = float(request.form['actividad'])

            # Fórmula de Mifflin-St Jeor
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad)
            if sexo == 'masculino':
                tmb += 5
            else:
                tmb -= 161

            # Cálculo del gasto calórico total
            gct = round(tmb * actividad, 2)
        else:
            gct = "Por favor completa todos los campos."

    return render_template('gct.html', gct=gct)

@app.route('/peso_ideal', methods=['GET', 'POST'])
def peso_ideal():
    peso_ideal = None
    if request.method == 'POST':
        # Validar que todos los campos estén completos
        if all(k in request.form and request.form[k] for k in ['altura', 'edad', 'sexo']):
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']

            # Fórmula de Lorentz (considera altura, sexo y edad)
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

            # Ajuste calórico según objetivo
            if objetivo == 'mantener':
                calorias_totales = calorias
            elif objetivo == 'perder':
                calorias_totales = calorias * 0.85  # -15%
            else:  # ganar
                calorias_totales = calorias * 1.15  # +15%

            # Distribución típica (en porcentaje)
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

@app.route('/analizador', methods=['GET', 'POST'])
def analizador():
    resultado = None
    if request.method == 'POST':
        receta = request.form.get('receta', '').strip().lower()

        # Pequeña base de datos simulada (por 100 g o unidad aprox)
        alimentos = {
            'pollo': {'calorias': 165, 'proteinas': 31, 'carbohidratos': 0, 'grasas': 3.6},
            'arroz': {'calorias': 130, 'proteinas': 2.7, 'carbohidratos': 28, 'grasas': 0.3},
            'huevo': {'calorias': 155, 'proteinas': 13, 'carbohidratos': 1.1, 'grasas': 11},
            'aguacate': {'calorias': 160, 'proteinas': 2, 'carbohidratos': 9, 'grasas': 15},
            'pan': {'calorias': 265, 'proteinas': 9, 'carbohidratos': 49, 'grasas': 3.2},
            'manzana': {'calorias': 52, 'proteinas': 0.3, 'carbohidratos': 14, 'grasas': 0.2},
            'queso': {'calorias': 402, 'proteinas': 25, 'carbohidratos': 1.3, 'grasas': 33},
            'pasta': {'calorias': 131, 'proteinas': 5, 'carbohidratos': 25, 'grasas': 1.1}
        }

        # Separar los ingredientes escritos por el usuario
        ingredientes = [i.strip() for i in receta.split(',') if i.strip()]
        if ingredientes:
            total = {'calorias': 0, 'proteinas': 0, 'carbohidratos': 0, 'grasas': 0}
            encontrados = []

            for ing in ingredientes:
                if ing in alimentos:
                    for k in total:
                        total[k] += alimentos[ing][k]
                    encontrados.append(ing)

            if encontrados:
                resultado = {
                    'ingredientes': ', '.join(encontrados),
                    'calorias': round(total['calorias'], 1),
                    'proteinas': round(total['proteinas'], 1),
                    'carbohidratos': round(total['carbohidratos'], 1),
                    'grasas': round(total['grasas'], 1)
                }
            else:
                resultado = "No se reconocieron los ingredientes. Intenta con: pollo, arroz, huevo, etc."
        else:
            resultado = "Por favor, escribe al menos un ingrediente."

    return render_template('analizador.html', resultado=resultado)




if __name__ == '__main__':
    app.run(debug=True)

