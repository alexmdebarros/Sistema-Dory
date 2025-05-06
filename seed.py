from dory import app, db, Evento
from datetime import datetime

with app.app_context():
    # Limpar dados existentes
    db.session.query(Evento).delete()
    
    # Eventos para Maio/2025 (Lucro Real)
    eventos = [
        # --- IMPOSTOS ---
        Evento(
            nome="ICMS - MAIO/2025",
            tipo="imposto",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 15),
            descricao="ICMS mensal do estado",
            prioridade="alta"
        ),
        Evento(
            nome="PIS/COFINS - Apuração",
            tipo="imposto",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 10),
            prioridade="alta"
        ),
        Evento(
            nome="IRPJ - Estimativa",
            tipo="imposto",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 20),
            descricao="Pagamento do IRPJ mensal"
        ),
        
        # --- DECLARAÇÕES FISCAIS ---
        Evento(
            nome="EFD Contribuições",
            tipo="sped",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 11),
            prioridade="urgente"
        ),
        Evento(
            nome="SPED Fiscal",
            tipo="sped",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 18),
            descricao="Envio da escrituração fiscal"
        ),
        Evento(
            nome="DCTF Mensal",
            tipo="declaracao",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 25),
            prioridade="alta"
        ),
        
        # --- TRABALHISTAS ---
        Evento(
            nome="FGTS - MAIO/2025",
            tipo="trabalhista",
            departamento="rh",
            data_vencimento=datetime(2025, 5, 7),
            status="atrasado",
            descricao="Pagamento atrasado"
        ),
        Evento(
            nome="INSS - Recolhimento",
            tipo="trabalhista",
            departamento="rh",
            data_vencimento=datetime(2025, 5, 20),
            prioridade="alta"
        ),
        Evento(
            nome="RAIS Mensal",
            tipo="trabalhista",
            departamento="rh",
            data_vencimento=datetime(2025, 5, 30)
        ),
        
        # --- CONTÁBEIS ---
        Evento(
            nome="Balancete Mensal",
            tipo="declaracao",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 5),
            descricao="Conferência do balancete"
        ),
        Evento(
            nome="LALUR - Atualização",
            tipo="declaracao",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 12)
        ),
        
        # --- MUNICIPAIS ---
        Evento(
            nome="ISS - São Paulo",
            tipo="imposto",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 10)
        ),
        Evento(
            nome="IPTU - Parcela 2/10",
            tipo="imposto",
            departamento="financeiro",
            data_vencimento=datetime(2025, 5, 25)
        ),
        
        # --- OUTRAS OBRIGAÇÕES ---
        Evento(
            nome="DIRF - Retificadora",
            tipo="declaracao",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 8),
            descricao="Envio retificatório"
        ),
        Evento(
            nome="Simples Nacional - Opção",
            tipo="declaracao",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 2),
            status="concluido"
        ),
        Evento(
            nome="Auditoria Interna",
            tipo="outros",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 28),
            prioridade="alta"
        ),
        Evento(
            nome="Renovação Certificado Digital",
            tipo="outros",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 14),
            descricao="Vencimento do e-CPF"
        ),
        Evento(
            nome="Relatório Contábil Gerencial",
            tipo="outros",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 6)
        ),
        Evento(
            nome="Declaração de Débitos Tributários",
            tipo="declaracao",
            departamento="fiscal",
            data_vencimento=datetime(2025, 5, 22)
        ),
        Evento(
            nome="Reunião com Contador",
            tipo="outros",
            departamento="contabil",
            data_vencimento=datetime(2025, 5, 9),
            prioridade="normal"
        )
    ]
    
    db.session.bulk_save_objects(eventos)
    db.session.commit()
    print(f"{len(eventos)} eventos de teste criados com sucesso para Maio/2025!")