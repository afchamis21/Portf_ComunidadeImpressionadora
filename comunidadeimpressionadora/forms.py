from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidadeimpressionadora.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Digite o Usuário', validators=[DataRequired()])
    email = StringField('Digite o E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Digite a Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criar_conta = SubmitField('Criar Conta')

    def validate_email(self, email):
        user_exists = Usuario.query.filter_by(email=email.data).first()
        if user_exists:
            raise ValidationError('E-mail já cadastrado')


class FormLogin(FlaskForm):
    email_login = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username = StringField('Digite o Usuário', validators=[DataRequired()])
    email = StringField('Digite o E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])

    curso_excel = BooleanField('Excel Impressionador')
    curso_vba = BooleanField('VBA Impressionador')
    curso_powerbi = BooleanField('Power BI Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_sql = BooleanField('SQL Impressionador')

    botao_submit_editar_perfil = SubmitField('Confirmar')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('E-mail já cadastrado')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post Aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')


class FormEditarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post Aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Editar Post')
