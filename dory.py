from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventos.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Lista de feriados nacionais e locais (Maringá/PR)
feriados_brasil = [
    datetime(2025, 1, 1),   # Confraternização Universal
    datetime(2025, 4, 18),  # Paixão de Cristo
    datetime(2025, 4, 21),  # Tiradentes
    datetime(2025, 5, 1),   # Dia do Trabalho
    datetime(2025, 9, 7),   # Independência do Brasil
    datetime(2025, 10, 12), # Nossa Senhora Aparecida
    datetime(2025, 11, 2),  # Finados
    datetime(2025, 11, 15), # Proclamação da República
    datetime(2025, 11, 20), # Dia da Consciência Negra
    datetime(2025, 12, 25), # Natal
    datetime(2025, 12, 19), # Emancipação Política do Paraná
    datetime(2025, 5, 12),  # Aniversário de Maringá
    datetime(2025, 8, 15),  # Nossa Senhora da Glória (Padroeira)
]

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
    repetir_mensal = db.Column(db.Boolean, default=False)
    antecipar_dia_util = db.Column(db.Boolean, default=False)
    data_fim_repeticao = db.Column(db.DateTime)
    evento_pai_id = db.Column(db.Integer, db.ForeignKey('evento.id'))
    ultima_notificacao = db.Column(db.DateTime)  # Data da última notificação
    tentativas_notificacao = db.Column(db.Integer, default=0)  # Quantas vezes foi notificado
    
    def deve_notificar(self):
        if self.status == 'concluido':
            return False
            
        agora = datetime.utcnow()
        dias_atraso = (agora.date() - self.data_vencimento.date()).days
        
        # Lógica de frequência de notificação
        if dias_atraso == 0:  # Vence hoje
            return True
        elif dias_atraso == 1:  # 1 dia atrasado
            return self.tentativas_notificacao < 3
        elif dias_atraso <= 7:  # 1 semana atrasada
            return self.tentativas_notificacao < (dias_atraso * 2)
        else:  # Mais de 1 semana
            return agora > (self.ultima_notificacao or self.data_vencimento) + timedelta(days=2)
    

    def __repr__(self):
        return f'<Evento {self.nome}>'
    
    def status_notificacao(self):
        hoje = datetime.utcnow().date()
        dias_restantes = (self.data_vencimento.date() - hoje).days
        
        if dias_restantes < 0:
            return {
                'status': f"ATRASADO {abs(dias_restantes)} dia(s)",
                'urgente': True,
                'icone': 'exclamation-triangle'
            }
        elif dias_restantes == 0:
            return {
                'status': "VENCE HOJE",
                'urgente': True,
                'icone': 'exclamation-circle'
            }
        elif dias_restantes <= 2:
            return {
                'status': f"Vence em {dias_restantes} dias",
                'urgente': False,
                'icone': 'bell'
            }
        return None

def ajustar_dia_util(data):
    """Ajusta a data para o último dia útil se cair em fim de semana ou feriado"""
    while data.weekday() >= 5 or data.date() in [f.date() for f in feriados_brasil]:
        data -= timedelta(days=1)
    return data

@app.route("/")
def home():
    eventos = Evento.query.order_by(Evento.data_vencimento).limit(5).all()
    return render_template("index.html", eventos=eventos)

@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        # Capturar dados do formulário
        form_data = {
            'nome': request.form['nome'],
            'tipo': request.form['tipo'],
            'departamento': request.form['departamento'],
            'data': request.form['data_vencimento'],
            'descricao': request.form.get('descricao', ''),
            'prioridade': request.form.get('prioridade', 'normal'),
            'repetir_mensal': 'repetir_mensal' in request.form,
            'antecipar_dia_util': 'antecipar_dia_util' in request.form,
            'meses_repeticao': int(request.form.get('meses_repeticao', 12))
        }

        try:
            data_vencimento = datetime.strptime(form_data['data'], '%Y-%m-%d')
        except ValueError:
            flash('⚠️ Formato de data inválido! Use o formato AAAA-MM-DD', 'error')
            return render_template("cadastrar.html", form_data=form_data)

        # Gerar lista de datas para verificação
        dates_to_check = []
        if form_data['repetir_mensal']:
            # Verificar evento pai
            dates_to_check.append(data_vencimento)
            
            # Gerar datas dos eventos filhos
            for i in range(form_data['meses_repeticao']):
                nova_data = data_vencimento + relativedelta(months=+i)
                if form_data['antecipar_dia_util']:
                    nova_data = ajustar_dia_util(nova_data)
                dates_to_check.append(nova_data)
        else:
            # Ajustar data única se necessário
            if form_data['antecipar_dia_util']:
                data_vencimento = ajustar_dia_util(data_vencimento)
            dates_to_check.append(data_vencimento)

        # Verificar duplicatas
        existing_dates = []
        for date in dates_to_check:
            exists = Evento.query.filter_by(
                nome=form_data['nome'],
                tipo=form_data['tipo'],
                departamento=form_data['departamento'],
                data_vencimento=date
            ).first()
            
            if exists:
                existing_dates.append(date.strftime('%d/%m/%Y'))

        if existing_dates:
            flash(f'⚠️ Evento já existe nas datas: {", ".join(existing_dates)}', 'error')
            return render_template("cadastrar.html", form_data=form_data)

        # Criar eventos
        eventos = []
        evento_pai = None

        try:
            if form_data['repetir_mensal']:
                # Criar evento pai
                evento_pai = Evento(
                    nome=form_data['nome'],
                    tipo=form_data['tipo'],
                    departamento=form_data['departamento'],
                    data_vencimento=data_vencimento,
                    descricao=form_data['descricao'],
                    prioridade=form_data['prioridade'],
                    repetir_mensal=True,
                    antecipar_dia_util=form_data['antecipar_dia_util'],
                    data_fim_repeticao=data_vencimento + relativedelta(months=+form_data['meses_repeticao'])
                )
                db.session.add(evento_pai)
                db.session.commit()

                # Criar eventos filhos
                for i in range(form_data['meses_repeticao']):
                    nova_data = data_vencimento + relativedelta(months=+i)
                    if form_data['antecipar_dia_util']:
                        nova_data = ajustar_dia_util(nova_data)

                    eventos.append(Evento(
                        nome=f"{form_data['nome']} ({nova_data.strftime('%m/%Y')})",
                        tipo=form_data['tipo'],
                        departamento=form_data['departamento'],
                        data_vencimento=nova_data,
                        descricao=form_data['descricao'],
                        prioridade=form_data['prioridade'],
                        repetir_mensal=True,
                        antecipar_dia_util=form_data['antecipar_dia_util'],
                        evento_pai_id=evento_pai.id
                    ))
            else:
                # Criar evento único
                eventos.append(Evento(
                    nome=form_data['nome'],
                    tipo=form_data['tipo'],
                    departamento=form_data['departamento'],
                    data_vencimento=data_vencimento,
                    descricao=form_data['descricao'],
                    prioridade=form_data['prioridade']
                ))

            db.session.bulk_save_objects(eventos)
            db.session.commit()
            flash('✅ Evento cadastrado com sucesso!', 'success')
            return redirect(url_for('eventos'))

        except Exception as e:
            db.session.rollback()
            flash(f'⚠️ Erro no cadastro: {str(e)}', 'error')
            return render_template("cadastrar.html", form_data=form_data)

    return render_template("cadastrar.html")

@app.route("/eventos")
def eventos():
    eventos = Evento.query.order_by(Evento.data_vencimento).all()
    return render_template("eventos.html", eventos=eventos)

@app.route("/editar/<int:id>", methods=['GET', 'POST'])
def editar(id):
    evento = Evento.query.get_or_404(id)
    
    if request.method == 'POST':
        editar_todos = request.form.get('editar_todos') == 'on'
        
        if editar_todos and evento.evento_pai_id:
            eventos_serie = Evento.query.filter_by(evento_pai_id=evento.evento_pai_id).all()
            for ev in eventos_serie:
                if ev.data_vencimento >= evento.data_vencimento:
                    ev.nome = request.form['nome'].split(' (')[0] + f" ({ev.data_vencimento.strftime('%m/%Y')})"
                    ev.tipo = request.form['tipo']
                    ev.departamento = request.form['departamento']
                    ev.descricao = request.form['descricao']
                    ev.prioridade = request.form.get('prioridade', 'normal')
        else:
            evento.nome = request.form['nome']
            evento.tipo = request.form['tipo']
            evento.departamento = request.form['departamento']
            evento.descricao = request.form['descricao']
            evento.prioridade = request.form.get('prioridade', 'normal')
        
        db.session.commit()
        return redirect(url_for('eventos'))
    
    return render_template("editar.html", evento=evento)

@app.route("/excluir/<int:id>")
def excluir(id):
    evento = Evento.query.get_or_404(id)
    excluir_todos = request.args.get('todos', 'false') == 'true'
    
    if excluir_todos and evento.evento_pai_id:
        Evento.query.filter_by(evento_pai_id=evento.evento_pai_id).delete()
    else:
        db.session.delete(evento)
    
    db.session.commit()
    return redirect(url_for('eventos'))

@app.route("/concluir/<int:id>", methods=['POST'])
def concluir(id):
    evento = Evento.query.get_or_404(id)
    evento.status = 'concluido'
    evento.ultima_notificacao = datetime.utcnow()
    db.session.commit()
    
    # Redireciona de volta para a página de eventos
    return redirect(url_for('eventos'))

@app.route("/calendario")
def calendario():
    return render_template("calendario.html")

@app.route("/api/eventos")
def api_eventos():
    eventos = Evento.query.all()
    eventos_json = [{
        'id': e.id,
        'title': e.nome,
        'start': e.data_vencimento.strftime('%Y-%m-%d'),
        'color': '#4361ee' if e.tipo == 'imposto' else '#2ecc71' if e.tipo == 'declaracao' else '#e67e22',
        'extendedProps': {
            'tipo': e.tipo,
            'departamento': e.departamento,
            'status': e.status,
            'descricao': e.descricao
        }
    } for e in eventos]
    return jsonify(eventos_json)

@app.route("/api/notificacoes")
def api_notificacoes():
    hoje = datetime.utcnow().date()
    data_limite = hoje + timedelta(days=2)  # Agora considera 2 dias à frente

    # Busca eventos que vencem até 2 dias no futuro (incluindo atrasados)
    eventos = Evento.query.filter(
        Evento.data_vencimento <= data_limite,
        Evento.status != 'concluido'
    ).order_by(
        Evento.data_vencimento.asc()
    ).all()

    notificacoes = []
    for evento in eventos:
        dias_restantes = (evento.data_vencimento.date() - hoje).days
        
        if dias_restantes < 0:
            status = f"⚠️ ATRASADO {abs(dias_restantes)} dia(s)"
            prioridade = 'urgente'
        elif dias_restantes == 0:
            status = "⚠️ VENCE HOJE"
            prioridade = 'urgente'
        elif dias_restantes == 1:
            status = "Vence amanhã"
            prioridade = 'media'
        else:  # dias_restantes == 2
            status = "Vence em 2 dias"
            prioridade = 'baixa'

        notificacoes.append({
            'id': evento.id,
            'titulo': f"{evento.tipo.upper()}: {evento.nome}",
            'mensagem': f"{status} | Depto: {evento.departamento}",
            'tipo': evento.tipo,
            'prioridade': prioridade,
            'dias_restantes': dias_restantes,
            'data_vencimento': evento.data_vencimento.strftime('%d/%m/%Y')
        })

    return jsonify(notificacoes)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)