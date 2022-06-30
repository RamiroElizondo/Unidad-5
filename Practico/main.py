from datetime import datetime
from flask import Flask, request,render_template, session,url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib
from datetime import datetime



app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Usuario, Receta, Ingrediente
contador:int = 1

def aumentar():
    global contador
    contador = contador + 1

def reiniciar():
    global contador 
    contador = 0

@app.route("/")
def bienvenido():
    return render_template ("bienvenido.html")

@app.route("/inicio",methods=["POST","GET"])
def inicio():
    return render_template("inicio.html")

@app.route("/verificar",methods=["POST","GET"])
def verificar():
    if request.method == 'POST':
        if not request.form["correo"] or not request.form["clave"]:
            return render_template ("error.html")
        else:
            usuario_actual=Usuario.query.filter_by(correo=request.form["correo"]).first()
            if usuario_actual is None:
                return render_template ("error.html")
            else: 
                if usuario_actual and hashlib.md5(request.form['clave'].encode()).hexdigest() == usuario_actual.clave:
                    session['persona'] = usuario_actual.id
                    print(session['persona'])
                    return render_template("menu.html",user=usuario_actual)
                else:
                    return render_template("error.html")
    else:
        return render_template("error.html")

@app.route("/registro",methods=["POST","GET"])
def registro():
    return render_template("registro.html")


@app.route("/crear_cuenta",methods=["POST","GET"])
def crear_cuenta():
    if request.method == 'POST':
        if not request.form["correo"] or not request.form["clave"] or not request.form["nombre"]:
            return render_template ("error.html")
        elif Usuario.query.filter_by(correo=request.form["correo"]).first():
            return render_template ("registro.html")
        elif Usuario.query.filter_by(correo=request.form["nombre"]).first():
            return render_template ("registro.html")
        else:
            user = Usuario(
			nombre=request.form['nombre'],
			correo=request.form['correo'],
			clave=hashlib.md5(bytes(request.form['clave'], encoding='utf-8')).hexdigest()
            )
            db.session.add(user)
            db.session.commit()
            return render_template ("inicio.html")
    
    else:
        return render_template ("error.html")

@app.route("/receta",methods=["POST","GET"])
def receta():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    return render_template("receta.html",user=usuario,valor=None)

@app.route('/menu',methods=["POST","GET"])
def menu():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    return render_template("menu.html",user=usuario)

@app.route("/guardarreceta",methods=["POST","GET"])
def guardarreceta():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    if request.method == 'POST':
        if not request.form["nombreR"] or not request.form["elaboracion"] or not request.form["tiempo"]:
            return render_template ("error.html")
        receta = Receta(
            nombre=request.form['nombreR'],
            tiempo=int(request.form['tiempo']),
            elaboracion=request.form['elaboracion'],
            cantidadmegusta= 0,
            fecha= datetime.now(),
            usuarioid= usuario.id
        )
        #return redirect(url_for('receta'))
        db.session.add(receta)
        db.session.commit()
        session['receta'] = receta.id
        return render_template("ingredientes.html",user=usuario,contador=contador)
    else:
        return render_template("error.html")

@app.route("/guardaringrediente",methods=["POST","GET"])
def guardaringrediente():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    receta = Receta.query.filter_by(id=session['receta']).first()
    if request.method == 'POST':
        if not request.form["nombre"] or not request.form["cantidad"] or not request.form["unidad"]:
            return render_template ("error.html")
        ingrediente = Ingrediente(
            nombre = request.form['nombre'],
            cantidad = request.form['cantidad'],
            unidad = request.form['unidad'],
            recetaid= receta.id
        )
        db.session.add(ingrediente)
        db.session.commit()
        if contador <= 2:
            aumentar()
            return render_template('ingredientes.html',user=usuario,contador=contador)
        else: 
            reiniciar()
            return render_template('receta.html',user=usuario,valor='Entre')
    else:
        return render_template("error.html")

@app.route("/ranking",methods=["POST","GET"])
def ranking():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    receta=Receta.query.order_by(Receta.cantidadmegusta.desc()).all()
    return render_template("ranking.html",user=usuario,lista=receta[0:5])

@app.route("/consultar_tiempo",methods=["POST","GET"])
def consultar_tiempo():
    if request.method == 'GET':
        usuario=Usuario.query.filter_by(id=session['persona']).first()
        return render_template("consultar_tiempo.html",user=usuario,list=None)
    elif request.method == 'POST':
        lista=[]
        usuario=Usuario.query.filter_by(id=session['persona']).first()
        receta = Receta.query.all()
        if not request.form['tiempo']:
            return render_template('error.html')
        else:
            for elem in receta:
                if elem.tiempo <= int(request.form['tiempo']):
                    lista.append(elem)
        return render_template("consultar_tiempo.html",user=usuario,list=lista)

@app.route('/buscarelmostrar',methods=["POST","GET"])
def buscarelmostrar():
    if request.method == 'POST':
        user1= usuario=Usuario.query.filter_by(id=session['persona']).first()
        nombre = request.form['nombre']
        recetas = Receta.query.all()
        ingrediente = Ingrediente.query.all()
        receta = None
        listaI = []
        usuario = None
        for elem in recetas:
            if elem.nombre==nombre:
                receta = elem
                session['receta']=receta.id
                usuarioid = receta.usuarioid
                usuario=Usuario.query.filter_by(id=usuarioid).first()
                for elemI in ingrediente:
                    if elemI.recetaid == elem.id:
                        listaI.append(elemI)
        
        if receta == None:
            return render_template('error.html')
        else:
            return render_template('mostrarRUI.html',user1=user1,user=usuario,receta=receta,listaI=listaI)
    else:
        return render_template('error.html')
@app.route('/megusta',methods=["POST","GET"])
def megusta():
    if request.method == 'POST':
        receta = Receta.query.filter_by(id=session['receta']).first()
        usuarioActual = session['persona']
        if usuarioActual == receta.usuarioid:
            return render_template('error.html')
        else:
            if request.form['megusta'] == 'megusta':
                receta.cantidadmegusta = receta.cantidadmegusta + 1
                db.session.commit()
            return render_template('menu.html',user = session['persona'])
    else:
        return render_template('error.html')

@app.route("/consultar_ingrediente",methods=["POST","GET"])
def consultar_ingrediente():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    return render_template("consultar_ingrediente.html",user=usuario)

@app.route("/buscar_ingrediente",methods=["POST","GET"])
def buscar_ingrediente():
    usuario=Usuario.query.filter_by(id=session['persona']).first()
    if request.method == 'POST':
        if not request.form["ingrediente"]:
            return render_template ("error.html")
        else:
            #ingreso de ingredientes en lower tambien
            nombreIngrediente = request.form['ingrediente'].lower()
            recetas_filtradas = []

            for receta in Receta.query.all():
                for ingrediente in receta.ingrediente:
                    if nombreIngrediente in ingrediente.nombre.lower() and receta not in recetas_filtradas:
                        recetas_filtradas.append(receta)

            if nombreIngrediente is None:
                return render_template ("error.html")
            else: 
                return render_template("mostrar_ingrediente.html",user=usuario,lista=recetas_filtradas)
    else: 
        return render_template ("error.html")

if __name__== "__main__":
    db.create_all
    app.run(debug = True)