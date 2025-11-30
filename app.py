from flask import Flask, render_template,redirect,request,url_for,flash,session
import requests
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config['SECRET_KEY']="Jose_Miguel7"
USUARIOS_REGISTRADOS ={
    'admin@gmail.com':{
        'password': 'admin123',
        'nombre':'Admistrador',
        'fecha_nacimineto':'2008-04-06'
    }    
}
API_KEY = "1cCX8y0wpTQRG1fpLyFdZHacgthjLhTdd3N127AA"
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

## CONFIGURACION MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB'] = 'usuarios_db'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)  

@app.route('/educacion', methods=['GET', 'POST'])
def educacion():
    return render_template('educacion.html', )

# Rutas de la aplicación que no requieren autenticación
@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

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
@app.route('/analizador', methods=['GET', 'POST'])
def analizador():
    detalles = []# lista
    totales = { #diccionario
        "calorias": 0,
        "proteina": 0,
        "carbohidratos": 0,
        "grasas": 0
    }
    receta_texto = ""
    if 'id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        receta_texto = request.form.get('receta', '').strip()

        if not receta_texto:
            flash("Escribe al menos un ingrediente para analizar.", "warning")
        else:
            lineas = [l.strip() for l in receta_texto.splitlines() if l.strip()]

            for linea in lineas:
                gramos = 100  
                texto_busqueda = linea

                partes = linea.split()
                if partes and partes[0].isdigit():
                    gramos = float(partes[0])
                    texto_busqueda = " ".join(partes[1:])  

                info = buscar_nutrientes_usda(texto_busqueda)

                if not info:
                    detalles.append({
                        "ingrediente": linea,
                        "encontrado": False
                    })
                    continue

                factor = gramos / 100.0

                cal = (info["calorias"] or 0) * factor
                prot = (info["proteina"] or 0) * factor
                carb = (info["carbohidratos"] or 0) * factor
                gra = (info["grasas"] or 0) * factor

                detalles.append({
                    "ingrediente": linea,
                    "nombre_mostrado": info["nombre_mostrado"],
                    "gramos": gramos,
                    "calorias": round(cal, 1),
                    "proteina": round(prot, 1),
                    "carbohidratos": round(carb, 1),
                    "grasas": round(gra, 1),
                    "encontrado": True
                })

                totales["calorias"] += cal
                totales["proteina"] += prot
                totales["carbohidratos"] += carb
                totales["grasas"] += gra

            for k in totales:
                totales[k] = round(totales[k], 1)

    return render_template(
        'analizador.html',
        detalles=detalles,
        totales=totales,
        receta_texto=receta_texto
    )

def buscar_nutrientes_usda(nombre_ingrediente):
    try:
        params = {
            "api_key": API_KEY,
            "query": nombre_ingrediente,
            "pageSize": 1
        }
        resp = requests.get(API_URL, params=params, timeout=5)

        if resp.status_code != 200:
            return None

        data = resp.json()
        foods = data.get("foods", [])
        if not foods:
            return None

        food = foods[0]   
        descripcion = food.get("description", nombre_ingrediente)

        # Nutrientes
        calorias = proteina = carbohidratos = grasas = None

        for n in food.get("foodNutrients", []):
            nombre_n = n.get("nutrientName", "").lower()
            valor = n.get("value", 0)

            if "energy" in nombre_n or "kilocalories" in nombre_n:
                calorias = valor
            elif "protein" in nombre_n:
                proteina = valor
            elif "carbohydrate" in nombre_n:
                carbohidratos = valor
            elif "fat" in nombre_n or "lipid" in nombre_n:
                grasas = valor

        return {
            "nombre_mostrado": descripcion,
            "calorias": calorias,
            "proteina": proteina,
            "carbohidratos": carbohidratos,
            "grasas": grasas
        }

    except Exception as e:
        print("Error en buscar_nutrientes_usda:", e)
        return None


@app.route('/ver_perfil')
def ver_perfil():
    if 'id' not in session:
        flash('Debes iniciar sesión para ver tu perfil', 'warning')
        return redirect(url_for('login'))
    usuario = session.get('usuario', {})
    perfil = session.get('perfil', {})
    return render_template('ver_perfil.html', usuario=usuario, perfil=perfil)

@app.route("/rutina")
def rutina():
    rutina = {
        "nombre": "Full Body Básico",
        "nivel": "Principiante",
        "objetivo": "Tonificar y activar el cuerpo",
        "duracion": "30 minutos",
        "descripcion": "Rutina perfecta para comenzar. No necesitas equipo.",
        "ejercicios": [
            "Sentadillas – 3x12",
            "Lagartijas – 3x8",
            "Plancha – 3x30s",
            "Saltos de tijera – 3x20",
            "Crunches – 3x15"
        ],
        "calorias": 280,
        "imagen": "/static/img/rutina.jpg"
    }

    return render_template("rutina.html", rutina=rutina)

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

        edad_db = None
        altura_db = None
        peso_db = None

        try:
            if edad:
                edad_db = int(edad)
                if edad_db < 18 or edad_db > 100:
                    errores.append("La edad debe estar entre 18 y 100.")
            if altura_cm:
                altura_db = int(altura_cm)
                if altura_db < 50 or altura_db > 250:
                    errores.append("La altura debe estar entre 50 y 250 cm.")
            if peso_kg:
                peso_db = float(peso_kg)
                if peso_db < 20 or peso_db > 400:
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

        usuario_existente = obtener_usuario_por_email(email)
        if usuario_existente:
            flash("Ese correo ya está registrado. Intenta con otro.", "danger")
            return render_template('registro.html'), 400

        try:
            cur = mysql.connection.cursor()
            password_hash = generate_password_hash(password)

            sql = """
                INSERT INTO usuarios (
                    nombre, apellidos, email, password,
                    edad, genero, altura_cm, peso_kg,
                    actividad, objetivo, goal_other
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                nombre,
                apellidos,
                email,
                password_hash,
                edad_db,
                genero or None,
                altura_db,
                peso_db,
                actividad or None,
                objetivo or None,
                goal_other or None
            ))
            mysql.connection.commit()
            nuevo_id = cur.lastrowid
            cur.close()
        except Exception as e:
            print("Error al insertar usuario:", e)
            flash("Ocurrió un error al registrar el usuario. Intenta de nuevo.", "danger")
            return render_template('registro.html'), 500

        session['id'] = nuevo_id
        session['usuario_nombre'] = nombre
        session['usuario_email'] = email

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

            
            if imc < 18.5:
                categoria = "Bajo peso"
            elif 18.5 <= imc < 24.9:
                categoria = "Peso normal"
            elif 25 <= imc < 29.9:
                categoria = "Sobrepeso"
            else:
                categoria = "Obesidad"

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
            else:
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
    info = None
  
    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']

            
            if sexo == 'masculino':
                tmb_valor = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
            else:
                tmb_valor = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

            resultado = round(tmb_valor, 2)

            info = {
                "titulo": "¿Para qué sirve la TMB?",
                "descripcion": (
                    "La Tasa Metabólica Basal (TMB) es la cantidad de calorías que tu cuerpo "
                    "necesita para funcionar en reposo absoluto. "
                    "Incluye procesos como respirar, mantener la temperatura corporal "
                    "y el funcionamiento de órganos vitales."
                ),
                "extra": "",
                "imagen": "img/tasabasal.webp"  
            }

            if sexo == "masculino":
                info["extra"] = "Tu cuerpo tiende a tener mayor masa muscular, lo cual aumenta ligeramente tu TMB."
            else:
                info["extra"] = "En mujeres la TMB suele ser más baja debido a diferencias hormonales y musculares."

        except:
            resultado = None
            info = None

    return render_template('tmb.html', resultado=resultado, info=info)

@app.route('/gct', methods=['GET', 'POST'])
def gct():
    gct = None
    info = None
    if 'id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Verificamos que todos los campos vengan llenos
        campos = ['peso', 'altura', 'edad', 'sexo', 'actividad']
        if all(k in request.form and request.form[k] for k in campos):
            try:
                peso = float(request.form['peso'])
                altura = float(request.form['altura'])
                edad = int(request.form['edad'])
                sexo = request.form['sexo']
                actividad = float(request.form['actividad'])

                # TMB con fórmula de Mifflin-St Jeor
                tmb = (10 * peso) + (6.25 * altura) - (5 * edad)
                if sexo == 'masculino':
                    tmb += 5
                else:
                    tmb -= 161

                
                gct = round(tmb * actividad, 2)

               
                info = {
                    "titulo": "¿Qué es el Gasto Calórico Total (GCT)?",
                    "descripcion": (
                        "El Gasto Calórico Total es la cantidad aproximada de calorías que tu cuerpo "
                        "necesita al día considerando tu metabolismo basal y tu nivel de actividad física. "
                        "Si consumes más calorías de las que marca tu GCT, tiendes a subir de peso; si "
                        "consumes menos, tiendes a bajarlo."
                    ),
                    "extra": (
                        "Usa este valor como referencia para ajustar tus objetivos: perder grasa, "
                        "mantener tu peso o ganar masa muscular, siempre acompañado de hábitos saludables."
                    ),
                    "imagen": "img/tasabasal.webp"  
                }

            except ValueError:
                flash("Verifica que peso, altura y edad sean números válidos.", "danger")
        else:
            flash("Por favor completa todos los campos.", "warning")

    return render_template('gct.html', gct=gct, info=info)

@app.route('/peso_ideal', methods=['GET', 'POST'])
def peso_ideal():
    peso_ideal = None
    info = None

    if request.method == 'POST':
        try:
            altura = float(request.form['altura'])
            edad = int(request.form['edad'])
            sexo = request.form['sexo']

            if sexo == 'masculino':
                peso_ideal_valor = (altura - 100) - ((altura - 150) / 4) + ((edad - 20) / 4)
            else:
                peso_ideal_valor = (altura - 100) - ((altura - 150) / 2.5) + ((edad - 20) / 6)
            peso_ideal = round(peso_ideal_valor, 2)

            info = {
                "titulo": "¿Qué es el Peso Ideal?",
                "descripcion": (
                    "El peso ideal es una estimación del peso que tu cuerpo debería tener según tu "
                    "altura, edad y sexo. No busca un cuerpo ‘perfecto’, sino un rango saludable que "
                    "ayude a reducir riesgos de enfermedades y mejorar tu bienestar general."
                ),
                "extra": (
                    "Este cálculo es una referencia. La composición corporal, músculo y grasa pueden "
                    "hacer que tu peso ideal real varíe ligeramente."
                ),
                "imagen": "img/pesoidea.webp"  
            }

        except:
            peso_ideal = "Error: verifica los datos ingresados."
            info = None

    return render_template('peso_ideal.html', peso_ideal=peso_ideal, info=info)


@app.route('/macronutrientes', methods=['GET', 'POST'])
def macronutrientes():
    macros = None
    info = None
    if 'id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        if all(k in request.form and request.form[k] for k in ['calorias', 'objetivo']):
            calorias = float(request.form['calorias'])
            objetivo = request.form['objetivo']

            
            if objetivo == 'mantener':
                calorias_totales = calorias
            elif objetivo == 'perder':
                calorias_totales = calorias * 0.85  
            else:  
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

            
            info = {
                "titulo": "¿Por qué son importantes los macronutrientes?",
                "descripcion": (
                    "Los macronutrientes son los nutrientes que tu cuerpo necesita en mayor cantidad: "
                    "proteínas, carbohidratos y grasas. Una buena distribución ayuda a tener energía, "
                    "mantener la masa muscular y regular hormonas y funciones vitales."
                ),
                "extra": "",
                "imagen": "img/macros.webp"  
            }

            if objetivo == 'mantener':
                info["extra"] = (
                    "Esta distribución está pensada para mantener tu peso actual con un equilibrio "
                    "entre energía y saciedad."
                )
            elif objetivo == 'perder':
                info["extra"] = (
                    "El ligero déficit calórico te ayuda a perder grasa de forma gradual, "
                    "manteniendo proteínas suficientes para cuidar tu masa muscular."
                )
            else:  
                info["extra"] = (
                    "El superávit calórico favorece la ganancia de masa muscular si lo combinas "
                    "con entrenamiento de fuerza."
                )

        else:
            macros = "Por favor completa todos los campos."
            info = None

    return render_template('macronutrientes.html', macros=macros, info=info)

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

    return render_template('indexforcalculadora.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Por favor ingrese email y contraseña', 'danger')
            return render_template('sesion.html')

        usuario = obtener_usuario_por_email(email)

        if usuario:
            if check_password_hash(usuario[3], password):
                session['id'] = usuario[0]
                session['usuario_nombre'] = usuario[1]
                session['usuario_email'] = usuario[2]

                flash(f'Bienvenido {usuario[1]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Contraseña incorrecta', 'danger')
        else:
            flash('El correo no está registrado', 'danger')

    return render_template('sesion.html')

@app.route('/dashboard')
def dashboard():
    if 'id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    return render_template('inicio.html')   

def obtener_usuario_por_email(email):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, nombre, email, password
        FROM usuarios
        WHERE email = %s
    """, (email,))
    usuario = cur.fetchone()
    cur.close()
    return usuario

if __name__ == '__main__':
    app.run(debug=True)

