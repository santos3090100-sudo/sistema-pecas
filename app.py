from flask import Flask, render_template_string, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta'

# 🔐 SENHA
SENHA = "3090100"

# Criar banco
def criar_banco():
    conn = sqlite3.connect('pecas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peca TEXT,
            modelo TEXT,
            preco REAL
        )
    ''')
    conn.commit()
    conn.close()

criar_banco()

# 🔐 TELA DE LOGIN
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Acesso</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex align-items-center justify-content-center" style="height:100vh;">

<div class="card p-4 shadow">
    <h4 class="mb-3 text-center">🔒 Acesso ao Sistema</h4>
    <form method="POST">
        <input type="password" name="senha" class="form-control mb-3" placeholder="Digite a senha" required>
        <button class="btn btn-primary w-100">Entrar</button>
    </form>
    {% if erro %}
    <p class="text-danger mt-2 text-center">Senha incorreta</p>
    {% endif %}
</div>

</body>
</html>
"""

# 🌐 HTML PRINCIPAL
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Peças</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-4">

    <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>📱 Sistema de Peças</h2>
        <a href="/logout" class="btn btn-danger">Sair</a>
    </div>

    <div class="card p-3 mb-4 shadow">
        <h5>Cadastrar Peça</h5>
        <form method="POST">
            <div class="row">
                <div class="col">
                    <input class="form-control" type="text" name="peca" placeholder="Peça" required>
                </div>
                <div class="col">
                    <input class="form-control" type="text" name="modelo" placeholder="Modelo" required>
                </div>
                <div class="col">
                    <input class="form-control" type="number" step="0.01" name="preco" placeholder="Preço" required>
                </div>
                <div class="col">
                    <button class="btn btn-primary w-100">Salvar</button>
                </div>
            </div>
        </form>
    </div>

    <div class="card p-3 mb-4 shadow">
        <h5>Pesquisar</h5>
        <form method="GET">
            <input class="form-control" type="text" name="busca" placeholder="Digite para pesquisar">
        </form>
    </div>

    <div class="card p-3 shadow">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Peça</th>
                    <th>Modelo</th>
                    <th>Preço (R$)</th>
                </tr>
            </thead>
            <tbody>
                {% for item in resultados %}
                <tr>
                    <td>{{ item[0] }}</td>
                    <td>{{ item[1] }}</td>
                    <td>R$ {{ item[2] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

</div>

</body>
</html>
"""

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = False

    if request.method == 'POST':
        if request.form.get('senha') == SENHA:
            session['logado'] = True
            return redirect('/')
        else:
            erro = True

    return render_template_string(LOGIN_HTML, erro=erro)

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# 🌐 SISTEMA
@app.route('/', methods=['GET', 'POST'])
def index():

    # 🔒 PROTEÇÃO
    if not session.get('logado'):
        return redirect('/login')

    busca = request.args.get('busca', '')

    conn = sqlite3.connect('pecas.db')
    c = conn.cursor()

    # Salvar
    if request.method == 'POST':
        peca = request.form.get('peca')
        modelo = request.form.get('modelo')
        preco = request.form.get('preco')

        c.execute("INSERT INTO pecas (peca, modelo, preco) VALUES (?, ?, ?)",
                  (peca, modelo, preco))
        conn.commit()
        return redirect('/')

    # Buscar
    if busca:
        c.execute("SELECT peca, modelo, preco FROM pecas WHERE peca LIKE ? OR modelo LIKE ?",
                  ('%' + busca + '%', '%' + busca + '%'))
    else:
        c.execute("SELECT peca, modelo, preco FROM pecas")

    resultados = c.fetchall()

    conn.close()

    return render_template_string(HTML, resultados=resultados)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
