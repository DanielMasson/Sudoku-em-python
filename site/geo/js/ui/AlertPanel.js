/**
 * ALERT PANEL UI
 * Gerencia o centro de alertas
 */

class AlertPanel {
    constructor() {
        this._initialized = false;
        this.currentFilter = 'all';
        this.alerts = [];
    }

    /**
     * Inicializa o painel
     */
    init() {
        if (this._initialized) return;
        this._initialized = true;
        this._bindEvents();
        console.log('[AlertPanel] Inicializado');
    }

    /**
     * Renderiza lista de alertas
     * @param {Array} alerts 
     */
    render(alerts) {
        this.alerts = alerts || [];
        const container = document.getElementById('alertsList');
        if (!container) return;

        const filtered = this._applyFilter(this.alerts);

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="text-align:center;padding:60px 20px;color:var(--text-secondary);">
                    <div style="font-size:48px;margin-bottom:16px;">✅</div>
                    <h3 style="color:var(--text-primary);margin-bottom:8px;">Nenhum Alerta</h3>
                    <p style="font-size:14px;">Não há alertas ${this.currentFilter !== 'all' ? 'com este filtro' : ''}.</p>
                </div>
            `;
            return;
        }

        let html = '';
        filtered.forEach(alert => {
            html += this._createAlertItem(alert);
        });

        container.innerHTML = html;
        this._bindAlertEvents();
    }

    /**
     * Cria item de alerta
     * @param {Object} alert 
     * @returns {string}
     * @private
     */
    _createAlertItem(alert) {
        const severityEmojis = {
            'critica': '🔴',
            'alta': '🟠',
            'media': '🟡',
            'normal': '🟢'
        };

        const severityLabels = {
            'critica': 'CRÍTICO',
            'alta': 'ALTO',
            'media': 'MÉDIO',
            'normal': 'NORMAL'
        };

        const statusColors = {
            'Detectado': 'var(--status-critical)',
            'Em análise': 'var(--status-high)',
            'Confirmado': 'var(--status-normal)',
            'Falso positivo': 'var(--text-muted)',
            'Encerrado': 'var(--text-muted)'
        };

        const emoji = severityEmojis[alert.severity] || '⚠️';
        const severityLabel = severityLabels[alert.severity] || alert.severity.toUpperCase();
        const statusColor = statusColors[alert.status] || 'var(--text-secondary)';

        const date = new Date(alert.createdAt || alert.date);
        const dateStr = date.toLocaleString('pt-BR');

        return `
            <div class="alert-item ${alert.severity}" data-alert-id="${alert.id}">
                <div class="alert-icon">${emoji}</div>
                <div class="alert-content">
                    <div class="alert-title">
                        ${alert.areaName || 'Área não especificada'}
                        <span style="font-size:12px;font-weight:400;color:var(--text-muted);margin-left:8px;">
                            ${severityLabel}
                        </span>
                    </div>
                    <div class="alert-desc">${alert.description || 'Alerta detectado'}</div>
                    <div class="alert-meta">
                        <span>📅 ${dateStr}</span>
                        <span>🎯 Confiança: ${(alert.confidence * 100).toFixed(0)}%</span>
                        ${alert.affectedAreaHa ? `<span>📏 ${alert.affectedAreaHa.toFixed(1)} ha</span>` : ''}
                        <span style="color:${statusColor};font-weight:600;">${alert.status}</span>
                    </div>
                    <div class="alert-actions">
                        <button data-action="view" data-id="${alert.id}">👁️ Ver</button>
                        <button data-action="status" data-id="${alert.id}">📌 Atualizar Status</button>
                        ${alert.status !== 'Encerrado' && alert.status !== 'Falso positivo' ? 
                            `<button data-action="resolve" data-id="${alert.id}" style="color:var(--status-normal);">✅ Resolver</button>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Vincula eventos dos alertas
     * @private
     */
    _bindAlertEvents() {
        document.querySelectorAll('.alert-item .alert-actions button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                const id = btn.dataset.id;
                this._handleAction(action, id);
            });
        });

        // Clique no item para ver detalhes
        document.querySelectorAll('.alert-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.dataset.alertId;
                this._handleAction('view', id);
            });
        });
    }

    /**
     * Manipula ações dos alertas
     * @param {string} action 
     * @param {string} id 
     * @private
     */
    _handleAction(action, id) {
        const alert = window.app?.alertService?.get(id);
        if (!alert) {
            window.app?._showNotification('⚠️ Erro', 'Alerta não encontrado.', 'critical');
            return;
        }

        switch(action) {
            case 'view':
                this._showAlertDetails(alert);
                break;

            case 'status':
                this._showStatusUpdate(alert);
                break;

            case 'resolve':
                this._resolveAlert(id);
                break;

            default:
                break;
        }
    }

    /**
     * Mostra detalhes do alerta
     * @param {Object} alert 
     * @private
     */
    _showAlertDetails(alert) {
        const severityColors = {
            'critica': 'var(--status-critical)',
            'alta': 'var(--status-high)',
            'media': 'var(--status-medium)',
            'normal': 'var(--status-normal)'
        };

        const severityColor = severityColors[alert.severity] || 'var(--text-secondary)';
        const date = new Date(alert.createdAt || alert.date);

        const html = `
            <div style="display:flex;flex-direction:column;gap:16px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <h3 style="margin:0;font-size:18px;color:${severityColor};">
                            ⚠️ Alerta: ${alert.areaName || 'Área não especificada'}
                        </h3>
                        <div style="color:var(--text-secondary);font-size:14px;margin-top:4px;">
                            ${alert.type ? APP_CONFIG.CHANGE_TYPES.find(t => t.value === alert.type)?.label || alert.type : 'Alerta'}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:14px;font-weight:600;color:${severityColor};text-transform:uppercase;">
                            ${alert.severity.toUpperCase()}
                        </div>
                        <div style="font-size:12px;color:var(--text-muted);">
                            ${alert.status}
                        </div>
                    </div>
                </div>

                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;background:var(--bg-tertiary);border-radius:8px;padding:16px;">
                    <div>
                        <div style="font-size:11px;color:var(--text-muted);">Confiança</div>
                        <div style="font-weight:600;font-size:18px;">${(alert.confidence * 100).toFixed(0)}%</div>
                    </div>
                    ${alert.affectedAreaHa ? `
                    <div>
                        <div style="font-size:11px;color:var(--text-muted);">Área Afetada</div>
                        <div style="font-weight:600;font-size:18px;">${alert.affectedAreaHa.toFixed(1)} ha</div>
                    </div>
                    ` : ''}
                    <div>
                        <div style="font-size:11px;color:var(--text-muted);">Data</div>
                        <div style="font-weight:500;">${date.toLocaleString('pt-BR')}</div>
                    </div>
                    <div>
                        <div style="font-size:11px;color:var(--text-muted);">Status</div>
                        <div style="font-weight:500;color:${severityColor};">${alert.status}</div>
                    </div>
                </div>

                <div style="background:var(--bg-tertiary);border-radius:8px;padding:12px;">
                    <div style="font-size:12px;color:var(--text-muted);">Descrição</div>
                    <div style="margin-top:4px;">${alert.description || 'Nenhuma descrição fornecida.'}</div>
                </div>

                ${alert.history && alert.history.length > 0 ? `
                <div style="background:var(--bg-tertiary);border-radius:8px;padding:12px;">
                    <div style="font-size:12px;color:var(--text-muted);">Histórico de Status</div>
                    <div style="margin-top:8px;display:flex;flex-direction:column;gap:4px;">
                        ${alert.history.map(h => `
                            <div style="display:flex;justify-content:space-between;font-size:13px;padding:4px 0;border-bottom:1px solid var(--border-color);">
                                <span>${h.status}</span>
                                <span style="color:var(--text-muted);font-size:12px;">
                                    ${new Date(h.timestamp).toLocaleString('pt-BR')}
                                    ${h.user ? ` • ${h.user}` : ''}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <button onclick="window.app?.switchView('analysis');document.getElementById('analysisAreaSelect').value='${alert.areaId}';document.getElementById('runAnalysisBtn')?.click();" 
                            class="btn-primary" style="font-size:13px;">
                        🔍 Ver Análise
                    </button>
                    <button onclick="window.app?.mapService?.focusArea(window.app?.areaService?.get('${alert.areaId}'));window.app?.switchView('map');" 
                            class="btn-secondary" style="font-size:13px;">
                        🗺️ Ver no Mapa
                    </button>
                    ${alert.status !== 'Encerrado' && alert.status !== 'Falso positivo' ? `
                    <button onclick="this.closest('.modal').remove();window.app?.alertService?.updateStatus('${alert.id}','Confirmado');window.app?._updateUI();" 
                            class="btn-secondary" style="font-size:13px;color:var(--status-normal);border-color:var(--status-normal);">
                        ✅ Confirmar
                    </button>
                    <button onclick="this.closest('.modal').remove();window.app?.alertService?.updateStatus('${alert.id}','Falso positivo');window.app?._updateUI();" 
                            class="btn-secondary" style="font-size:13px;color:var(--text-muted);">
                        ❌ Falso Positivo
                    </button>
                    ` : ''}
                </div>
            </div>
        `;

        // Mostra em um modal
        const modal = document.createElement('div');
        modal.className = 'modal open';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width:600px;">
                <div class="modal-header">
                    <h2>📋 Detalhes do Alerta</h2>
                    <button class="modal-close" onclick="this.closest('.modal').remove();">&times;</button>
                </div>
                <div class="modal-body">
                    ${html}
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove();">Fechar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    /**
     * Mostra atualização de status
     * @param {Object} alert 
     * @private
     */
    _showStatusUpdate(alert) {
        const statuses = ['Detectado', 'Em análise', 'Confirmado', 'Falso positivo', 'Encerrado'];
        
        const html = `
            <div style="display:flex;flex-direction:column;gap:16px;">
                <p style="color:var(--text-secondary);">Atualizar status do alerta: <strong>${alert.areaName}</strong></p>
                <div style="display:flex;flex-direction:column;gap:8px;">
                    ${statuses.map(s => `
                        <button onclick="this.closest('.modal').remove();window.app?.alertService?.updateStatus('${alert.id}','${s}');window.app?._updateUI();" 
                                class="btn-secondary" style="text-align:left;padding:10px 16px;${s === alert.status ? 'border-color:var(--accent-blue);' : ''}">
                            ${s === alert.status ? '✅ ' : ''}${s}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        const modal = document.createElement('div');
        modal.className = 'modal open';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width:400px;">
                <div class="modal-header">
                    <h2>📌 Atualizar Status</h2>
                    <button class="modal-close" onclick="this.closest('.modal').remove();">&times;</button>
                </div>
                <div class="modal-body">
                    ${html}
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    /**
     * Resolve um alerta
     * @param {string} id 
     * @private
     */
    _resolveAlert(id) {
        if (!confirm('Confirmar que este alerta foi resolvido?')) return;
        
        const result = window.app?.alertService?.updateStatus(id, 'Encerrado');
        if (result) {
            window.app?._updateUI();
            window.app?._showNotification(
                '✅ Alerta resolvido',
                `Alerta "${result.areaName}" foi encerrado.`,
                'success'
            );
        }
    }

    /**
     * Aplica filtro aos alertas
     * @param {Array} alerts 
     * @returns {Array}
     * @private
     */
    _applyFilter(alerts) {
        if (this.currentFilter === 'all') return alerts;

        return alerts.filter(a => {
            if (this.currentFilter === 'critical') return a.severity === 'critica';
            if (this.currentFilter === 'high') return a.severity === 'alta';
            if (this.currentFilter === 'medium') return a.severity === 'media';
            if (this.currentFilter === 'normal') return a.severity === 'normal';
            return true;
        });
    }

    /**
     * Filtra alertas por severidade
     * @param {string} filter 
     */
    filter(filter) {
        this.currentFilter = filter;
        this.render(this.alerts);
    }

    /**
     * Vincula eventos globais
     * @private
     */
    _bindEvents() {
        // Filtros já são vinculados via data-filter no app.js
    }
}

// Exportar para uso global
window.AlertPanel = AlertPanel;