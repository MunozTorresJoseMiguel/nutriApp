from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)

