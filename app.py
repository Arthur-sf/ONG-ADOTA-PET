"""Projeto 4: ONG de adoção de pets. Flask + MySQL + Leaflet."""
import os
from functools import wraps
from urllib.parse import urlparse, unquote
from decimal import Decimal
from datetime import date, datetime

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import Swagger

load_dotenv()
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'CHAVE_APENAS_PARA_DESENVOLVIMENTO'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
    MAX_CONTENT_LENGTH=1024 * 1024,
)
Swagger(app, template={'info': {'title': 'API ONG Adoção de Pets', 'version': '1.0', 'description': 'Rotas do Projeto 4'}})


def conectar():
    endereco = os.getenv('DATABASE_URL')

    if not endereco:
        raise RuntimeError('Configure DATABASE_URL no arquivo .env')

    url = urlparse(endereco)

    config = dict(
        host=url.hostname,
        port=url.port or 3306,
        user=unquote(url.username or ''),
        password=unquote(url.password or ''),
        database=url.path.lstrip('/'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

    ca = os.getenv('DB_SSL_CA')

    if ca:
        config['ssl_ca'] = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ca
        )
        config['ssl_verify_cert'] = True
        config['ssl_verify_identity'] = True

    elif url.hostname.endswith('.aivencloud.com'):
        raise RuntimeError('Configure o certificado SSL do Aiven')

    return pymysql.connect(**config)


def executar(sql, params=(), *, um=False, escrita=False):
    conn = conectar()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            resultado = cur.lastrowid if escrita else (cur.fetchone() if um else cur.fetchall())
        if escrita:
            conn.commit()
        return resultado
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def json_pronto(obj):
    if isinstance(obj, dict):
        return {k: json_pronto(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_pronto(x) for x in obj]
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


def erro(mensagem, status=400):
    return jsonify(erro=mensagem), status


def dados_json():
    return request.get_json(silent=True) or {}


def usuario_atual():
    return session.get('usuario')


def exige_login(*perfis):
    def decorar(func):
        @wraps(func)
        def protegido(*args, **kwargs):
            u = usuario_atual()
            if not u:
                return erro('Faça login para continuar.', 401)
            if perfis and u['perfil'] not in perfis:
                return erro('Você não tem permissão.', 403)
            return func(*args, **kwargs)
        return protegido
    return decorar


def texto(d, campo, limite, obrigatorio=True):
    valor = str(d.get(campo, '') or '').strip()
    if (obrigatorio and not valor) or len(valor) > limite:
        raise ValueError(f'Campo {campo} inválido (máximo {limite} caracteres).')
    return valor


def booleano(d, campo):
    if d.get(campo) not in (True, False):
        raise ValueError(f'Campo {campo} deve ser verdadeiro ou falso.')
    return d[campo]


def validar_pet(d):
    p = {k: texto(d, k, tamanho, obrigatorio) for k, tamanho, obrigatorio in [
        ('nome', 100, True), ('especie', 100, True), ('raca', 100, False),
        ('porte', 30, True), ('sexo', 20, True), ('descricao', 500, True), ('cidade', 100, True)]}
    if p['porte'] not in ('Pequeno', 'Medio', 'Grande') or p['sexo'] not in ('Macho', 'Femea'):
        raise ValueError('Porte ou sexo inválido.')
    try:
        idade = int(d['idade_meses'])
        if idade < 0 or idade > 360:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ValueError('Informe a idade total em meses (0 a 360).')
    p['idade_meses'] = idade
    p['castrado'] = booleano(d, 'castrado')
    p['vacinado'] = booleano(d, 'vacinado')
    lat, lng = d.get('latitude'), d.get('longitude')
    if (lat in ('', None)) != (lng in ('', None)):
        raise ValueError('Informe latitude e longitude juntas.')
    if lat in ('', None):
        p['latitude'], p['longitude'] = None, None
    else:
        try:
            p['latitude'], p['longitude'] = float(lat), float(lng)
        except (TypeError, ValueError):
            raise ValueError('Coordenadas inválidas.')
        if not (-90 <= p['latitude'] <= 90 and -180 <= p['longitude'] <= 180):
            raise ValueError('Coordenadas fora do intervalo permitido.')
    return p


@app.errorhandler(pymysql.MySQLError)
def erro_banco(e):
    app.logger.exception('Falha no MySQL')
    return erro('Erro de conexão ou operação no banco de dados.', 503)


@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/health')
def health():
    executar('SELECT 1')
    return jsonify(status='ok')


@app.post('/api/usuarios')
def cadastrar():
    d = dados_json()
    try:
        nome = texto(d, 'nome', 250)
        email = texto(d, 'email', 250).lower()
        telefone = texto(d, 'telefone', 20)
        cidade = texto(d, 'cidade', 100)
        senha = str(d.get('senha', ''))
        perfil = d.get('perfil')
        if '@' not in email or len(senha) < 8 or len(senha) > 128:
            return erro('Informe e-mail válido e senha de 8 a 128 caracteres.')
        if perfil not in ('adotante', 'responsavel'):
            return erro('Perfil inválido. Administradores não podem se cadastrar publicamente.')
    except ValueError as e:
        return erro(str(e))
    try:
        uid = executar('INSERT INTO usuarios (nome,email,senha_hash,perfil,telefone,cidade) VALUES (%s,%s,%s,%s,%s,%s)',
                       (nome, email, generate_password_hash(senha), perfil, telefone, cidade), escrita=True)
    except pymysql.err.IntegrityError:
        return erro('E-mail já cadastrado.', 409)
    return jsonify(id=uid, nome=nome, perfil=perfil), 201


@app.post('/api/login')
def login():
    d = dados_json()
    email = str(d.get('email', '')).strip().lower()
    u = executar('SELECT id,nome,email,perfil,senha_hash FROM usuarios WHERE email=%s', (email,), um=True)
    if not u or not check_password_hash(u['senha_hash'], str(d.get('senha', ''))):
        return erro('E-mail ou senha incorretos.', 401)
    session.clear()
    session['usuario'] = {k: u[k] for k in ('id', 'nome', 'email', 'perfil')}
    return jsonify(usuario=session['usuario'])


@app.post('/api/logout')
@exige_login()
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get('/api/me')
def me():
    return jsonify(usuario=usuario_atual())


CAMPOS = 'id,responsavel_id,nome,especie,raca,porte,sexo,idade_meses,castrado,vacinado,descricao,cidade,latitude,longitude,status'


@app.get('/api/pets')
def listar_pets():
    filtros = ['status = %s']
    params = ['Disponivel']
    if request.args.get('todos') == '1':
        filtros, params = [], []
    for campo in ('especie', 'porte', 'cidade'):
        v = request.args.get(campo, '').strip()
        if v:
            filtros.append(f'{campo} = %s')
            params.append(v)
    idade = request.args.get('idade_max')
    if idade:
        try:
            idade = int(idade)
            if idade < 0:
                raise ValueError()
        except ValueError:
            return erro('Idade máxima inválida.')
        filtros.append('idade_meses <= %s')
        params.append(idade)
    where = (' WHERE ' + ' AND '.join(filtros)) if filtros else ''
    rows = executar(f'SELECT {CAMPOS} FROM pets{where} ORDER BY id DESC LIMIT 200', params)
    return jsonify(json_pronto(rows))


@app.get('/api/pets/<int:pet_id>')
def detalhe_pet(pet_id):
    p = executar(f'SELECT {CAMPOS} FROM pets WHERE id=%s', (pet_id,), um=True)
    return jsonify(json_pronto(p)) if p else erro('Pet não encontrado.', 404)


@app.post('/api/pets')
@exige_login('responsavel', 'administrador')
def criar_pet():
    try:
        p = validar_pet(dados_json())
    except ValueError as e:
        return erro(str(e))
    campos = list(p)
    sql = 'INSERT INTO pets (responsavel_id,' + ','.join(campos) + ') VALUES (%s,' + ','.join(['%s'] * len(campos)) + ')'
    pet_id = executar(sql, [usuario_atual()['id']] + [p[k] for k in campos], escrita=True)
    return jsonify(id=pet_id), 201


@app.put('/api/pets/<int:pet_id>')
@exige_login('responsavel', 'administrador')
def editar_pet(pet_id):
    existente = executar('SELECT responsavel_id,status FROM pets WHERE id=%s', (pet_id,), um=True)
    if not existente:
        return erro('Pet não encontrado.', 404)
    if existente['responsavel_id'] != usuario_atual()['id'] and usuario_atual()['perfil'] != 'administrador':
        return erro('Você não é responsável por este pet.', 403)
    if existente['status'] == 'Adotado':
        return erro('Pet adotado não pode ser editado.', 409)
    try:
        p = validar_pet(dados_json())
    except ValueError as e:
        return erro(str(e))
    campos = list(p)
    executar('UPDATE pets SET ' + ','.join(f'{c}=%s' for c in campos) + ' WHERE id=%s',
             [p[k] for k in campos] + [pet_id], escrita=True)
    return jsonify(ok=True)


@app.delete('/api/pets/<int:pet_id>')
@exige_login('responsavel', 'administrador')
def excluir_pet(pet_id):
    p = executar('SELECT responsavel_id FROM pets WHERE id=%s', (pet_id,), um=True)
    if not p:
        return erro('Pet não encontrado.', 404)
    if p['responsavel_id'] != usuario_atual()['id'] and usuario_atual()['perfil'] != 'administrador':
        return erro('Sem permissão.', 403)
    if executar('SELECT id FROM pedidos_adocao WHERE pet_id=%s LIMIT 1', (pet_id,), um=True):
        return erro('Não é possível excluir um pet com histórico de pedidos.', 409)
    executar('DELETE FROM pets WHERE id=%s', (pet_id,), escrita=True)
    return jsonify(ok=True)


@app.post('/api/pets/<int:pet_id>/pedidos')
@exige_login('adotante')
def solicitar(pet_id):
    d = dados_json()
    try:
        mensagem = texto(d, 'mensagem', 2000)
    except ValueError as e:
        return erro(str(e))
    pet = executar('SELECT status,responsavel_id FROM pets WHERE id=%s', (pet_id,), um=True)
    if not pet:
        return erro('Pet não encontrado.', 404)
    if pet['status'] != 'Disponivel':
        return erro('Pet indisponível para adoção.', 409)
    try:
        pid = executar('INSERT INTO pedidos_adocao (pet_id,adotante_id,mensagem) VALUES (%s,%s,%s)',
                       (pet_id, usuario_atual()['id'], mensagem), escrita=True)
    except pymysql.err.IntegrityError:
        return erro('Você já enviou um pedido para este pet.', 409)
    return jsonify(id=pid, status='Pendente'), 201


@app.get('/api/pedidos')
@exige_login()
def listar_pedidos():
    u = usuario_atual()
    if u['perfil'] == 'adotante':
        sql = 'SELECT pa.*,p.nome AS pet_nome FROM pedidos_adocao pa JOIN pets p ON p.id=pa.pet_id WHERE pa.adotante_id=%s ORDER BY pa.id DESC'
        params = (u['id'],)
    elif u['perfil'] == 'administrador':
        sql = 'SELECT pa.*,p.nome AS pet_nome FROM pedidos_adocao pa JOIN pets p ON p.id=pa.pet_id ORDER BY pa.id DESC LIMIT 200'
        params = ()
    else:
        sql = 'SELECT pa.*,p.nome AS pet_nome FROM pedidos_adocao pa JOIN pets p ON p.id=pa.pet_id WHERE p.responsavel_id=%s ORDER BY pa.id DESC'
        params = (u['id'],)
    return jsonify(json_pronto(executar(sql, params)))


@app.patch('/api/pedidos/<int:pedido_id>')
@exige_login('responsavel', 'administrador')
def decidir(pedido_id):
    novo = dados_json().get('status')
    if novo not in ('Aceito', 'Recusado'):
        return erro('Status deve ser Aceito ou Recusado.')
    conn = conectar()
    try:
        with conn.cursor() as cur:
            # Primeiro bloqueia o pet, para serializar decisões concorrentes.
            cur.execute('SELECT p.id,p.responsavel_id,p.status FROM pets p JOIN pedidos_adocao pa ON pa.pet_id=p.id WHERE pa.id=%s FOR UPDATE', (pedido_id,))
            pet = cur.fetchone()
            if not pet:
                return erro('Pedido não encontrado.', 404)
            if pet['responsavel_id'] != usuario_atual()['id'] and usuario_atual()['perfil'] != 'administrador':
                return erro('Sem permissão.', 403)
            cur.execute('SELECT id,status FROM pedidos_adocao WHERE id=%s FOR UPDATE', (pedido_id,))
            pedido = cur.fetchone()
            if pedido['status'] != 'Pendente' or pet['status'] == 'Adotado':
                return erro('Pedido já finalizado ou pet adotado.', 409)
            cur.execute('UPDATE pedidos_adocao SET status=%s WHERE id=%s', (novo, pedido_id))
            if novo == 'Aceito':
                cur.execute("UPDATE pets SET status='Adotado' WHERE id=%s", (pet['id'],))
                cur.execute("UPDATE pedidos_adocao SET status='Recusado' WHERE pet_id=%s AND id<>%s AND status='Pendente'", (pet['id'], pedido_id))
        conn.commit()
        return jsonify(ok=True, status=novo)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.get('/api/favoritos')
@exige_login()
def meus_favoritos():
    rows = executar(f'SELECT p.{CAMPOS.replace(",", ",p.")} FROM favoritos f JOIN pets p ON p.id=f.pet_id WHERE f.usuario_id=%s', (usuario_atual()['id'],))
    return jsonify(json_pronto(rows))


@app.post('/api/favoritos/<int:pet_id>')
@exige_login()
def favoritar(pet_id):
    if not executar('SELECT id FROM pets WHERE id=%s', (pet_id,), um=True):
        return erro('Pet não encontrado.', 404)
    executar('INSERT IGNORE INTO favoritos (usuario_id,pet_id) VALUES (%s,%s)', (usuario_atual()['id'], pet_id), escrita=True)
    return jsonify(ok=True), 201


@app.delete('/api/favoritos/<int:pet_id>')
@exige_login()
def desfavoritar(pet_id):
    executar('DELETE FROM favoritos WHERE usuario_id=%s AND pet_id=%s', (usuario_atual()['id'], pet_id), escrita=True)
    return jsonify(ok=True)


@app.get('/api/pets/<int:pet_id>/fotos')
def listar_fotos(pet_id):
    return jsonify(executar('SELECT id,caminho_foto,principal FROM fotos_pets WHERE pet_id=%s ORDER BY principal DESC,id', (pet_id,)))


@app.post('/api/pets/<int:pet_id>/fotos')
@exige_login('responsavel', 'administrador')
def adicionar_foto(pet_id):
    pet = executar('SELECT responsavel_id FROM pets WHERE id=%s', (pet_id,), um=True)
    if not pet:
        return erro('Pet não encontrado.', 404)
    if pet['responsavel_id'] != usuario_atual()['id'] and usuario_atual()['perfil'] != 'administrador':
        return erro('Sem permissão.', 403)
    # Para evitar upload inseguro, esta versão aceita apenas URL HTTPS.
    url = str(dados_json().get('caminho_foto', '')).strip()
    if not url.startswith('https://') or len(url) > 500:
        return erro('Informe uma URL HTTPS de foto (até 500 caracteres).')
    fid = executar('INSERT INTO fotos_pets (pet_id,caminho_foto) VALUES (%s,%s)', (pet_id, url), escrita=True)
    return jsonify(id=fid), 201


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
