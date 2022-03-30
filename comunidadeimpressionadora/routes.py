import flask_bcrypt
from flask import render_template, redirect, url_for, flash, request, abort
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost, FormEditarPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
from time import sleep
import secrets
import os

@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_criarconta.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login Realizado Com Sucesso no email {form_login.email_login.data}', 'alert-success')
            par_next = request.args.get('next')

            if par_next:
                return redirect(par_next)

            return redirect(url_for('home'))
        else:
            flash('E-mail ou Senha inválidos', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criar_conta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta Criada Com Sucesso no Email {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))

    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout realizado com sucesso', 'alert-success')
    return redirect(url_for('home'))


def quantidade_cursos(user: current_user):
    lista_cursos = user.cursos.split(';')
    if 'Não Informado' in lista_cursos:
        return 0, lista_cursos

    return len(lista_cursos), lista_cursos


@app.route('/perfil')
@login_required
def perfil():
    num_cursos, cursos = quantidade_cursos(current_user)
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil, cursos=cursos, quantidade_cursos=num_cursos)


@app.route('/post/criar',  methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)


def salvar_imagem(imagem, imagem_antiga):
    if imagem_antiga != 'default.jpg':
        os.remove(os.path.join(app.root_path, 'static/fotos_perfil', imagem_antiga))

    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)

    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)

    return nome_arquivo


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    if not lista_cursos:
        lista_cursos.append('Não Informado')
    return ';'.join(lista_cursos)


@app.route('/perfil/editar',  methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    num_cursos, cursos = quantidade_cursos(current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data, current_user.foto_perfil)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash('Perfil Atualizado Com Sucesso', 'alert-success')
        return redirect(url_for('perfil'))

    if request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username

    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form, cursos=cursos, quantidade_cursos=num_cursos)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    form = None

    if current_user == post.autor:
        form = FormEditarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))

    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído com Sucesso', 'alert-danger')
        return redirect(url_for('home'))

    abort(403)
