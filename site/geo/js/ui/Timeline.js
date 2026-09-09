/**
 * TIMELINE UI
 * Gerencia a visualização do histórico e timeline
 */

class Timeline {
    constructor() {
        this._initialized = false;
        this.history = [];
        this.currentFilter = 'all';
    }

    /**
     * Inicializa a timeline
     */
    init() {
        if (this._initialized) return;
        this._initialized = true;
        this._bindEvents();
        console.log('[Timeline] Inicializado');
    }

    /**
     * Renderiza a timeline
     * @param {Array} history 
     */
    render(history) {
        this.history = history || [];
        const container = document.getElementById('historyTimeline');
        if (!container) return;

        const filtered = this._applyFilter(this.history);

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="text-align:center;padding:40px 20px;color:var(--text-secondary);">
                    <div style="font-size:32px;margin-bottom:12px;">📜</div>
                    <p style="font-size:14px;">Nenhum registro no histórico.</p>
                </div>
            `;
            return;
        }

        let html = '';
        filtered.forEach(entry => {
            html += this._createHistoryItem(entry);
        });

        container.innerHTML = html;
    }

    /**
     * Cria item do histórico
     * @param {Object} entry 
     * @returns {string}
     * @private
     */
    _createHistoryItem(entry) {
        const severity = entry.severity || 'normal';
        const severityClass = severity === 'critica' ? 'critical' : 
                             severity === 'alta' ? 'high' : 'normal';

        const severityEmojis = {
            'critica': '🔴',
            'alta': '🟠',
            'media': '🟡',
            'normal': '🟢'
        };

        const emoji = severityEmojis[severity] || '📌';
        const date = new Date(entry.timestamp || entry.createdAt || Date.now());

        let content = entry.details || entry.action || 'Evento registrado';
        let title = entry.action || 'Evento';

        // Se for análise, mostra mais detalhes
        if (entry.analysisResult) {
            const result = entry.analysisResult;
            if (result.status === 'alteracao') {
                title = `⚠️ ${result.type_label || 'Alteração'}`;
                content = `Área afetada: ${result.affectedAreaHa?.toFixed(1) || 0} ha | Confiança: ${(result.confidence * 100).toFixed(0)}%`;
            } else {
                title = '✅ Análise Normal';
                content = 'Nenhuma alteração significativa detectada.';
            }
        }

        return `
            <div class="history-item ${severityClass}">
                <div class="history-header">
                    <div class="history-title">
                        ${emoji} ${title}
                    </div>
                    <div class="history-date">
                        ${date.toLocaleString('pt-BR')}
                    </div>
                </div>
                <div class="history-desc">
                    ${content}
                    ${entry.user ? `<span style="color:var(--text-muted);font-size:12px;margin-left:8px;">• ${entry.user}</span>` : ''}
                </div>
                ${entry.areaId ? `
                <div style="margin-top:6px;">
                    <button onclick="window.app?.switchView('areas');" 
                            style="font-size:11px;padding:2px 10px;border-radius:4px;border:1px solid var(--border-color);background:var(--bg-tertiary);color:var(--text-secondary);cursor:pointer;">
                        Ver área
                    </button>
                </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Aplica filtro ao histórico
     * @param {Array} history 
     * @returns {Array}
     * @private
     */
    _applyFilter(history) {
        if (this.currentFilter === 'all') return history;

        return history.filter(h => h.areaId === this.currentFilter);
    }

    /**
     * Filtra histórico por área
     * @param {string} areaId 
     */
    filter(areaId) {
        this.currentFilter = areaId;
        this.render(this.history);
    }

    /**
     * Atualiza dropdown de filtro com áreas
     * @param {Array} areas 
     */
    updateFilterOptions(areas) {
        const select = document.getElementById('historyAreaFilter');
        if (!select) return;

        const currentValue = select.value;
        select.innerHTML = `
            <option value="all">Todas as áreas</option>
            ${areas.map(a => `
                <option value="${a.id}">${a.nome}</option>
            `).join('')}
        `;
        if (currentValue) select.value = currentValue;
    }

    /**
     * Vincula eventos globais
     * @private
     */
    _bindEvents() {
        // Atualiza filtro quando mudar
        document.getElementById('historyAreaFilter')?.addEventListener('change', (e) => {
            this.filter(e.target.value);
        });
    }
}

// Exportar para uso global
window.Timeline = Timeline;