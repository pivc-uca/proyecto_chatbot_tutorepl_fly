# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, g
from basedatos import db, init_db, create_tables
from modelos import Usuarios, Historial # archivo modelos.py
from formularios import RegistroForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import os
import socketio
import requests
import json
from datetime import datetime # Asegúrate de importar datetime para el default value si es necesario
from groq import Groq
from flask_cors import CORS

app = Flask(__name__)
# Esto permite que CUALQUIER máquina externa use tu URL de ngrok
CORS(app)

app.config['SECRET_KEY'] = os.urandom(24) # Necesario para Flask-WTF y sesiones seguras

# Inicializa la base de datos
init_db(app) #

# Configura Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # La ruta a la que redirigir si el usuario no está logueado

# Configura tu cliente con la API Key
API_KEY_GROQ = os.getenv("API_KEY_GROQIA")
# Cliente Groq 
client = Groq(api_key=API_KEY_GROQ)
            
RASA_URL = os.getenv("RASA_SERVER_URL") 

@login_manager.user_loader
def load_user(user_id):
    #return Usuarios.query.get(int(user_id))
    return db.session.get(Usuarios, int(user_id))

# --- Rutas ---

@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        if current_user.rol == 'estudiante':
            return redirect(url_for('estudiante_pagina'))
        elif current_user.rol == 'profesor':
            return redirect(url_for('profesor_pagina'))
    return render_template('login.html', form=LoginForm()) # Redirige al login si no está autenticado

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # Si ya está logueado, redirigir a la página principal

    form = RegistroForm()
    if form.validate_on_submit():
        user = Usuarios(
            usuario=form.usuario.data,
            correo=form.correo.data,
            rol=form.rol.data,
            nombres=form.nombres.data,
            apellidos=form.apellidos.data
        )
        user.set_password(form.clave.data)
        db.session.add(user)
        db.session.commit()
        
        # Guardar historial registro nuevo usuario
        registro_his = Historial( id_usu=user.id_usu, actividad="Usuario registrado") 
        db.session.add(registro_his) 
        db.session.commit()        
        
        flash('¡Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(usuario=form.usuario.data).first()
        if user and user.check_password(form.clave.data):
            login_user(user)
            
            # Guardar historial inicio sesion
            registro = Historial( id_usu=user.id_usu, actividad="Inicio de sesión") 
            db.session.add(registro) 
            db.session.commit()  
            
            flash('¡Has iniciado sesión exitosamente!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Inicio de sesión fallido. Por favor, verifica tu nombre de usuario y contraseña.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Guardar historial cerrar sesion
    registro_hist = Historial( id_usu=current_user.id_usu, actividad="Cerrar de sesión") 
    db.session.add(registro_hist) 
    db.session.commit()
    
    logout_user()
     
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

@app.route('/estudiante_pagina')
@login_required
def estudiante_pagina():
    if current_user.rol != 'estudiante':
        flash('Acceso denegado. No tienes permisos de estudiante.', 'danger')
        return redirect(url_for('index'))
    return render_template('estudiante.html', user=current_user)

@app.route('/profesor_pagina')
@login_required
def profesor_pagina():
    if current_user.rol != 'profesor':
        flash('Acceso denegado. No tienes permisos de profesor.', 'danger')
        return redirect(url_for('index'))
    return render_template('profesor.html', user=current_user)
    
@app.route('/api/guardar_historial', methods=['POST'])
def guardar_historial():
    data = request.get_json() # Obtiene los datos JSON enviados desde el frontend

    if not data:
        return jsonify({"message": "No se recibieron datos JSON"}), 400

    user_id = data.get('user_id')
    actividad = data.get('actividad')

    if not user_id or not actividad:
        return jsonify({"message": "Faltan datos requeridos (user_id, actividad)"}), 400

    try:
        # Asegúrate de que el user_id exista para la ForeignKey
        # Usamos User.query.get(user_id) si user_id es la clave primaria.
        # Si usas current_user.id en el frontend, no necesitas buscar el usuario aquí.
        #user_exists = Usuarios.query.get(user_id) 
        user_exists = db.session.get(Usuarios, int(user_id))
        if not user_exists:
            return jsonify({"message": "El user_id proporcionado no existe."}), 404

        # Crear una nueva instancia del modelo Historial
        # ¡Ahora pasamos la actividad!
        nueva_seleccion = Historial(id_usu=user_id, actividad=actividad) #
        db.session.add(nueva_seleccion) #
        db.session.commit() #
        
        # Aquí puedes añadir un print o log para verificar que los datos llegaron
        print(f"DEBUG: Recibido historial para user_id={user_id}, actividad='{actividad}'")
        
        return jsonify({"message": "Historial guardado exitosamente",
                        "data": {"user_id": user_id, "actividad": actividad, "timestamp": nueva_seleccion.fecha.isoformat()}}), 200 #
        
    except Exception as e:
        db.session.rollback() # ¡Descomenta esto para deshacer transacciones en caso de error!
        return jsonify({"message": f"Error al guardar el historial: {str(e)}"}), 500
 
@app.route('/enviar-mensaje-rasa', methods=['POST'])
# @requerir_url
def enviar_mensaje_rasa():
    data = request.json
    sender_id = data.get("sender_id")
    message = data.get("message")
    
    print("Recibido desde frontend:", sender_id, message)

    if not sender_id or not message:
        return jsonify({"error": "Faltan datos"}), 400

    try:
            # response = requests.post("http://localhost:5005/webhooks/rest/webhook", json={
            # response = requests.post(f"{g.rasa_url}/webhooks/rest/webhook", json={
            response = requests.post(f"{RASA_URL}/webhooks/rest/webhook", json={
                "sender": sender_id,
                "message": message
            })

            if response.status_code == 200:
                return jsonify({"status": "ok", "respuesta_rasa": response.json()})
            else:
                return jsonify({"error": "Error desde Rasa", "status_code": response.status_code}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
        
@app.route('/chatbot/message', methods=['POST'])
# @requerir_url
def chatbot_message():
    user_message = request.json.get("message")
    # rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    # response = requests.post(f"{g.rasa_url}/webhooks/rest/webhook", json={"sender": "student", "message": user_message})
    response = requests.post(f"{RASA_URL}/webhooks/rest/webhook", json={"sender": "student", "message": user_message})
    # response = requests.post(rasa_url, json={"sender": "student", "message": user_message})

    if response.status_code == 200:
        data = response.json()
        if data:
            return jsonify({"response": data[0]["text"]})
        else:
            return jsonify({"response": "No se obtuvo respuesta del chatbot."})
    return jsonify({"response": "Error al conectar con RASA."})
        
@app.route('/caso/<int:case_id>')
@login_required
def ver_caso(case_id):
    if case_id == 1:
        return render_template('caso1_detalle.html',
                           user=current_user)
    elif case_id == 2:
        return render_template('caso2_detalle.html',
                           user=current_user)

@app.route('/validar_extension')
# @requerir_url
@login_required
def validar_extension():
    case_id = request.args.get('case_id') # Obtiene el case_id de los parámetros de la URL
    student_name = request.args.get('student_name') # Obtiene el student_name
    
    print(f"DEBUG: Validar extension")

    # Renderiza la nueva plantilla, pasándole los datos
    return render_template('validar_extension.html', 
                               case_id=case_id, 
                               student_name=student_name,
                               extension_id="dlfnmjnmhljcjpcfnlobkghefcoojibc") # Tu ID                        

@app.route('/practica_epl')
# @requerir_url
@login_required
def practica_epl():
    case_id = request.args.get('case_id') # Obtiene el case_id de los parámetros de la URL
    student_name = request.args.get('student_name') # Obtiene el student_name
    
    print(f"DEBUG: Practica EPL, url RASA, {RASA_URL}")

    # Puedes añadir validación aquí para asegurarte de que los parámetros existen y son válidos
    if not case_id or not student_name:
        flash('Datos de práctica incompletos.', 'error')
        return redirect(url_for('estudiante_pagina'))

    # Renderiza la nueva plantilla, pasándole los datos
    return render_template('practica_epl.html',
                           case_id=case_id,
                           student_name=student_name,
                           user=current_user, # Pasa el current_user también si lo necesitas en la plantilla
                           rasa_url=RASA_URL) # Pasamos la ruta URL
                          
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "")

        if not user_prompt:
            return jsonify({"error": "No se recibió ningún prompt."}), 400

        # Llamada al modelo Llama 3
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un experto en EPL. Tu objetivo es ayudar a los estudiantes a practicar EPL utilizando la plataforma Espertech EPL OnLine. Responde de manera clara, concisa y siempre como un tutor experto en EPL. Siempre mantente en el contexto de EPL"},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Validar que la respuesta tenga contenido 
        if not completion.choices: return jsonify({"error": "Groq no devolvió respuesta"}), 500        
        
        respuesta = completion.choices[0].message.content

        return jsonify({"response": respuesta})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/historial')
@login_required
def ver_historial():
    if current_user.rol != 'profesor':
        flash('Acceso denegado. Solo los profesores pueden ver el historial.', 'danger')
        return redirect(url_for('index'))

    # Obtener historial con JOIN para mostrar nombres del usuario
    historial = (
    db.session.query(
        Historial,
        Usuarios.nombres,
        Usuarios.apellidos
    )
    .join(Usuarios, Historial.id_usu == Usuarios.id_usu)
    .filter(Usuarios.rol == "estudiante")
    .order_by(Historial.id_usu, Historial.id_his.desc())
    .all()
)


    return render_template('historial.html', historial=historial)
              

if __name__ == '__main__':
    
    # IMPORTANTE: host='0.0.0.0' permite conexiones externas
    app.run(host='0.0.0.0', port=port)

    with app.app_context():
        create_tables(app) # Asegura que las tablas se creen al iniciar la app
    app.run(debug=True) # debug=True recarga el servidor automáticamente con los cambios y muestra errores

    