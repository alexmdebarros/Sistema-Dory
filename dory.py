from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventos.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Importante para formulários
db = SQLAlchemy(app)

# Modelo de Dados
class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    departamento = db.Column(db.String(50), nullable=False)
    data_vencimento = db.Column(db.DateTime, nullable=False)
    descricao = db.Column(db.Text)
    prioridade = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Evento {self.nome}>'

# Criar o banco de dados (executar apenas uma vez)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        try:
            novo_evento = Evento(
                nome=request.form['nome'],
                tipo=request.form['tipo'],
                departamento=request.form['departamento'],
                data_vencimento=datetime.strptime(request.form['data'], '%Y-%m-%d'),
                descricao=request.form['descricao'],
                prioridade=request.form.get('prioridade', 'normal')
            )
            db.session.add(novo_evento)
            db.session.commit()
            return redirect(url_for('eventos'))
        except Exception as e:
            print(f"Erro ao salvar evento: {e}")
            db.session.rollback()
    return render_template("cadastrar.html")

@app.route("/excluir/<int:id>")
def excluir(id):
    evento = Evento.query.get_or_404(id)
    try:
        db.session.delete(evento)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao excluir: {e}")
        db.session.rollback()
    return redirect(url_for('eventos'))

@app.route("/editar/<int:id>", methods=['GET', 'POST'])
def editar(id):
    evento = Evento.query.get_or_404(id)
    if request.method == 'POST':
        try:
            evento.nome = request.form['nome']
            evento.tipo = request.form['tipo']
            evento.departamento = request.form['departamento']
            evento.data_vencimento = datetime.strptime(request.form['data'], '%Y-%m-%d')
            evento.descricao = request.form['descricao']
            evento.prioridade = request.form.get('prioridade', 'normal')
            db.session.commit()
            return redirect(url_for('eventos'))
        except Exception as e:
            print(f"Erro na edição: {e}")
            db.session.rollback()
    return render_template("editar.html", evento=evento)

@app.route("/concluir/<int:id>", methods=['POST'])
def concluir(id):
    evento = Evento.query.get_or_404(id)
    evento.status = 'concluido'
    db.session.commit()
    return redirect(url_for('eventos'))

@app.route("/eventos")
def eventos():
    eventos = Evento.query.order_by(Evento.data_vencimento).all()
    return render_template("eventos.html", eventos=eventos)

@app.route("/relatorios")
def relatorios():
    return "<h1>Relatórios</h1> <p>Em construção...</p>"

@app.route("/configuracoes")
def configuracoes():
    return "<h1>Configurações</h1> <p>Em construção...</p>"

if __name__ == "__main__":
    app.run(debug=True)