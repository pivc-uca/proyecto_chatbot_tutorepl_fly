# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from modelos import Usuarios

class RegistroForm(FlaskForm):
    nombres = StringField('Nombres', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    usuario = StringField('Usuario', validators=[DataRequired()])
    correo = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    clave = PasswordField('Contraseña', validators=[DataRequired()])
    confirmar_clave = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('clave')])
    rol = SelectField('Rol', choices=[('estudiante', 'Estudiante'), ('profesor', 'Profesor')], validators=[DataRequired()])
    submit = SubmitField('Registrar')

    def validate_username(self, usuario):
        user = Usuarios.query.filter_by(usuario=usuario.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso. Por favor, elige uno diferente.')

    def validate_email(self, correo):
        user = Usuarios.query.filter_by(correo=correo.data).first()
        if user:
            raise ValidationError('Ese correo electrónico ya está registrado. Por favor, elige uno diferente.')

class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    clave = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')