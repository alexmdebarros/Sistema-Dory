from dory import app, db, Evento
from datetime import datetime

with app.app_context():
    # Limpar dados existentes
    db.session.query(Evento).delete()
    
    # Criar eventos de exemplo
    eventos = [
        Evento(
            nome="ICMS - MAIO/2025",
            tipo="imposto",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 15),
            descricao="ICMS mensal do estado",
            prioridade="alta"
        ),
        Evento(
            nome="FGTS",
            tipo="trabalhista",
            departamento="rh",
            data_vencimento=datetime(2025, 5, 7),
            status="atrasado"
        )
    ]
    
    db.session.bulk_save_objects(eventos)
    db.session.commit()
    print("Dados de teste criados com sucesso!")