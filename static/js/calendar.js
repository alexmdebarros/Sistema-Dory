document.addEventListener('DOMContentLoaded', function() {
    // Debug: Verificar se a API está retornando dados
    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => console.log('Dados da API:', data))
        .catch(error => console.error('Erro ao carregar eventos:', error));

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'pt-br',
        initialView: 'dayGridMonth',
        headerToolbar: false,
        events: {
            url: '/api/eventos',
            method: 'GET',
            failure: function() {
                alert('Erro ao carregar eventos! Verifique o console para detalhes.');
            }
        },
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            abrirModalEvento(info.event);
        },
        eventDisplay: 'block',
        eventTimeFormat: { 
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        eventContent: function(arg) {
            const tipo = arg.event.extendedProps.tipo;
            const icon = {
                'imposto': 'file-invoice-dollar',
                'declaracao': 'file-export',
                'trabalhista': 'user-tie',
                'sped': 'file-code'
            }[tipo] || 'calendar-day';
            
            return {
                html: `<div class="fc-event-main">
                    <i class="fas fa-${icon}"></i>
                    ${arg.event.title}
                    <span class="fc-event-date">${arg.event.start.toLocaleDateString('pt-BR')}</span>
                </div>`
            };
        },
        eventClassNames: function(arg) {
            return [
                'event-' + arg.event.extendedProps.tipo,
                'status-' + arg.event.extendedProps.status
            ];
        }
    });

    calendar.render();

    // Controles do calendário
    document.getElementById('prev-btn').addEventListener('click', () => calendar.prev());
    document.getElementById('next-btn').addEventListener('click', () => calendar.next());
    document.getElementById('today-btn').addEventListener('click', () => {
        calendar.today();
        calendar.changeView('dayGridMonth');
    });

    // Botões de visualização
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            calendar.changeView(this.dataset.view);
        });
    });

    // Modal
    const modal = document.getElementById('eventModal');
    const closeModal = document.querySelector('.close-modal');

    function abrirModalEvento(evento) {
        document.getElementById('modalTitle').textContent = evento.title;
        document.getElementById('modalType').textContent = evento.extendedProps.tipo;
        document.getElementById('modalDept').textContent = evento.extendedProps.departamento;
        document.getElementById('modalDate').textContent = evento.start.toLocaleDateString('pt-BR');
        document.getElementById('modalStatus').textContent = evento.extendedProps.status;
        document.getElementById('modalDesc').textContent = evento.extendedProps.descricao || 'Nenhuma descrição';
        
        document.getElementById('editEventBtn').onclick = () => {
            window.location.href = `/editar/${evento.id}`;
        };
        
        document.getElementById('deleteEventBtn').onclick = () => {
            if (confirm('Tem certeza que deseja excluir este evento?')) {
                window.location.href = `/excluir/${evento.id}`;
            }
        };
        
        modal.style.display = 'block';
    }

    closeModal.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target === modal) modal.style.display = 'none';
    });
});