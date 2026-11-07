const glyphs = {
    inbox: 'M21 8v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8m0 0 5-5h8l5 5m-18 0h5l2 3h4l2-3h5',
    users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m14-18a4 4 0 0 1 0 8m6 10v-2a4 4 0 0 0-3-3.87M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
    chart: 'M3 3v18h18M7 16v-5m5 5V7m5 9v-8',
    flow: 'M12 3h7a2 2 0 0 1 2 2v7m-9-9V1m0 2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3M8 12h8M12 8v8',
    plug: 'M12 22v-5m-4-7V2m8 8V2M7 10h10v3a5 5 0 0 1-10 0v-3Z',
    globe: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-10 10h20m-10-10c-6 5-6 15 0 20m0-20c6 5 6 15 0 20',
    activity: 'M3 12h5l3-8 4 16 3-8h3',
    layout: 'M3 3h18v18H3zM9 3v18m0-12h12',
    bookmark: 'M5 3h14v19l-7-5-7 5V3Z',
    flag: 'M4 22V4m0 1c6-4 10 4 16 0v11c-6 4-10-4-16 0',
    layers: 'M12 2 2 7l10 5 10-5-10-5Zm-10 10 10 5 10-5M2 17l10 5 10-5',
    settings: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm7.4-1a1.9 1.9 0 0 0 .4 2.1l-1.7 1.7a1.9 1.9 0 0 0-2.1-.4 1.9 1.9 0 0 0-1 1.8V21h-2.4v-1.8a1.9 1.9 0 0 0-1-1.8 1.9 1.9 0 0 0-2.1.4l-1.7-1.7a1.9 1.9 0 0 0 .4-2.1 1.9 1.9 0 0 0-1.8-1H4v-2.4h1.8a1.9 1.9 0 0 0 1.8-1 1.9 1.9 0 0 0-.4-2.1l1.7-1.7a1.9 1.9 0 0 0 2.1.4 1.9 1.9 0 0 0 1-1.8V3h2.4v1.8a1.9 1.9 0 0 0 1 1.8 1.9 1.9 0 0 0 2.1-.4l1.7 1.7a1.9 1.9 0 0 0-.4 2.1 1.9 1.9 0 0 0 1.8 1H21v2.4h-1.8a1.9 1.9 0 0 0-1.8 1Z',
    search: 'M21 21l-4.35-4.35M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z',
    send: 'm22 2-7 20-4-9-9-4 20-7ZM22 2 11 13',
    plus: 'M12 5v14M5 12h14',
    bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4',
    pin: 'm16 3 5 5m-6 4 4-4-4-4-7 7v3l-4 4m10-6-6-6M8 13l3 3',
    arrow: 'M5 12h14m-7-7 7 7-7 7',
    back: 'M19 12H5m7 7-7-7 7-7',
    logout: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4m7 14 5-5-5-5m5 5H9',
    chevron: 'm6 9 6 6 6-6',
    close: 'M18 6 6 18M6 6l12 12',
    check: 'M20 6 9 17l-5-5',
    note: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm0 0v6h6M8 13h8m-8 4h8',
    moon: 'M20 15.5A8 8 0 0 1 8.5 4 8 8 0 1 0 20 15.5Z',
    sun: 'M12 2v2m0 16v2M2 12h2m16 0h2m-4.9-7.1 1.4-1.4M4.5 19.5l1.4-1.4M4.5 4.5l1.4 1.4m11.2 11.2 1.4 1.4M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z',
    filter: 'M4 7h16M7 12h10m-7 5h4',
    briefcase: 'M3 7h18v13H3V7Zm5 0V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18',
    clock: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 5v5l3 2',
    shield: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z',
    info: 'M12 18v-6m0-4h.01M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z',
    sparkles: 'm12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3ZM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z',
    menu: 'M4 6h16M4 12h16M4 18h16',
    copy: 'M8 4h11a2 2 0 0 1 2 2v12M5 8h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2Z'
};
function Icon({ name, size = 18 }) { return React.createElement("svg", { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.65", strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": "true" },
    React.createElement("path", { d: glyphs[name] || glyphs.info })); }
function fmt(ts) { if (!ts)
    return '—'; return new Date(ts * 1000).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }); }
function dateFmt(ts) { if (!ts)
    return '—'; return new Date(ts * 1000).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }); }
function formatMoney(value, currency = 'RUB') { try {
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: currency || 'RUB', maximumFractionDigits: 0 }).format(Number(value || 0));
}
catch (e) {
    return Number(value || 0).toLocaleString('ru-RU') + ' ' + currency;
} }
function initials(name) { return (name || '?').split(' ').slice(0, 2).map((v) => v[0]).join('').toUpperCase(); }
function avatarColor(name) { let h = 0; for (let ch of name || '')
    h = ((h << 5) - h) + ch.charCodeAt(0); return `hsl(${Math.abs(h) % 360} 38% 28%)`; }
function Avatar({ name, size = 42 }) { return React.createElement("div", { className: "avatar", style: { width: size, height: size, background: avatarColor(name), fontSize: size * .31 }, "aria-hidden": "true" }, initials(name)); }
function outgoingLimit(type) { return type === 'instagram' ? 1000 : type === 'avito' ? 1000 : 4000; }
function outgoingSize(type, text) { return type === 'instagram' ? new TextEncoder().encode(text).length : text.length; }
const DELIVERY_LABELS = {
    queued: '\u0412 \u043e\u0447\u0435\u0440\u0435\u0434\u0438',
    processing: '\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u0435\u0442\u0441\u044f',
    accepted: '\u041f\u0440\u0438\u043d\u044f\u0442\u043e API',
    sent: '\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e',
    delivered: '\u0414\u043e\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u043e',
    read: '\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u043d\u043e',
    uncertain: '\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c',
    failed: '\u041e\u0448\u0438\u0431\u043a\u0430',
    cancelled: '\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u043e',
};
function inboundIssueLabel(error) {
    return {
        'encryption_key_unavailable': 'Ключ шифрования недоступен: проверьте ключи перед восстановлением',
        'invalid_encrypted_event': 'Событие повреждено: проверьте источник перед повтором',
        'worker_claim_expired': 'Обработчик не завершил попытку: проверьте состояние сервера',
        'SyntheticFailure': 'Тестовая ошибка обработки'
    }[error] || 'Ошибка обработки — требуется проверка';
}
function deliveryLabel(status, provider = '') { if (status === 'accepted' && provider === 'website')
    return 'Ожидает подтверждения виджета'; return DELIVERY_LABELS[status] || '\u041d\u0435 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u043e'; }
function providerName(s) { return { avito: 'Авито', instagram: 'Instagram', whatsapp: 'WhatsApp', telegram: 'Telegram', vk: 'ВКонтакте', max: 'MAX', messenger: 'Facebook Messenger', website: 'Сайт' }[s] || s; }
function Provider({ type, small = false }) {
    const cls = 'provider ' + type + (small ? ' small' : '');
    let mark = null;
    if (type === 'avito')
        mark = React.createElement("span", { className: "avito-mark" },
            React.createElement("i", null),
            React.createElement("i", null),
            React.createElement("i", null),
            React.createElement("i", null));
    else if (type === 'instagram')
        mark = React.createElement("svg", { viewBox: "0 0 30 30", "aria-hidden": "true" },
            React.createElement("rect", { x: "5", y: "5", width: "20", height: "20", rx: "6", fill: "none", stroke: "white", strokeWidth: "2.5" }),
            React.createElement("circle", { cx: "15", cy: "15", r: "5.1", fill: "none", stroke: "white", strokeWidth: "2.3" }),
            React.createElement("circle", { cx: "21.3", cy: "8.8", r: "1.5", fill: "white" }));
    else if (type === 'whatsapp')
        mark = React.createElement("svg", { viewBox: "0 0 30 30", "aria-hidden": "true" },
            React.createElement("path", { d: "M15 4a10.8 10.8 0 0 0-9 16.7L4 26l5.6-1.9A10.8 10.8 0 1 0 15 4Z", stroke: "white", strokeWidth: "2", fill: "none" }),
            React.createElement("path", { d: "M10.6 10.4c.6-1 1.3-1.1 1.8-.4l1.3 1.9-.8 1.2c1.1 2.1 2.4 3.2 4.5 4.1l1.2-.9 2.1 1.2c.6.4.6 1.2-.2 1.9-2.8 2.4-10.1-3.5-10.2-7.2 0-.7.1-1.2.3-1.8Z", fill: "white" }));
    else if (type === 'telegram')
        mark = React.createElement("svg", { viewBox: "0 0 30 30", "aria-hidden": "true" },
            React.createElement("path", { d: "M4 14.2 25 6.5c1.2-.4 1.7.2 1.3 1.5l-3.8 17.1c-.3 1.2-1.1 1.4-2 0l-5.7-4.2-2.8 2.7-.1-5.2 10-9.1-12.2 7.8-5-1.5c-1.2-.4-1.3-.9-.7-1.4Z", fill: "white" }));
    else if (type === 'vk')
        mark = React.createElement("span", { className: "vk-mark" }, "VK");
    else if (type === 'max')
        mark = React.createElement("span", { className: "max-mark" }, "M");
    else if (type === 'messenger')
        mark = React.createElement("span", { className: "messenger-mark" }, "\u2197");
    else
        mark = React.createElement("svg", { viewBox: "0 0 30 30", "aria-hidden": "true" },
            React.createElement("path", { d: "M6 6h18v14H14l-6 5v-5H6Z", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinejoin: "round" }),
            React.createElement("circle", { cx: "11", cy: "13", r: "1.2" }),
            React.createElement("circle", { cx: "15", cy: "13", r: "1.2" }),
            React.createElement("circle", { cx: "19", cy: "13", r: "1.2" }));
    return React.createElement("span", { className: cls, title: providerName(type), "aria-label": providerName(type) }, mark);
}
const CHANNELS = ['avito', 'instagram', 'whatsapp', 'telegram', 'vk', 'max', 'messenger', 'website'];
const PRIORITIES = { urgent: 'Срочно', high: 'Высокий', normal: 'Обычный', low: 'Низкий' };
const STATUS = { new: 'Новый', in_progress: 'В работе', waiting: 'Ожидает', closed: 'Закрыт' };
const STAGES = { new: 'Новый', interested: 'Заинтересован', negotiation: 'Переговоры', payment: 'Оплата', success: 'Успешно', lost: 'Отказ' };
const NAV = [['command', 'layout', 'Центр управления'], ['inbox', 'inbox', 'Входящие'], ['contacts', 'users', 'Клиенты'], ['analytics', 'chart', 'Аналитика'], ['rules', 'flow', 'Автоматизация'], ['integrations', 'plug', 'Интеграции'], ['websites', 'globe', 'Чат для сайтов'], ['operations', 'activity', 'Контроль доставки'], ['team', 'users', 'Команда']];
function readableError(message) {
    if (/Failed to fetch|NetworkError|fetch failed/i.test(message))
        return 'Не удалось связаться с OSMANX. Проверьте сеть и попробуйте снова — ваши сообщения не удалены.';
    if (/Another teammate is currently replying/i.test(message))
        return 'С этим клиентом сейчас работает коллега. Откройте другой диалог или повторите позже.';
    if (/Диалог уже изменился/i.test(message))
        return 'Пока вы писали, переписка обновилась. Текст ответа сохранён. Проверьте новые сообщения и отправьте снова.';
    if (/401|сессия истекла|не авторизован/i.test(message))
        return 'Сеанс завершён. Войдите снова, чтобы продолжить.';
    return message || 'Не удалось выполнить действие. Попробуйте ещё раз.';
}
function csrf() { const v = document.cookie.split('; ').find(x => x.startsWith('omnichat_csrf=')); return v ? decodeURIComponent(v.split('=').slice(1).join('=')) : ''; }
async function request(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    if (opts.method && opts.method !== 'GET')
        headers['X-CSRF-Token'] = csrf();
    const response = await fetch('/api' + path, { credentials: 'same-origin', ...opts, headers });
    const data = await response.json().catch(() => ({ detail: 'Сервер вернул нечитаемый ответ' }));
    if (!response.ok)
        throw new Error(typeof data.detail === 'string' ? data.detail : `Ошибка ${response.status}`);
    return data;
}
class OmniApp extends React.Component {
    constructor() {
        super(...arguments);
        this.state = { boot: true, me: null, view: new URLSearchParams(window.location.search).get('view') || 'inbox', authMode: 'demo', authCompany: '', authName: '', authEmail: '', authPassword: '', authError: '', loading: false,
            convs: [], selected: null, detail: null, search: '', channelFilter: '', statusFilter: '', priorityFilter: '', sortFilter: 'recent', reply: '', note: '', tab: 'info', activity: [], views: [], viewName: '', viewShared: false, command: null, team: [], sessions: null, contacts: [], analytics: null, rules: [], integrations: null, plans: null,
            toast: '', templates: [], alerts: null, archivedFilter: false, assignedFilter: '', privacy: null, templateName: '', templateBody: '', light: localStorage.getItem('omnichat_theme') === 'light', mobilePane: 'list', sidebarOpen: false, moreNav: false, advancedFilters: false, customerOpen: true, customerExtras: false, followupEditing: false, tagInput: '', tagEditing: false, showEmoji: false, showQuickReplies: false, chatActionsOpen: false, modal: '', connectToken: '', connectPhone: '', botProvider: 'telegram', botGroupId: '', botConfirmation: '', botConnectedInfo: null, inviteEmail: '', inviteRole: 'operator', inviteToken: '',
            integrationGuide: null, quickstart: null, focusedProvider: '', messengerPages: [], channelDiagnostics: null, channelDiagnosticsFor: '', connectWaba: '', newOrganization: '', rotateChannel: '', rotateToken: '', registerPhoneChannel: '', registrationPin: '', metaSession: null,
            ruleName: '', ruleCondition: 'contains', ruleTerm: '', ruleAction: 'tag', ruleActionValue: 'VIP', demoInbound: '', contactDraft: null, sites: [], siteSelected: '', siteName: '', siteOrigins: '', siteGreeting: 'Здравствуйте! Чем можем вам помочь?', siteAccent: '#90b7a7', localization: null, operations: null, operationsJobs: [], operationsInboundJobs: [], inboundHealth: null, inboundIntegrity: null, inboundRepairReason: '', inboundRepairConfirmed: false, inboundTriageStatus: '', inboundTriageCursor: null,
            inboundControlScope: 'organization', inboundPauseAction: 'pause', inboundPauseReason: '',
            inboundBatchChannel: '', inboundBatchReason: '', inboundBatchPreview: null, inboundRetryJob: null, inboundRetryReason: '', inboundDismissJob: null, inboundDismissReason: '', inboundDismissCode: 'unrecoverable', inboundDismissConfirmed: false, reconcileJob: null, reconcileStatus: 'accepted', reconcileEvidence: '', reconcileExternalId: '', outboxRetryJob: null, outboxRetryEvidence: '', outboxRetryVerified: false,
            dispatchPauses: null, deliveryTelemetry: null, opsPauseReason: 'incident', opsPauseMinutes: '60', opsPauseChannel: '', selectedJobEvents: null,
            waTemplates: [], waConsent: false, waSelected: '', waParams: [], waConsentSource: '', waConsentCheckbox: false, waLoading: false, olderLoading: false };
        this.timer = null;
        this.searchTimer = null;
        this.toastTimer = null;
        this.ws = null;
        this.reconnectTimer = null;
        this.metaFlow = null;
        this.historyLoading = false;
        // Draft text lives in memory only. It is never written to browser storage or sent to the server before Send.
        this.drafts = {};
        this.pendingSend = {};
        this.sending = false;
        this.handleHotkey = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                if (this.state.view !== 'inbox')
                    this.changeView('inbox');
                setTimeout(() => document.querySelector('[aria-label="Поиск по перепискам"]')?.focus(), 100);
                return;
            }
            if (e.key === 'Escape') {
                this.setState({ modal: '', sidebarOpen: false });
                return;
            }
            if ((e.metaKey || e.ctrlKey) && e.key === '1') {
                e.preventDefault();
                this.changeView('command');
                return;
            }
            if ((e.metaKey || e.ctrlKey) && e.key === '2') {
                e.preventDefault();
                this.changeView('inbox');
                return;
            }
            const target = e.target;
            if (target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName))
                return;
            if (this.state.view === 'inbox' && !e.metaKey && !e.ctrlKey && ['j', 'k'].includes(e.key)) {
                const rows = this.state.convs;
                const current = rows.findIndex((c) => c.id === this.state.selected);
                const index = e.key === 'j' ? Math.min(rows.length - 1, current + 1) : Math.max(0, current - 1);
                if (rows[index]) {
                    e.preventDefault();
                    this.select(rows[index].id);
                }
            }
        };
        this.notify = (text) => { this.setState({ toast: readableError(text) }); if (this.toastTimer)
            clearTimeout(this.toastTimer); this.toastTimer = setTimeout(() => this.setState({ toast: '' }), 4500); };
        this.boot = async () => {
            try {
                const me = await request('/auth/me');
                this.setState({ me, boot: false }, () => this.connectRealtime());
                const requested = this.state.view;
                const view = ['owner', 'admin'].includes(me.role) || requested !== 'start' ? requested : 'inbox';
                if (view !== requested)
                    this.setState({ view });
                await this.loadView(view);
                await this.loadShared();
                if (['owner', 'admin'].includes(me.role) && view !== 'start') {
                    try {
                        this.setState({ quickstart: await request('/quickstart') });
                    }
                    catch (e) { }
                }
            }
            catch (e) {
                this.setState({ me: null, boot: false });
            }
        };
        this.connectRealtime = () => {
            if (!this.state.me || !['http:', 'https:'].includes(window.location.protocol) || !('WebSocket' in window))
                return;
            try {
                if (this.ws) {
                    this.ws.close();
                    this.ws = null;
                }
                const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
                const socket = new WebSocket(proto + '//' + location.host + '/api/ws');
                this.ws = socket;
                socket.onmessage = (e) => { try {
                    const event = JSON.parse(e.data);
                    if (event.event === 'inbox.changed') {
                        this.loadConvs(true);
                        if (this.state.selected)
                            this.loadDetail(this.state.selected, true);
                    }
                }
                catch (err) { } };
                socket.onclose = () => { if (this.ws === socket && this.state.me) {
                    this.reconnectTimer = setTimeout(() => this.connectRealtime(), 6500);
                } };
            }
            catch (e) { }
        };
        this.tick = async () => { if (!this.state.me || document.hidden)
            return; if (this.state.view === 'inbox') {
            await this.loadConvs(true);
            if (this.state.selected)
                await this.loadDetail(this.state.selected, true);
            await this.loadAlerts();
        } };
        this.loadShared = async () => { try {
            const [team, templates, alerts, views] = await Promise.all([request('/team'), request('/quick-replies'), request('/alerts'), request('/views')]);
            this.setState({ team, templates, alerts, views });
        }
        catch (e) {
            this.notify(e.message);
        } };
        this.loadAlerts = async () => { try {
            this.setState({ alerts: await request('/alerts') });
        }
        catch (e) { } };
        this.saveTemplate = () => this.run(async () => { await request('/quick-replies', { method: 'POST', body: JSON.stringify({ title: this.state.templateName, body: this.state.templateBody }) }); this.setState({ templateName: '', templateBody: '' }); this.setState({ templates: await request('/quick-replies') }); this.notify('Шаблон сохранён'); });
        this.deleteTemplate = (id) => this.run(async () => { await request('/quick-replies/' + id, { method: 'DELETE' }); this.setState({ templates: await request('/quick-replies') }); });
        this.changeAvailability = (id, available) => this.run(async () => { await request('/team/' + id + '/availability', { method: 'PATCH', body: JSON.stringify({ available }) }); this.setState({ team: await request('/team') }); });
        this.syncAvito = (id) => this.run(async () => { const result = await request('/integrations/' + id + '/sync', { method: 'POST' }); await this.loadView('integrations'); await this.loadConvs(); this.notify('Авито: получено ' + result.new_inbound_messages + ' новых сообщений'); });
        this.savePrivacy = () => this.run(async () => { await request('/organization/privacy', { method: 'PATCH', body: JSON.stringify({ retention_days: Number(this.state.privacy.retention_days), sla_minutes: Number(this.state.privacy.sla_minutes) }) }); this.notify('Политика хранения и SLA обновлены'); });
        this.saveLocalization = () => this.run(async () => { const data = await request('/organization/localization', { method: 'PATCH', body: JSON.stringify({ currency: this.state.localization.currency, timezone: this.state.localization.timezone }) }); this.setState({ me: { ...this.state.me, organization: { ...this.state.me.organization, ...data } } }); this.notify('Региональные настройки сохранены'); });
        this.pauseDispatch = () => {
            const s = this.state;
            const channel_id = s.opsPauseChannel || null;
            const scope = channel_id ? 'выбранного аккаунта' : 'всей компании';
            if (!window.confirm('Временно остановить НОВЫЕ внешние отправки ' + scope + '? Уже начатый запрос к площадке может завершиться.'))
                return;
            this.run(async () => {
                await request('/operations/dispatch-pauses', { method: 'POST', body: JSON.stringify({ channel_id, reason_code: s.opsPauseReason, minutes: s.opsPauseMinutes === 'unlimited' ? null : Number(s.opsPauseMinutes) }) });
                await this.loadView('operations');
                this.notify('Временная пауза установлена. Входящие продолжают работать.');
            });
        };
        this.resumeDispatch = (channel_id) => {
            if (!window.confirm('Снять временную паузу ' + (channel_id ? 'этого аккаунта' : 'всей компании') + '? Убедитесь, что причина инцидента устранена.'))
                return;
            this.run(async () => { await request('/operations/dispatch-pauses/resume', { method: 'POST', body: JSON.stringify({ channel_id }) }); await this.loadView('operations'); this.notify('Временная пауза снята'); });
        };
        this.exportSafeSupport = () => this.run(async () => {
            const data = await request('/operations/support-bundle');
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const uri = URL.createObjectURL(blob);
            const el = document.createElement('a');
            try {
                el.href = uri;
                el.download = 'osmanx-omnichat-r36-support.json';
                document.body.appendChild(el);
                el.click();
                el.remove();
            }
            finally {
                URL.revokeObjectURL(uri);
            }
            this.notify('Отчёт сохранён без переписок и персональных данных');
        });
        this.loadJobEvents = (job_id) => this.run(async () => {
            const result = await request('/operations/delivery-events?job_id=' + encodeURIComponent(job_id));
            this.setState({ selectedJobEvents: { job_id, events: result.events, truncated: result.truncated } });
        });
        this.exportWorkspace = () => this.run(async () => { const data = await request('/organization/export'); const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = 'osmanx-omnichat-export.json'; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); this.notify('Экспорт создан из ваших данных'); });
        this.toggleNotifications = () => { if (!('Notification' in window)) {
            this.notify('Браузер не поддерживает уведомления');
            return;
        } Notification.requestPermission().then(v => this.notify(v === 'granted' ? 'Уведомления разрешены' : 'Разрешение на уведомления не предоставлено')); };
        this.run = async (action) => { try {
            this.setState({ loading: true });
            await action();
        }
        catch (e) {
            this.notify(e.message || 'Ошибка запроса');
        }
        finally {
            this.setState({ loading: false });
        } };
        this.login = () => this.run(async () => {
            const s = this.state;
            const endpoint = s.authMode === 'register' ? '/auth/register' : s.authMode === 'login' ? '/auth/login' : '/demo/start';
            const body = s.authMode === 'register' ? { company: s.authCompany, name: s.authName, email: s.authEmail, password: s.authPassword } : { email: s.authEmail, password: s.authPassword };
            await request(endpoint, { method: 'POST', body: JSON.stringify(body) });
            const landing = s.authMode === 'register' ? 'start' : 'inbox';
            this.setState({ view: landing, selected: null });
            history.replaceState({}, '', landing === 'start' ? '/?view=start' : '/');
            await this.boot();
            this.notify(s.authMode === 'demo' ? 'Демопространство создано. Все данные тестовые.' : 'Добро пожаловать в OMNICHAT');
        });
        this.loadSessions = () => this.run(async () => { const sessions = await request('/auth/sessions'); this.setState({ sessions }); });
        this.revokeOtherSessions = () => this.run(async () => { const r = await request('/auth/sessions/revoke-others', { method: 'POST' }); this.notify('Сеансы на других устройствах завершены: ' + r.revoked); this.setState({ sessions: await request('/auth/sessions') }); });
        this.revokeAllSessions = () => this.run(async () => { if (!window.confirm('Завершить сеансы на всех устройствах, включая это?'))
            return; await request('/auth/sessions/revoke-all', { method: 'POST' }); this.drafts = {}; this.pendingSend = {}; if (this.ws) {
            this.ws.close();
            this.ws = null;
        } if (this.reconnectTimer)
            clearTimeout(this.reconnectTimer); this.setState({ me: null, selected: null, detail: null, reply: '', authMode: 'login', quickstart: null, sessions: null }); this.notify('Все сеансы завершены. Для продолжения войдите снова.'); });
        this.logout = () => this.run(async () => { await request('/auth/logout', { method: 'POST' }); this.drafts = {}; this.pendingSend = {}; this.setState({ me: null, selected: null, detail: null, reply: '', authMode: 'login', quickstart: null }); if (this.ws) {
            this.ws.close();
            this.ws = null;
        } if (this.reconnectTimer)
            clearTimeout(this.reconnectTimer); });
        this.loadView = async (view) => {
            if (view === 'start') {
                this.setState({ quickstart: await request('/quickstart') });
                return;
            }
            if (view === 'command') {
                this.setState({ command: await request('/command-center') });
                return;
            }
            if (view === 'inbox') {
                await this.loadConvs();
                return;
            }
            if (view === 'contacts' || view === 'deals')
                this.setState({ contacts: await request('/contacts') });
            if (view === 'analytics')
                this.setState({ analytics: await request('/analytics') });
            if (view === 'rules')
                this.setState({ rules: await request('/rules') });
            if (view === 'integrations') {
                const [integrations, integrationGuide] = await Promise.all([request('/integrations'), request('/integrations/guide')]);
                let messengerPages = [];
                if (['owner', 'admin'].includes(this.state.me?.role)) {
                    try {
                        messengerPages = (await request('/integrations/messenger/pages')).pages || [];
                    }
                    catch (e) { }
                }
                const owned = integrations.connections.find((c) => c.mode === 'live' && c.status !== 'disconnected');
                this.setState({ integrations, integrationGuide, messengerPages,
                    focusedProvider: this.state.focusedProvider || owned?.provider || 'telegram' });
            }
            if (view === 'websites')
                this.setState({ sites: await request('/website-widgets') });
            if (view === 'operations') {
                const params = new URLSearchParams({ limit: '30' });
                if (this.state.inboundTriageStatus)
                    params.set('status', this.state.inboundTriageStatus);
                const [operations, operationsJobs, triage, inboundHealth, inboundIntegrity, dispatchPauses, deliveryTelemetry] = await Promise.all([
                    request('/operations/overview'), request('/operations/outbox'),
                    request('/operations/inbound/triage?' + params.toString()), request('/operations/inbound/health'), request('/operations/inbound/integrity'),
                    request('/operations/dispatch-pauses'), request('/operations/delivery-telemetry')
                ]);
                this.setState({ operations, operationsJobs, operationsInboundJobs: triage.items, inboundHealth, inboundIntegrity, dispatchPauses, deliveryTelemetry,
                    inboundTriageCursor: triage.next_cursor });
            }
            if (view === 'team')
                this.setState({ team: await request('/team') });
            if (view === 'settings') {
                this.setState({ plans: await request('/plans') });
                if (['owner', 'admin'].includes(this.state.me?.role || '')) {
                    const [privacy, localization] = await Promise.all([request('/organization/privacy'), request('/organization/localization')]);
                    this.setState({ privacy, localization });
                }
            }
        };
        this.changeView = (view) => this.run(async () => { this.setState({ view, sidebarOpen: false }); history.replaceState({}, '', view === 'inbox' ? '/' : '/?view=' + view); await this.loadView(view); });
        this.loadConvs = async (silent = false) => {
            try {
                const s = this.state;
                const params = new URLSearchParams();
                if (s.search)
                    params.set('q', s.search);
                if (s.channelFilter)
                    params.set('channel', s.channelFilter);
                if (s.statusFilter)
                    params.set('status', s.statusFilter);
                if (s.archivedFilter)
                    params.set('archived', 'true');
                if (s.assignedFilter)
                    params.set('assigned', s.assignedFilter);
                if (s.priorityFilter)
                    params.set('priority', s.priorityFilter);
                if (s.sortFilter)
                    params.set('sort', s.sortFilter);
                const convs = await request('/conversations?' + params.toString());
                if (silent && this.state.convs.length) {
                    const old = new Map(this.state.convs.map((x) => [x.id, x.unread_count]));
                    const changed = convs.find((c) => (old.get(c.id) === undefined && c.unread_count > 0) || (c.unread_count > (old.get(c.id) || 0)));
                    if (changed && !s.me.organization.is_demo) {
                        this.notify('Новое обращение: ' + changed.contact_name);
                        if ('Notification' in window && Notification.permission === 'granted')
                            new Notification('OSMANX OMNICHAT', { body: changed.contact_name + ' · ' + providerName(changed.channel) });
                    }
                }
                this.setState({ convs });
                if (!this.state.selected && convs.length && !silent)
                    this.select(convs[0].id, window.innerWidth <= 680);
            }
            catch (e) {
                if (!silent)
                    this.notify(e.message);
            }
        };
        this.loadDetail = async (id, silent = false) => {
            try {
                const d = await request('/conversations/' + encodeURIComponent(id));
                if (this.state.selected !== id)
                    return;
                const current = this.state.detail;
                const scroller = this.chatScroll;
                const wasAtBottom = !!scroller && scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 90;
                if (current?.conversation?.id === id) {
                    const byId = new Map((current.messages || []).map((m) => [m.id, m]));
                    for (const m of d.messages)
                        byId.set(m.id, m);
                    d.messages = Array.from(byId.values()).sort((a, b) => a.created_at - b.created_at || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
                    d.message_paging = current.message_paging || d.message_paging;
                }
                this.setState({ detail: d, contactDraft: this.state.contactDraft && this.state.contactDraft.id === d.contact.id ? this.state.contactDraft : { ...d.contact } }, () => {
                    if (this.chatScroll && (!current || wasAtBottom))
                        this.chatScroll.scrollTop = this.chatScroll.scrollHeight;
                });
                return d; // Allows read receipt to use the exact visible snapshot version.
            }
            catch (e) {
                if (!silent)
                    this.notify(e.message);
                return null;
            }
        };
        this.loadOlderMessages = async () => {
            const d = this.state.detail, id = d?.conversation?.id;
            const cursor = d?.message_paging?.next_before;
            if (!id || !cursor || this.historyLoading)
                return;
            this.historyLoading = true;
            this.setState({ olderLoading: true });
            const scroller = this.chatScroll;
            const priorHeight = scroller?.scrollHeight || 0, priorTop = scroller?.scrollTop || 0;
            try {
                const page = await request('/conversations/' + encodeURIComponent(id) + '/messages?' + new URLSearchParams({ before: cursor, limit: '120' }));
                if (this.state.selected !== id || this.state.detail?.conversation?.id !== id)
                    return;
                const latest = this.state.detail;
                const byId = new Map(page.messages.map((m) => [m.id, m]));
                for (const m of latest.messages)
                    byId.set(m.id, m);
                const messages = Array.from(byId.values()).sort((a, b) => a.created_at - b.created_at || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
                this.setState({ detail: { ...latest, messages, message_paging: page.message_paging } }, () => {
                    if (this.chatScroll === scroller && scroller) {
                        scroller.scrollTop = priorTop + scroller.scrollHeight - priorHeight;
                    }
                });
            }
            catch (e) {
                this.notify(readableError(e.message));
            }
            finally {
                this.historyLoading = false;
                this.setState({ olderLoading: false });
            }
        };
        this.select = (id, autoMobile = false) => {
            const previous = this.state.selected;
            if (previous && this.state.reply.trim())
                this.drafts[previous] = this.state.reply;
            this.setState({ selected: id, detail: null, olderLoading: false, tab: 'info', activity: [], mobilePane: autoMobile ? 'list' : 'chat', customerOpen: window.innerWidth >= 1260, customerExtras: false, followupEditing: false, tagEditing: false, showEmoji: false, showQuickReplies: false, chatActionsOpen: false, reply: this.drafts[id] || '' }, () => this.run(async () => {
                const loaded = await this.loadDetail(id);
                if (autoMobile || !loaded || this.state.selected !== id)
                    return;
                let changedWhileReading = false;
                try {
                    const seen = await request(`/conversations/${id}/read`, { method: 'POST', body: JSON.stringify({ expected_version: loaded.conversation.version }) });
                    if (this.state.selected === id) {
                        if (this.state.detail?.conversation?.version === loaded.conversation.version) {
                            const d = this.state.detail;
                            this.setState({ detail: { ...d, conversation: { ...d.conversation, version: seen.version, unread_count: 0 } } });
                        }
                        else
                            await this.loadDetail(id, true);
                    }
                }
                catch (e) {
                    // Concurrent inbound messages must remain unread; show the new state.
                    changedWhileReading = true;
                    if (this.state.selected === id) {
                        await this.loadDetail(id, true);
                        this.notify('Появилось новое сообщение — оно осталось непрочитанным.');
                    }
                }
                // The conflict already informed this operator. Suppress a second, generic
                // "new conversation" toast that would hide the more useful explanation.
                await this.loadConvs(!changedWhileReading);
            }));
        };
        this.loadActivity = async (id) => { try {
            const activity = await request('/conversations/' + id + '/activity');
            if (this.state.selected === id)
                this.setState({ activity });
        }
        catch (e) {
            this.notify(e.message);
        } };
        this.setPriority = (priority) => {
            const d = this.state.detail;
            if (!d)
                return;
            this.run(async () => {
                const updated = await request('/conversations/' + d.conversation.id + '/priority', { method: 'PATCH', body: JSON.stringify({ priority, expected_version: d.conversation.version }) });
                this.setState({ detail: { ...d, conversation: updated } });
                await this.loadConvs(true);
                await this.loadActivity(d.conversation.id);
                this.notify('Приоритет диалога изменён');
            });
        };
        this.createSavedView = () => this.run(async () => {
            const s = this.state;
            const filters = { channel: s.channelFilter, status: s.statusFilter, priority: s.priorityFilter, assigned: s.assignedFilter, archived: s.archivedFilter, sort: s.sortFilter };
            const created = await request('/views', { method: 'POST', body: JSON.stringify({ name: s.viewName, shared: s.viewShared, filters }) });
            this.setState({ views: [created, ...s.views], viewName: '', viewShared: false, modal: '' });
            this.notify('Представление сохранено');
        });
        this.deleteSavedView = (id) => this.run(async () => { await request('/views/' + id, { method: 'DELETE' }); this.setState({ views: this.state.views.filter((x) => x.id !== id) }); this.notify('Представление удалено'); });
        this.applySavedView = (view) => {
            const f = view.filters || {};
            this.setState({ view: 'inbox', channelFilter: f.channel || '', statusFilter: f.status || '', priorityFilter: f.priority || '', assignedFilter: f.assigned || '', archivedFilter: !!f.archived, sortFilter: f.sort || 'recent', selected: null, detail: null, mobilePane: 'list' }, () => this.loadConvs());
            history.replaceState({}, '', '/');
        };
        this.openQueueConversation = (id) => {
            if (this.state.selected && this.state.reply.trim())
                this.drafts[this.state.selected] = this.state.reply;
            this.setState({ view: 'inbox', search: '', channelFilter: '', statusFilter: '', priorityFilter: '', assignedFilter: '', archivedFilter: false, sortFilter: 'recent', selected: id, detail: null, mobilePane: 'chat', reply: this.drafts[id] || '' }, async () => { await this.loadConvs(true); await this.loadDetail(id); });
            history.replaceState({}, '', '/');
        };
        this.changeSearch = (text) => { this.setState({ search: text }); if (this.searchTimer)
            clearTimeout(this.searchTimer); this.searchTimer = setTimeout(() => this.loadConvs(), 250); };
        this.changeFilter = (key, value) => { this.setState({ [key]: value, selected: null, detail: null, mobilePane: 'list' }, () => this.loadConvs()); };
        this.changeReply = (value) => {
            const id = this.state.selected;
            if (id) {
                if (value)
                    this.drafts[id] = value;
                else
                    delete this.drafts[id];
            }
            this.setState({ reply: value });
        };
        this.send = async () => {
            const d = this.state.detail, s = this.state;
            if (!d || !s.reply.trim() || this.sending)
                return;
            const id = d.conversation.id, body = s.reply.trim();
            if (outgoingSize(d.conversation.channel, body) > outgoingLimit(d.conversation.channel)) {
                this.notify('Сообщение слишком длинное для этой площадки. Укоротите текст.');
                return;
            }
            const pending = this.pendingSend[id];
            const nonce = pending && pending.body === body ? pending.nonce :
                (window.crypto?.randomUUID ? window.crypto.randomUUID() : 'nonce-' + Date.now() + '-' + Math.random());
            this.pendingSend[id] = { body, nonce };
            this.sending = true;
            this.setState({ loading: true });
            try {
                const data = await request(`/conversations/${id}/reply`, { method: 'POST', body: JSON.stringify({ body, expected_version: d.conversation.version, client_nonce: nonce }) });
                delete this.pendingSend[id];
                delete this.drafts[id];
                if (this.state.selected === id) {
                    const keepText = this.state.reply !== s.reply;
                    this.setState({ reply: keepText ? this.state.reply : '', detail: { ...d, conversation: data.conversation,
                            messages: d.messages.some((m) => m.id === data.message.id) ? d.messages : [...d.messages, data.message] } });
                    if (keepText)
                        this.drafts[id] = this.state.reply;
                    await this.loadDetail(id);
                }
                await this.loadConvs(true);
                this.notify(data.conversation.outbound_paused ? 'Ответ сохранён в очереди. Отправка приостановлена администратором.' : data.message.delivery_status === 'queued' ? 'Ответ передан в очередь. Статус доставки появится в переписке.' : 'Ответ сохранён в переписке.');
            }
            catch (e) {
                this.notify(readableError(e.message || ''));
                if (this.state.selected === id)
                    await this.loadDetail(id, true); // refresh server version, keep draft and idempotency nonce
            }
            finally {
                this.sending = false;
                this.setState({ loading: false });
            }
        };
        this.openWaTemplates = async () => {
            const c = this.state.detail?.conversation;
            if (!c)
                return;
            this.setState({ modal: 'wa-template', waTemplates: [], waConsent: false, waSelected: '', waParams: [], waLoading: true });
            try {
                const result = await request(`/conversations/${c.id}/whatsapp-templates`);
                this.setState({ waTemplates: result.templates, waConsent: result.consent_recorded,
                    waSelected: result.templates[0] ? result.templates[0].name + '|' + result.templates[0].language : '',
                    waParams: Array(result.templates[0]?.param_count || 0).fill(''), waLoading: false });
            }
            catch (e) {
                this.notify(e.message);
                this.setState({ waLoading: false });
            }
        };
        this.recordWaConsent = () => this.run(async () => {
            const c = this.state.detail?.conversation;
            if (!c)
                return;
            const response = await request(`/conversations/${c.id}/whatsapp-consent`, { method: 'POST',
                body: JSON.stringify({ source: this.state.waConsentSource, confirmed: this.state.waConsentCheckbox }) });
            this.setState({ waConsent: response.consent_recorded });
            this.notify('Факт согласия записан со слов сотрудника. Платформа не проверяла его автоматически.');
        });
        this.revokeWaConsent = () => this.run(async () => {
            const c = this.state.detail?.conversation;
            if (!c)
                return;
            await request(`/conversations/${c.id}/whatsapp-consent/revoke`, { method: 'POST' });
            this.setState({ waConsent: false });
            this.notify('Согласие отозвано: новые шаблоны нельзя отправлять');
        });
        this.sendWaTemplate = () => this.run(async () => {
            const s = this.state, c = s.detail?.conversation;
            if (!c)
                return;
            const selection = (s.waTemplates || []).find((t) => t.name + '|' + t.language === s.waSelected);
            if (!selection)
                return;
            const fingerprint = JSON.stringify([selection.name, selection.language, s.waParams]);
            const key = 'wa:' + c.id, pending = this.pendingSend[key];
            const nonce = pending?.body === fingerprint ? pending.nonce : (window.crypto?.randomUUID ? window.crypto.randomUUID() :
                'template-' + Date.now() + '-' + Math.random());
            this.pendingSend[key] = { body: fingerprint, nonce };
            const response = await request(`/conversations/${c.id}/whatsapp-template`, { method: 'POST',
                body: JSON.stringify({ name: selection.name, language: selection.language,
                    parameters: s.waParams, expected_version: c.version, client_nonce: nonce }) });
            delete this.pendingSend[key];
            this.setState({ modal: '' });
            await this.loadDetail(c.id);
            await this.loadConvs(true);
            this.notify(response.duplicate ? 'Этот шаблон уже находится в переписке' :
                'Одобренный шаблон добавлен в очередь. Доставка ещё не подтверждена.');
        });
        this.updateConv = (kind, value) => {
            const d = this.state.detail;
            if (!d)
                return;
            this.run(async () => {
                const id = d.conversation.id;
                const path = kind === 'status' ? '/status' : kind === 'assign' ? '/assign' : '/pin';
                const body = kind === 'status' ? { status: value, expected_version: d.conversation.version } :
                    kind === 'assign' ? { user_id: value, expected_version: d.conversation.version } :
                        { expected_version: d.conversation.version };
                try {
                    await request(`/conversations/${id}${path}`, { method: 'PATCH', body: JSON.stringify(body) });
                }
                catch (e) {
                    if (/Диалог изменён|Диалог занят/.test(e.message || '')) {
                        await this.loadDetail(id);
                        await this.loadConvs(true);
                        throw new Error('Коллега изменил диалог. Данные обновлены — проверьте их и повторите действие.');
                    }
                    throw e;
                }
                await this.loadDetail(id);
                await this.loadConvs(true);
            });
        };
        this.addNote = () => { const d = this.state.detail; if (!d || !this.state.note.trim())
            return; this.run(async () => { await request(`/conversations/${d.conversation.id}/notes`, { method: 'POST', body: JSON.stringify({ body: this.state.note }) }); this.setState({ note: '' }); await this.loadDetail(d.conversation.id); }); };
        this.saveContact = (contact) => this.run(async () => { const patch = { ...contact }; delete patch.id; await request('/contacts/' + contact.id, { method: 'PATCH', body: JSON.stringify(patch) }); this.notify('Карточка клиента сохранена'); if (this.state.view === 'contacts' || this.state.view === 'deals')
            await this.loadView(this.state.view); if (this.state.selected)
            await this.loadDetail(this.state.selected); });
        this.addCustomerTag = () => { const s = this.state; const draft = s.contactDraft; if (!draft)
            return; const tag = s.tagInput.trim(); if (!tag)
            return; const tags = Array.from(new Set([...(draft.tags || []), tag])); const next = { ...draft, tags }; this.setState({ tagInput: '', tagEditing: false, contactDraft: next }); this.saveContact(next); };
        this.removeCustomerTag = (tag) => { const draft = this.state.contactDraft; if (!draft)
            return; const next = { ...draft, tags: (draft.tags || []).filter((v) => v !== tag) }; this.setState({ contactDraft: next }); this.saveContact(next); };
        this.appendEmoji = (emoji) => { this.changeReply(this.state.reply + emoji); this.setState({ showEmoji: false }); };
        this.demoIncoming = () => { const d = this.state.detail; if (!d || !this.state.demoInbound.trim())
            return; this.run(async () => { await request('/demo/incoming', { method: 'POST', body: JSON.stringify({ conversation_id: d.conversation.id, body: this.state.demoInbound }) }); this.setState({ demoInbound: '' }); await this.loadDetail(d.conversation.id); await this.loadConvs(true); this.notify('Тестовое входящее добавлено'); }); };
        this.toggleTheme = () => { const next = !this.state.light; localStorage.setItem('omnichat_theme', next ? 'light' : 'dark'); document.body.classList.toggle('light', next); this.setState({ light: next }); };
        this.oauth = (provider) => this.run(async () => { const { url } = await request('/integrations/oauth-start/' + provider, { method: 'POST' }); window.location.href = url; });
        this.connectBot = () => this.run(async () => {
            const response = await request('/integrations/bots', { method: 'POST', body: JSON.stringify({ provider: this.state.botProvider, access_token: this.state.connectToken, group_id: this.state.botGroupId || null, confirmation_token: this.state.botConfirmation || null }) });
            this.setState({ modal: '', connectToken: '', botGroupId: '', botConfirmation: '', botConnectedInfo: response });
            await this.loadView('integrations');
            this.notify('Аккаунт проверен. Настройте защищённый webhook для приёма обращений.');
        });
        this.activateBot = (id) => this.run(async () => {
            const result = await request('/integrations/' + id + '/activate-webhook', { method: 'POST' });
            await this.loadView('integrations');
            this.notify(result.message);
        });
        this.connectWhatsApp = () => this.run(async () => {
            const result = await request('/integrations/manual', { method: 'POST', body: JSON.stringify({ provider: 'whatsapp', access_token: this.state.connectToken, phone_number_id: this.state.connectPhone, waba_id: this.state.connectWaba || null }) });
            this.setState({ modal: '', connectToken: '', connectPhone: '', connectWaba: '' });
            await this.loadView('integrations');
            this.notify(result.status === 'connected' ? 'Канал прошёл проверку' : 'Номер подтверждён. Подключите подписку WABA и проверьте входящее сообщение.');
        });
        this.disconnect = (id) => { if (!window.confirm('Отключить канал? Доступ к его сообщениям в OSMANX прекратится.'))
            return; this.run(async () => { const r = await request('/integrations/' + id + '/disconnect', { method: 'POST' }); await this.loadView('integrations'); this.notify(r?.message || 'Подключение отключено'); }); };
        this.pauseCompanyOutbound = (pausedAt) => {
            const paused = pausedAt !== null && pausedAt !== undefined;
            const warning = paused
                ? 'Возобновить новые исходящие сообщения ВСЕХ аккаунтов компании? Убедитесь, что инцидент устранён. Индивидуальные паузы сохранятся.'
                : 'АВАРИЙНО ОСТАНОВИТЬ НОВЫЕ ИСХОДЯЩИЕ ВСЕХ АККАУНТОВ? Входящие продолжат поступать. Запросы, уже начатые на площадке, могут завершиться.';
            if (!window.confirm(warning))
                return;
            this.run(async () => {
                const endpoint = paused ? '/operations/outbound/resume' : '/operations/outbound/pause';
                const body = paused ? { expected_paused_at: pausedAt, acknowledge_inflight: true }
                    : { reason: 'security_review', acknowledge_inflight: true };
                const result = await request(endpoint, { method: 'POST', body: JSON.stringify(body) });
                await this.loadView('operations');
                if (this.state.selected)
                    await this.loadDetail(this.state.selected, true);
                await this.loadConvs(true);
                this.notify(result.message);
            });
        };
        this.pauseOutbound = (id, paused) => {
            const warning = paused ? 'Возобновить новые исходящие сообщения через этот аккаунт? Сначала проверьте причину остановки.' : 'Приостановить НОВЫЕ исходящие сообщения этого аккаунта? Входящие продолжат работать. Отправки, уже прошедшие контрольную точку, могут завершиться.';
            if (!window.confirm(warning))
                return;
            this.run(async () => {
                const path = '/integrations/' + id + (paused ? '/outbound-resume' : '/outbound-pause');
                const options = { method: 'POST' };
                if (!paused)
                    options.body = JSON.stringify({ reason: 'security_review', acknowledge_inflight: true });
                const result = await request(path, options);
                await this.loadView('integrations');
                this.notify(result.message);
            });
        };
        this.diagnoseChannel = (id) => this.run(async () => {
            const data = await request('/integrations/' + id + '/diagnostics');
            this.setState({ channelDiagnostics: data, channelDiagnosticsFor: id }, () => {
                const block = document.querySelector('.onboarding-diagnostics');
                if (block)
                    block.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
        this.verifyProviderHook = (id) => this.run(async () => {
            const result = await request('/integrations/' + id + '/verify-provider-webhook', { method: 'POST' });
            await this.loadView('integrations');
            const data = await request('/integrations/' + id + '/diagnostics');
            this.setState({ channelDiagnostics: { ...data, provider_error: result.provider_error || null, pending_updates: result.pending_updates }, channelDiagnosticsFor: id }, () => {
                document.querySelector('.onboarding-diagnostics')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
            this.notify(result.message);
        });
        this.probeChannel = (id) => this.run(async () => {
            const report = await request('/integrations/' + id + '/probe', { method: 'POST' });
            await this.loadView('integrations');
            const diagnostic = await request('/integrations/' + id + '/diagnostics');
            this.setState({ channelDiagnostics: diagnostic, channelDiagnosticsFor: id }, () => {
                document.querySelector('.onboarding-diagnostics')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
            this.notify(report.next_step);
        });
        this.checkChannel = (id) => this.run(async () => {
            const result = await request('/integrations/' + id + '/check-access', { method: 'POST' });
            await this.loadView('integrations');
            this.notify(result.message);
        });
        this.registerWhatsAppPhone = () => this.run(async () => {
            const result = await request('/integrations/' + this.state.registerPhoneChannel + '/register-phone', {
                method: 'POST', body: JSON.stringify({ pin: this.state.registrationPin })
            });
            this.setState({ modal: '', registerPhoneChannel: '', registrationPin: '' });
            await this.loadView('integrations');
            this.notify(result.message);
        });
        this.rotateChannelToken = () => this.run(async () => {
            await request('/integrations/' + this.state.rotateChannel + '/rotate-token', { method: 'POST', body: JSON.stringify({ access_token: this.state.rotateToken }) });
            this.setState({ modal: '', rotateChannel: '', rotateToken: '' });
            await this.loadView('integrations');
            this.notify('Токен заменён. Проверьте webhook и входящее сообщение.');
        });
        this.vkCallback = (id) => this.run(async () => {
            const setup = await request('/integrations/' + id + '/vk-callback-setup');
            this.setState({ channelDiagnostics: { ...this.state.channelDiagnostics, ...setup, secretVisible: true }, channelDiagnosticsFor: id });
        });
        this.connectMessengerPage = (id) => this.run(async () => {
            const result = await request('/integrations/messenger/pages/' + id + '/connect', { method: 'POST' });
            await this.loadView('integrations');
            this.notify(result.message);
        });
        this.createCompany = () => this.run(async () => {
            const org = await request('/organizations', { method: 'POST', body: JSON.stringify({ name: this.state.newOrganization.trim() }) });
            await request('/auth/switch/' + org.id, { method: 'POST' });
            window.location.assign('/?view=integrations');
        });
        this.switchCompany = (id) => this.run(async () => {
            await request('/auth/switch/' + id, { method: 'POST' });
            window.location.assign('/?view=integrations');
        });
        this.metaMessage = (event) => {
            if (!this.metaFlow || !['https://www.facebook.com', 'https://web.facebook.com'].includes(event.origin))
                return;
            let packet = event.data;
            if (typeof packet === 'string') {
                try {
                    packet = JSON.parse(packet);
                }
                catch (e) {
                    return;
                }
            }
            if (packet?.type !== 'WA_EMBEDDED_SIGNUP')
                return;
            const data = packet.data || {};
            if (packet.event === 'FINISH' && data.waba_id && data.phone_number_id) {
                this.metaFlow.waba_id = String(data.waba_id);
                this.metaFlow.phone_number_id = String(data.phone_number_id);
                this.completeMetaIfReady();
            }
            if (packet.event === 'CANCEL')
                this.notify('Регистрация WhatsApp отменена в Meta.');
        };
        this.completeMetaIfReady = () => {
            const flow = this.metaFlow;
            if (!flow || flow.submitting || !flow.code || !flow.waba_id || !flow.phone_number_id)
                return;
            flow.submitting = true;
            this.run(async () => {
                const result = await request('/integrations/whatsapp/embedded/complete', { method: 'POST', body: JSON.stringify({ state: flow.state, code: flow.code, waba_id: flow.waba_id, phone_number_id: flow.phone_number_id }) });
                this.metaFlow = null;
                await this.loadView('integrations');
                this.notify(result.message);
            });
        };
        this.prepareMetaWhatsApp = () => this.run(async () => {
            // Preparation is asynchronous. The actual popup must open synchronously on
            // the NEXT user click, otherwise browsers may block it after an await.
            const flow = await request('/integrations/whatsapp/embedded/start', { method: 'POST' });
            const w = window;
            if (!w.FB) {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = 'https://connect.facebook.net/ru_RU/sdk.js';
                    script.async = true;
                    script.onload = () => resolve();
                    script.onerror = () => reject(new Error('Meta SDK не загрузился. Проверьте доступность Facebook.'));
                    document.head.appendChild(script);
                });
            }
            w.FB.init({ appId: flow.app_id, autoLogAppEvents: false, xfbml: false, version: flow.graph_version });
            this.setState({ metaSession: { ...flow, prepared_at: Date.now() } });
            this.notify('Meta подготовлена. Нажмите «Продолжить в Meta», чтобы открыть официальный вход.');
        });
        this.launchMetaWhatsApp = () => {
            const flow = this.state.metaSession;
            if (!flow || Date.now() - flow.prepared_at > 12 * 60 * 1000) {
                this.notify('Сеанс истёк. Подготовьте подключение ещё раз.');
                return;
            }
            const w = window;
            if (!w.FB) {
                this.notify('Meta SDK не загружен');
                return;
            }
            this.metaFlow = { ...flow, code: '', waba_id: '', phone_number_id: '', submitting: false };
            // Direct gesture-driven FB.login is required by popup blockers.
            w.FB.login((response) => {
                if (!this.metaFlow)
                    return;
                const code = response?.authResponse?.code;
                if (!code) {
                    this.notify('Meta не предоставила код авторизации. Проверьте разрешения приложения.');
                    return;
                }
                this.metaFlow.code = String(code);
                this.completeMetaIfReady();
            }, { config_id: flow.config_id, response_type: 'code', override_default_response_type: true,
                extras: { setup: {}, featureType: 'whatsapp_embedded_signup', sessionInfoVersion: '3' } });
        };
        this.createRule = () => this.run(async () => { await request('/rules', { method: 'POST', body: JSON.stringify({ name: this.state.ruleName || 'Новое правило', event: 'message_received', condition_type: this.state.ruleCondition, condition_value: this.state.ruleTerm, action_type: this.state.ruleAction, action_value: this.state.ruleActionValue, enabled: true }) }); this.setState({ modal: '', ruleName: '', ruleTerm: '' }); await this.loadView('rules'); this.notify('Правило активно'); });
        this.toggleRule = (id) => this.run(async () => { await request('/rules/' + id + '/toggle', { method: 'PATCH' }); await this.loadView('rules'); });
        this.invite = () => this.run(async () => { const data = await request('/team/invite', { method: 'POST', body: JSON.stringify({ email: this.state.inviteEmail, role: this.state.inviteRole }) }); this.setState({ inviteToken: data.invite_token }); this.notify('Приглашение создано. Скопируйте токен и передайте сотруднику.'); });
        this.clearSiteForm = () => this.setState({ siteSelected: '', siteName: '', siteOrigins: '', siteGreeting: 'Здравствуйте! Чем можем вам помочь?', siteAccent: '#90b7a7' });
        this.startEditSite = (w) => { this.setState({ siteSelected: w.id, siteName: w.name, siteOrigins: w.allowed_origins.join('\n'), siteGreeting: w.greeting, siteAccent: w.accent }); window.scrollTo({ top: 0, behavior: 'smooth' }); };
        this.saveSiteWidget = () => this.run(async () => { const s = this.state; const payload = { name: s.siteName.trim(), allowed_origins: s.siteOrigins.split(/[\s,]+/).map((v) => v.trim()).filter(Boolean), greeting: s.siteGreeting.trim(), accent: s.siteAccent }; if (!payload.allowed_origins.length)
            throw new Error('Укажите хотя бы один разрешённый адрес сайта (HTTPS в production)'); if (s.siteSelected)
            await request('/website-widgets/' + s.siteSelected, { method: 'PATCH', body: JSON.stringify({ ...payload, enabled: s.sites.find((x) => x.id === s.siteSelected)?.enabled ?? true }) });
        else
            await request('/website-widgets', { method: 'POST', body: JSON.stringify(payload) }); this.clearSiteForm(); await this.loadView('websites'); this.notify('Канал сайта сохранён'); });
        this.toggleSiteWidget = (w) => this.run(async () => { const payload = { name: w.name, allowed_origins: w.allowed_origins, greeting: w.greeting, accent: w.accent, enabled: !w.enabled }; await request('/website-widgets/' + w.id, { method: 'PATCH', body: JSON.stringify(payload) }); await this.loadView('websites'); this.notify(w.enabled ? 'Виджет приостановлен' : 'Виджет включён'); });
        this.rotateSiteWidget = (w) => { if (!window.confirm('Сменить публичный ключ виджета? Старый код перестанет работать на сайте.'))
            return; this.run(async () => { await request('/website-widgets/' + w.id + '/rotate-key', { method: 'POST' }); await this.loadView('websites'); this.notify('Ключ изменён. Обновите код на сайте.'); }); };
        this.copySnippet = (code) => { if (navigator.clipboard?.writeText)
            navigator.clipboard.writeText(code).then(() => this.notify('Код виджета скопирован')).catch(() => this.notify('Браузер запретил копирование. Выделите код вручную.'));
        else
            this.notify('Для копирования из браузера необходимо защищённое соединение HTTPS'); };
        this.repairInboundExpired = () => this.run(async () => {
            const s = this.state;
            if (!s.inboundRepairConfirmed || s.inboundRepairReason.trim().length < 12)
                return;
            const result = await request('/operations/inbound/repair-expired', {
                method: 'POST', body: JSON.stringify({ reason: s.inboundRepairReason.trim(), confirm_expired_only: true })
            });
            this.setState({ modal: '', inboundRepairReason: '', inboundRepairConfirmed: false });
            await this.loadView('operations');
            this.notify('Проверка завершена. Безопасно исправлено: ' + result.changes + '. Активные задачи сохранены.');
        });
        this.loadInboundTriage = (status = '', more = false) => this.run(async () => {
            const params = new URLSearchParams({ limit: '30' });
            if (status)
                params.set('status', status);
            if (more) {
                if (!this.state.inboundTriageCursor)
                    return;
                params.set('before', this.state.inboundTriageCursor);
            }
            const result = await request('/operations/inbound/triage?' + params.toString());
            this.setState({ inboundTriageStatus: status,
                operationsInboundJobs: more ? [...this.state.operationsInboundJobs, ...result.items] : result.items,
                inboundTriageCursor: result.next_cursor });
        });
        this.applyInboundPause = () => this.run(async () => {
            const s = this.state, scope = s.inboundControlScope === 'organization' ? 'organization' : 'channel';
            const body = { scope, channel_id: scope === 'channel' ? s.inboundControlScope : null,
                reason: s.inboundPauseReason.trim() };
            if (body.reason.length < 8)
                throw new Error('Укажите причину длиной от 8 символов');
            await request('/operations/inbound/' + s.inboundPauseAction, { method: 'POST', body: JSON.stringify(body) });
            this.setState({ modal: '', inboundPauseReason: '' });
            await this.loadView('operations');
            this.notify(s.inboundPauseAction === 'pause'
                ? 'Входящие сохраняются, их обработка приостановлена.'
                : 'Обработка входящих возобновлена.');
        });
        this.openInboundBatchPreview = () => this.run(async () => {
            if (!this.state.inboundBatchChannel)
                return;
            const preview = await request('/operations/inbound/retry-batch/preview', {
                method: 'POST', body: JSON.stringify({ channel_id: this.state.inboundBatchChannel, limit: 20 })
            });
            this.setState({ modal: 'inbound-batch', inboundBatchPreview: preview, inboundBatchReason: '' });
        });
        this.refreshInboundBatchPreview = () => this.run(async () => {
            if (!this.state.inboundBatchChannel)
                return;
            const preview = await request('/operations/inbound/retry-batch/preview', {
                method: 'POST', body: JSON.stringify({ channel_id: this.state.inboundBatchChannel, limit: 20 })
            });
            this.setState({ inboundBatchPreview: preview });
            this.notify('Предпросмотр обновлён. Проверьте количество событий перед подтверждением.');
        });
        this.retryInboundBatch = () => this.run(async () => {
            const s = this.state, preview = s.inboundBatchPreview;
            if (!preview || preview.count < 1 || s.inboundBatchReason.trim().length < 8)
                return;
            const result = await request('/operations/inbound/retry-batch-confirm', {
                method: 'POST', body: JSON.stringify({ proof: preview.proof,
                    reason: s.inboundBatchReason.trim() })
            });
            this.setState({ modal: '', inboundBatchReason: '', inboundBatchPreview: null });
            await this.loadView('operations');
            this.notify('Проверено и возвращено в очередь: ' + result.requeued + '. Результат появится в Inbox.');
        });
        this.dismissInbound = () => this.run(async () => {
            const s = this.state, job = s.inboundDismissJob;
            if (!job || !s.inboundDismissConfirmed || s.inboundDismissReason.trim().length < 12)
                return;
            const result = await request('/operations/inbound/' + encodeURIComponent(job.id) + '/dismiss', {
                method: 'POST', body: JSON.stringify({ code: s.inboundDismissCode,
                    reason: s.inboundDismissReason.trim(), confirm_permanent_loss: true })
            });
            this.setState({ modal: '', inboundDismissJob: null, inboundDismissReason: '', inboundDismissConfirmed: false });
            await this.loadView('operations');
            this.notify(result.message || 'Событие закрыто и шифротекст удалён.');
        });
        this.retryInbound = () => this.run(async () => {
            const job = this.state.inboundRetryJob;
            const reason = this.state.inboundRetryReason.trim();
            if (!job || reason.length < 8)
                return;
            await request('/operations/inbound/' + encodeURIComponent(job.id) + '/retry', { method: 'POST', body: JSON.stringify({ reason }) });
            this.setState({ modal: '', inboundRetryJob: null, inboundRetryReason: '' });
            await this.loadView('operations');
            this.notify('Входящее событие возвращено в очередь. После обработки обновите переписки.');
        });
        this.reconcileDelivery = () => this.run(async () => { const s = this.state; if (!s.reconcileJob || s.reconcileEvidence.trim().length < 8)
            return; await request('/operations/outbox/' + s.reconcileJob.id + '/resolve', { method: 'POST', body: JSON.stringify({ status: s.reconcileStatus, evidence: s.reconcileEvidence.trim(), external_id: s.reconcileExternalId || null }) }); this.setState({ modal: '', reconcileJob: null, reconcileEvidence: '', reconcileExternalId: '' }); await this.loadView('operations'); this.notify('Результат проверки доставки записан в журнал действий'); });
        this.cancelQueued = (j) => {
            if (!window.confirm('Отменить ответ, который ещё не отправлен в соцсеть? Если отправка уже началась, OSMANX не позволит отменить её.'))
                return;
            this.run(async () => { await request('/operations/outbox/' + j.id + '/cancel', { method: 'POST' }); await this.loadView('operations'); if (this.state.selected)
                await this.loadDetail(this.state.selected, true); this.notify('Ответ отменён до начала отправки. Клиенту он не передан.'); });
        };
        this.retryVerified = () => this.run(async () => {
            const s = this.state;
            if (!s.outboxRetryJob || !s.outboxRetryVerified || s.outboxRetryEvidence.trim().length < 12)
                return;
            await request('/operations/outbox/' + s.outboxRetryJob.id + '/retry-verified', { method: 'POST', body: JSON.stringify({ verified_not_delivered: true, evidence: s.outboxRetryEvidence.trim() }) });
            this.setState({ modal: '', outboxRetryJob: null, outboxRetryEvidence: '', outboxRetryVerified: false });
            await this.loadView('operations');
            this.notify('Повтор поставлен в очередь. Это ещё не подтверждение доставки.');
        });
        this.claimReply = (release = false) => { const c = this.state.detail?.conversation; if (!c)
            return; this.run(async () => { await request('/conversations/' + c.id + '/' + (release ? 'release' : 'claim'), { method: 'POST', body: release ? undefined : JSON.stringify({ seconds: 120 }) }); await this.loadDetail(c.id); await this.loadConvs(true); this.notify(release ? 'Диалог освобождён' : 'Диалог занят вами на 2 минуты'); }); };
    }
    componentDidMount() { document.body.classList.toggle('light', this.state.light); window.addEventListener('message', this.metaMessage); this.boot(); this.timer = setInterval(() => this.tick(), 7000); document.addEventListener('keydown', this.handleHotkey); }
    componentWillUnmount() { document.removeEventListener('keydown', this.handleHotkey); if (this.timer)
        clearInterval(this.timer); if (this.searchTimer)
        clearTimeout(this.searchTimer); if (this.toastTimer)
        clearTimeout(this.toastTimer); if (this.reconnectTimer)
        clearTimeout(this.reconnectTimer); if (this.ws)
        this.ws.close(); window.removeEventListener('message', this.metaMessage); }
    renderAuth() {
        const s = this.state;
        return React.createElement("div", { className: "quiet-auth-shell" },
            React.createElement("div", { className: "quiet-auth-main" },
                React.createElement("div", { className: "quiet-auth-brand" },
                    React.createElement("span", { className: "brand-symbol", "aria-hidden": "true" }),
                    React.createElement("div", null,
                        React.createElement("strong", null, "OSMANX"),
                        React.createElement("small", null, "OMNICHAT"))),
                React.createElement("div", { className: "quiet-auth-title" },
                    React.createElement("h1", null,
                        "\u0412\u0441\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F.",
                        React.createElement("br", null),
                        React.createElement("span", null, "\u041E\u0434\u043D\u043E \u043C\u0435\u0441\u0442\u043E.")),
                    React.createElement("p", null, "\u0420\u0430\u0431\u043E\u0442\u0430\u0439\u0442\u0435 \u0441 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F\u043C\u0438 \u0438\u0437 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D\u043D\u044B\u0445 \u0441\u043E\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0445 \u0441\u0435\u0442\u0435\u0439 \u0432 \u043E\u0434\u043D\u043E\u043C \u0441\u043F\u043E\u043A\u043E\u0439\u043D\u043E\u043C \u043F\u0440\u043E\u0441\u0442\u0440\u0430\u043D\u0441\u0442\u0432\u0435.")),
                React.createElement("div", { className: "quiet-auth-card" },
                    React.createElement("div", { className: "quiet-auth-modes" },
                        React.createElement("button", { className: s.authMode === 'demo' ? 'selected' : '', onClick: () => this.setState({ authMode: 'demo' }) }, "\u0414\u0435\u043C\u043E\u0432\u0435\u0440\u0441\u0438\u044F"),
                        React.createElement("button", { className: s.authMode === 'login' ? 'selected' : '', onClick: () => this.setState({ authMode: 'login' }) }, "\u0412\u0445\u043E\u0434"),
                        React.createElement("button", { className: s.authMode === 'register' ? 'selected' : '', onClick: () => this.setState({ authMode: 'register' }) }, "\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044F")),
                    React.createElement("h2", null, s.authMode === 'login' ? 'С возвращением' : s.authMode === 'register' ? 'Создать компанию' : 'Посмотрите, как всё устроено'),
                    React.createElement("p", null, s.authMode === 'demo' ? 'Откройте тестовые переписки, CRM и рабочий интерфейс. Реальные аккаунты не затрагиваются.' : s.authMode === 'register' ? 'Создайте отдельное рабочее пространство для своей компании.' : 'Войдите, чтобы продолжить работу с сообщениями.'),
                    s.authMode !== 'demo' ? React.createElement("form", { className: "quiet-auth-form", onSubmit: (e) => { e.preventDefault(); this.login(); } },
                        s.authMode === 'register' && React.createElement(React.Fragment, null,
                            React.createElement("label", null,
                                "\u041A\u043E\u043C\u043F\u0430\u043D\u0438\u044F",
                                React.createElement("input", { value: s.authCompany, required: true, minLength: 2, onChange: (e) => this.setState({ authCompany: e.target.value }), placeholder: "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438" })),
                            React.createElement("label", null,
                                "\u0418\u043C\u044F",
                                React.createElement("input", { value: s.authName, required: true, minLength: 2, onChange: (e) => this.setState({ authName: e.target.value }), placeholder: "\u041A\u0430\u043A \u0432\u0430\u0441 \u0437\u043E\u0432\u0443\u0442?" }))),
                        React.createElement("label", null,
                            "\u042D\u043B\u0435\u043A\u0442\u0440\u043E\u043D\u043D\u0430\u044F \u043F\u043E\u0447\u0442\u0430",
                            React.createElement("input", { type: "email", required: true, value: s.authEmail, onChange: (e) => this.setState({ authEmail: e.target.value }), placeholder: "company@example.com" })),
                        React.createElement("label", null,
                            "\u041F\u0430\u0440\u043E\u043B\u044C",
                            React.createElement("input", { type: "password", required: true, minLength: s.authMode === 'register' ? 12 : 1, value: s.authPassword, onChange: (e) => this.setState({ authPassword: e.target.value }), placeholder: "\u041D\u0435 \u043C\u0435\u043D\u0435\u0435 12 \u0441\u0438\u043C\u0432\u043E\u043B\u043E\u0432 \u0434\u043B\u044F \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438" })),
                        React.createElement("button", { className: "quiet-auth-primary", type: "submit", disabled: s.loading },
                            s.loading ? 'Проверяем...' : s.authMode === 'register' ? 'Создать компанию' : 'Войти',
                            " ",
                            React.createElement(Icon, { name: "arrow", size: 18 }))) : React.createElement("button", { className: "quiet-auth-primary", disabled: s.loading, onClick: this.login },
                        s.loading ? 'Создаём демопространство...' : 'Открыть демоверсию',
                        " ",
                        React.createElement(Icon, { name: "arrow", size: 19 })),
                    React.createElement("div", { className: "quiet-auth-note" },
                        React.createElement(Icon, { name: "shield", size: 14 }),
                        " \u0412 \u0434\u0435\u043C\u043E\u0432\u0435\u0440\u0441\u0438\u0438 \u043D\u0435\u0442 \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438 \u0432 \u0440\u0435\u0430\u043B\u044C\u043D\u044B\u0435 \u0441\u043E\u0446\u0441\u0435\u0442\u0438")),
                React.createElement("div", { className: "quiet-auth-footer" }, "OSMANX OMNICHAT \u00B7 OBSIDIAN SILENCE")));
    }
    renderSidebar() {
        const s = this.state, me = s.me;
        const compact = [['inbox', 'inbox', 'Входящие'], ['contacts', 'users', 'Клиенты'], ['deals', 'briefcase', 'Сделки'], ['integrations', 'layers', 'Интеграции'], ['settings', 'settings', 'Настройки']];
        const other = [['command', 'layout', 'Центр управления'], ['analytics', 'chart', 'Аналитика'], ['rules', 'flow', 'Автоматизация'], ['websites', 'globe', 'Чат для сайта'], ['operations', 'activity', 'Контроль доставки'], ['team', 'users', 'Команда']];
        return React.createElement("aside", { className: 'sidebar ' + (s.sidebarOpen ? 'open' : '') },
            React.createElement("div", { className: "sidebar-top" },
                React.createElement("div", { className: "brand" },
                    React.createElement("span", { className: "brand-symbol", "aria-hidden": "true" }),
                    React.createElement("div", null,
                        React.createElement("strong", null, "OSMANX"),
                        React.createElement("small", null, "OMNICHAT"))),
                React.createElement("button", { className: "icon-btn sidebar-close", "aria-label": "\u0417\u0430\u043A\u0440\u044B\u0442\u044C \u043C\u0435\u043D\u044E", onClick: () => this.setState({ sidebarOpen: false }) },
                    React.createElement(Icon, { name: "close" }))),
            React.createElement("nav", { "aria-label": "\u041E\u0441\u043D\u043E\u0432\u043D\u0430\u044F \u043D\u0430\u0432\u0438\u0433\u0430\u0446\u0438\u044F", className: "quiet-nav" }, compact.filter(([id]) => id !== 'integrations' || ['owner', 'admin', 'lead'].includes(me.role)).map(([id, ic, label]) => React.createElement("button", { key: id, className: 'nav-item ' + (s.view === id ? 'active' : ''), onClick: () => this.changeView(id) },
                React.createElement(Icon, { name: ic, size: 22 }),
                React.createElement("span", null, label)))),
            !me.organization.is_demo && ['owner', 'admin'].includes(me.role) && s.quickstart && !s.quickstart.all_done && React.createElement("button", { className: 'nav-item quickstart-nav ' + (s.view === 'start' ? 'active' : ''), onClick: () => this.changeView('start') },
                React.createElement(Icon, { name: "check", size: 19 }),
                React.createElement("span", null,
                    "\u0411\u044B\u0441\u0442\u0440\u044B\u0439 \u0441\u0442\u0430\u0440\u0442 \u00B7 ",
                    s.quickstart.completed,
                    "/",
                    s.quickstart.total)),
            React.createElement("div", { className: "sidebar-grow" }),
            React.createElement("button", { className: "nav-item quiet-more", "aria-expanded": s.moreNav, onClick: () => this.setState({ moreNav: !s.moreNav }) },
                React.createElement(Icon, { name: "menu", size: 19 }),
                React.createElement("span", null, s.moreNav ? 'Скрыть разделы' : 'Другие разделы'),
                React.createElement(Icon, { name: "chevron", size: 15 })),
            s.moreNav && React.createElement("nav", { "aria-label": "\u0414\u043E\u043F\u043E\u043B\u043D\u0438\u0442\u0435\u043B\u044C\u043D\u044B\u0435 \u0440\u0430\u0437\u0434\u0435\u043B\u044B", className: "sidebar-extra" }, other.filter(([id]) => !['operations', 'rules', 'websites'].includes(id) || ['owner', 'admin', 'lead'].includes(me.role)).map(([id, ic, label]) => React.createElement("button", { key: id, className: 'nav-item ' + (s.view === id ? 'active' : ''), onClick: () => this.changeView(id) },
                React.createElement(Icon, { name: ic, size: 17 }),
                React.createElement("span", null, label)))),
            React.createElement("div", { className: "sidebar-bottom" },
                React.createElement("div", { className: "quiet-workspace" },
                    React.createElement("span", { className: "workspace-dot" }),
                    React.createElement("div", null,
                        React.createElement("strong", null, me.organization.name),
                        React.createElement("small", null, me.organization.is_demo ? 'Демонстрация' : 'Рабочее пространство'))),
                React.createElement("div", { className: "quiet-account" },
                    React.createElement("button", { onClick: this.toggleTheme, className: "icon-btn", "aria-label": s.light ? 'Включить тёмную тему' : 'Включить светлую тему', title: "\u0421\u043C\u0435\u043D\u0438\u0442\u044C \u0442\u0435\u043C\u0443" },
                        React.createElement(Icon, { name: s.light ? 'moon' : 'sun' })),
                    React.createElement("button", { onClick: this.logout, className: "icon-btn", "aria-label": "\u0412\u044B\u0439\u0442\u0438 \u0438\u0437 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430", title: "\u0412\u044B\u0439\u0442\u0438" },
                        React.createElement(Icon, { name: "logout" })))));
    }
    renderStart() {
        const s = this.state, progress = s.quickstart;
        if (!progress)
            return React.createElement("div", { className: "page-content" },
                React.createElement("div", { className: "empty-list" }, "\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u0435\u043C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0432\u0430\u0448\u0435\u0439 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438..."));
        const tasks = progress.tasks || [];
        return React.createElement("div", { className: "page-content quickstart-page" },
            React.createElement("div", { className: "quickstart-overline" },
                React.createElement(Icon, { name: "sparkles", size: 17 }),
                " \u0411\u042B\u0421\u0422\u0420\u042B\u0419 \u0421\u0422\u0410\u0420\u0422 \u00B7 ",
                progress.is_demo ? 'ДЕМО' : 'ВАША КОМПАНИЯ'),
            React.createElement("h1", null, progress.all_done ? 'Первые шаги выполнены' : 'Настроим OSMANX за три шага'),
            React.createElement("p", { className: "quickstart-lead" }, "\u0411\u0435\u0437 \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0445 \u0442\u0435\u0440\u043C\u0438\u043D\u043E\u0432. \u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0432\u043E\u0439 \u043A\u0430\u043D\u0430\u043B \u043E\u0431\u0449\u0435\u043D\u0438\u044F, \u043F\u043E\u043B\u0443\u0447\u0438\u0442\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u0438 \u043E\u0442\u0432\u0435\u0442\u044C\u0442\u0435 \u043F\u0440\u044F\u043C\u043E \u0437\u0434\u0435\u0441\u044C."),
            progress.is_demo && React.createElement("div", { className: "quickstart-alert" },
                React.createElement(Icon, { name: "info", size: 17 }),
                " \u0412 \u0434\u0435\u043C\u043E\u0440\u0435\u0436\u0438\u043C\u0435 \u0432\u0441\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u0442\u0435\u0441\u0442\u043E\u0432\u044B\u0435. \u0414\u043B\u044F \u0440\u0430\u0431\u043E\u0442\u044B \u0441 \u043A\u043B\u0438\u0435\u043D\u0442\u0430\u043C\u0438 \u0441\u043E\u0437\u0434\u0430\u0439\u0442\u0435 \u043E\u0431\u044B\u0447\u043D\u0443\u044E \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044E."),
            React.createElement("div", { className: "quickstart-status" },
                React.createElement("strong", null,
                    progress.completed,
                    " \u0438\u0437 ",
                    progress.total,
                    " \u0448\u0430\u0433\u043E\u0432"),
                React.createElement("span", null, "\u0421\u0438\u0441\u0442\u0435\u043C\u0430 \u043E\u0442\u043C\u0435\u0447\u0430\u0435\u0442 \u0448\u0430\u0433\u0438 \u043F\u043E \u043D\u0430\u0441\u0442\u043E\u044F\u0449\u0438\u043C \u0434\u0430\u043D\u043D\u044B\u043C, \u0430 \u043D\u0435 \u043F\u043E \u043D\u0430\u0436\u0430\u0442\u0438\u044E \u043A\u043D\u043E\u043F\u043A\u0438.")),
            React.createElement("div", { className: "quickstart-track", role: "progressbar", "aria-label": "\u041F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u043A\u0430 \u0440\u0430\u0431\u043E\u0447\u0435\u0433\u043E \u043C\u0435\u0441\u0442\u0430", "aria-valuemin": 0, "aria-valuemax": progress.total, "aria-valuenow": progress.completed },
                React.createElement("div", { style: { width: (progress.completed / progress.total * 100) + '%' } })),
            React.createElement("div", { className: "quickstart-steps" }, tasks.map((task, i) => React.createElement("section", { className: 'quickstart-step ' + (task.done ? 'done' : ''), key: task.key },
                React.createElement("span", { className: "quickstart-number" }, task.done ? React.createElement(Icon, { name: "check", size: 19 }) : i + 1),
                React.createElement("div", { className: "quickstart-step-text" },
                    React.createElement("h2", null, task.title),
                    React.createElement("p", null, task.description)),
                React.createElement("button", { className: 'btn ' + (task.done ? 'secondary' : 'primary'), onClick: () => this.changeView(task.view) },
                    task.key === 'channel' ? 'Выбрать соцсеть' : task.key === 'incoming' ? 'Открыть сообщения' : 'Ответить клиенту',
                    " ",
                    React.createElement(Icon, { name: "arrow", size: 15 }))))),
            React.createElement("div", { className: "quickstart-bottom" },
                React.createElement("button", { className: "btn secondary", onClick: () => this.changeView('websites') },
                    React.createElement(Icon, { name: "globe", size: 17 }),
                    " \u0412\u043C\u0435\u0441\u0442\u043E \u0441\u043E\u0446\u0441\u0435\u0442\u0438 \u2014 \u0447\u0430\u0442 \u0434\u043B\u044F \u0441\u0430\u0439\u0442\u0430"),
                React.createElement("button", { className: "btn ghost", onClick: () => this.loadView('start') },
                    React.createElement(Icon, { name: "activity", size: 15 }),
                    " \u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u043F\u0440\u043E\u0433\u0440\u0435\u0441\u0441")),
            React.createElement("p", { className: "quickstart-disclaimer" },
                React.createElement(Icon, { name: "shield", size: 16 }),
                " ",
                progress.note));
    }
    renderCommand() {
        const s = this.state;
        const a = s.command;
        if (!a)
            return React.createElement("div", { className: "page-content" },
                React.createElement("div", { className: "empty-list" }, "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u0446\u0435\u043D\u0442\u0440\u0430 \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u044F..."));
        const queue = a.priority_queue || [];
        const maxLoad = Math.max(1, ...(a.workload || []).map((m) => m.open));
        return React.createElement("div", { className: "page-content command-page" },
            React.createElement("div", { className: "command-hero" },
                React.createElement("div", { className: "command-hero-content" },
                    React.createElement("div", { className: "eyebrow" },
                        React.createElement("span", { className: "dot green" }),
                        " \u041E\u041F\u0415\u0420\u0410\u0422\u0418\u0412\u041D\u042B\u0419 \u041E\u0411\u0417\u041E\u0420 / \u041E\u0411\u041D\u041E\u0412\u041B\u042F\u0415\u041C\u042B\u0415 \u0414\u0410\u041D\u041D\u042B\u0415"),
                    React.createElement("h1", null,
                        "\u041A\u0430\u0436\u0434\u043E\u0435 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0435",
                        React.createElement("br", null),
                        React.createElement("span", null, "\u043F\u043E\u0434 \u043A\u043E\u043D\u0442\u0440\u043E\u043B\u0435\u043C.")),
                    React.createElement("p", null, "\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442\u044B, \u0441\u0440\u043E\u043A\u0438 \u043E\u0442\u0432\u0435\u0442\u0430 \u0438 \u0440\u0430\u0431\u043E\u0442\u0430 \u043A\u043E\u043C\u0430\u043D\u0434\u044B \u2014 \u0432 \u043E\u0434\u043D\u043E\u043C \u043F\u0440\u043E\u0441\u0442\u0440\u0430\u043D\u0441\u0442\u0432\u0435. \u041E\u0447\u0435\u0440\u0435\u0434\u044C \u0440\u0430\u0441\u0441\u0447\u0438\u0442\u044B\u0432\u0430\u0435\u0442\u0441\u044F \u043F\u043E \u043F\u0440\u043E\u0437\u0440\u0430\u0447\u043D\u044B\u043C \u043F\u0440\u0430\u0432\u0438\u043B\u0430\u043C, \u0431\u0435\u0437 \u0418\u0418."),
                    React.createElement("div", { className: "command-hero-actions" },
                        React.createElement("button", { className: "btn command-primary", onClick: () => this.changeView('inbox') },
                            React.createElement(Icon, { name: "inbox", size: 17 }),
                            " \u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F ",
                            React.createElement(Icon, { name: "arrow", size: 16 })),
                        React.createElement("button", { className: "btn command-secondary", onClick: () => this.loadView('command') },
                            React.createElement(Icon, { name: "activity", size: 16 }),
                            " \u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u0434\u0430\u043D\u043D\u044B\u0435"))),
                React.createElement("div", { className: "command-hero-art", "aria-hidden": "true" },
                    React.createElement("div", { className: "orbit orbit-one" }),
                    React.createElement("div", { className: "orbit orbit-two" }),
                    React.createElement("div", { className: "orbit orbit-three" }),
                    React.createElement("div", { className: "hero-monogram" },
                        "OX",
                        React.createElement("span", null, " /")),
                    React.createElement("span", { className: "orbit-marker a" }),
                    React.createElement("span", { className: "orbit-marker b" }),
                    React.createElement("span", { className: "orbit-marker c" }))),
            React.createElement("div", { className: "command-section-title" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow small" }, "\u041E\u041F\u0415\u0420\u0410\u0426\u0418\u041E\u041D\u041D\u042B\u0415 \u041F\u041E\u041A\u0410\u0417\u0410\u0422\u0415\u041B\u0418"),
                    React.createElement("h2", null, "\u0421\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439")),
                React.createElement("div", { className: "command-updated" },
                    React.createElement("span", { className: "dot green" }),
                    " \u0414\u0430\u043D\u043D\u044B\u0435 \u043D\u0430 ",
                    fmt(a.refreshed_at),
                    " \u00B7 ",
                    a.is_demo ? 'тестовый режим' : 'рабочая область')),
            React.createElement("div", { className: "command-metrics" },
                React.createElement("div", { className: "command-metric" },
                    React.createElement("div", { className: "command-metric-top" },
                        React.createElement("span", null, "\u0410\u043A\u0442\u0438\u0432\u043D\u044B\u0435 \u0434\u0438\u0430\u043B\u043E\u0433\u0438"),
                        React.createElement(Icon, { name: "inbox", size: 19 })),
                    React.createElement("strong", null, a.total_open),
                    React.createElement("small", null, "\u0412 \u0442\u0435\u043A\u0443\u0449\u0435\u0439 \u043E\u0431\u043B\u0430\u0441\u0442\u0438 \u0432\u0438\u0434\u0438\u043C\u043E\u0441\u0442\u0438"),
                    React.createElement("div", { className: "command-metric-line" })),
                React.createElement("div", { className: "command-metric" },
                    React.createElement("div", { className: "command-metric-top" },
                        React.createElement("span", null, "\u041E\u0436\u0438\u0434\u0430\u044E\u0442 \u043E\u0442\u0432\u0435\u0442\u0430"),
                        React.createElement(Icon, { name: "clock", size: 19 })),
                    React.createElement("strong", null, a.waiting),
                    React.createElement("small", null, "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u0435\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u043E\u0442 \u043A\u043B\u0438\u0435\u043D\u0442\u0430"),
                    React.createElement("div", { className: "command-metric-line" })),
                React.createElement("div", { className: "command-metric warning" },
                    React.createElement("div", { className: "command-metric-top" },
                        React.createElement("span", null, "\u041F\u0440\u043E\u0441\u0440\u043E\u0447\u0435\u043D\u043E \u043F\u043E SLA"),
                        React.createElement(Icon, { name: "flag", size: 19 })),
                    React.createElement("strong", null, a.overdue),
                    React.createElement("small", null,
                        "\u041F\u043E\u0440\u043E\u0433 \u2014 ",
                        a.sla_minutes,
                        " \u043C\u0438\u043D."),
                    React.createElement("div", { className: "command-metric-line" })),
                React.createElement("div", { className: "command-metric" },
                    React.createElement("div", { className: "command-metric-top" },
                        React.createElement("span", null, "\u0411\u0435\u0437 \u043E\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043D\u043D\u043E\u0433\u043E"),
                        React.createElement(Icon, { name: "users", size: 19 })),
                    React.createElement("strong", null, a.unassigned),
                    React.createElement("small", null, "\u041D\u0443\u0436\u0435\u043D \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A \u0434\u043B\u044F \u043E\u0442\u0432\u0435\u0442\u0430"),
                    React.createElement("div", { className: "command-metric-line" }))),
            React.createElement("div", { className: "command-bottom-grid" },
                React.createElement("section", { className: "command-queue" },
                    React.createElement("div", { className: "command-card-head" },
                        React.createElement("div", null,
                            React.createElement("div", { className: "eyebrow small" }, "\u0423\u041C\u041D\u0410\u042F \u041E\u0427\u0415\u0420\u0415\u0414\u042C / \u0411\u0415\u0417 \u0418\u0418"),
                            React.createElement("h2", null, "\u0412 \u043F\u0435\u0440\u0432\u0443\u044E \u043E\u0447\u0435\u0440\u0435\u0434\u044C"),
                            React.createElement("p", null, "\u041F\u043E \u0441\u0440\u043E\u043A\u0443 \u043E\u0442\u0432\u0435\u0442\u0430, \u043F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442\u0443 \u0438 \u043D\u0435\u043F\u0440\u043E\u0447\u0438\u0442\u0430\u043D\u043D\u044B\u043C \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F\u043C")),
                        React.createElement("span", { className: "queue-count" },
                            queue.length,
                            " \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439")),
                    queue.length ? queue.slice(0, 7).map((c, i) => React.createElement("button", { className: "queue-item", key: c.id, onClick: () => this.openQueueConversation(c.id) },
                        React.createElement("span", { className: "queue-rank" }, String(i + 1).padStart(2, '0')),
                        React.createElement(Avatar, { name: c.contact_name, size: 40 }),
                        React.createElement("span", { className: "queue-person" },
                            React.createElement("strong", null, c.contact_name),
                            React.createElement("small", null,
                                React.createElement(Provider, { type: c.channel, small: true }),
                                " ",
                                providerName(c.channel),
                                " \u00B7 ",
                                c.reasons[0] || 'Требует внимания')),
                        React.createElement("span", { className: 'queue-priority ' + c.priority }, PRIORITIES[c.priority]),
                        React.createElement("span", { className: "queue-score" },
                            c.score,
                            React.createElement("small", null, "\u0431\u0430\u043B\u043B\u043E\u0432")),
                        React.createElement(Icon, { name: "arrow", size: 17 }))) : React.createElement("div", { className: "command-empty" },
                        React.createElement(Icon, { name: "check", size: 22 }),
                        " \u041D\u0435\u0442 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439, \u0442\u0440\u0435\u0431\u0443\u044E\u0449\u0438\u0445 \u0432\u043D\u0438\u043C\u0430\u043D\u0438\u044F"),
                    React.createElement("div", { className: "command-card-foot" },
                        React.createElement(Icon, { name: "shield", size: 14 }),
                        " \u041E\u0446\u0435\u043D\u043A\u0430 \u043E\u0441\u043D\u043E\u0432\u0430\u043D\u0430 \u043D\u0430 \u0441\u043E\u0431\u044B\u0442\u0438\u044F\u0445 \u0438 \u0440\u0435\u0433\u043B\u0430\u043C\u0435\u043D\u0442\u0435 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438, \u0430 \u043D\u0435 \u043D\u0430 \u043F\u0440\u0435\u0434\u043F\u043E\u043B\u043E\u0436\u0435\u043D\u0438\u044F\u0445.")),
                React.createElement("aside", { className: "command-side" },
                    React.createElement("div", { className: "command-side-card" },
                        React.createElement("div", { className: "eyebrow small" }, "\u041A\u041E\u041C\u0410\u041D\u0414\u0410 / \u041D\u0410\u0413\u0420\u0423\u0417\u041A\u0410"),
                        React.createElement("h3", null, "\u0420\u0430\u0441\u043F\u0440\u0435\u0434\u0435\u043B\u0435\u043D\u0438\u0435 \u0440\u0430\u0431\u043E\u0442\u044B"),
                        a.workload.length ? a.workload.map((m) => React.createElement("div", { className: "workload-row", key: m.id },
                            React.createElement("div", { className: "workload-name" },
                                React.createElement("span", { className: 'workload-dot ' + (m.active ? 'online' : '') }),
                                React.createElement("strong", null, m.name),
                                React.createElement("small", null,
                                    m.open,
                                    " \u0434\u0438\u0430\u043B.")),
                            React.createElement("div", { className: "workload-track" },
                                React.createElement("div", { style: { width: (m.open / maxLoad * 100) + '%' } })))) : React.createElement("p", { className: "no-workload" }, "\u0414\u043E\u0441\u0442\u0443\u043F\u043D\u0430 \u0442\u043E\u043B\u044C\u043A\u043E \u0432\u0430\u0448\u0430 \u043E\u0447\u0435\u0440\u0435\u0434\u044C")),
                    React.createElement("div", { className: "command-side-card command-how" },
                        React.createElement("div", { className: "eyebrow small" }, "\u041A\u0410\u041A \u0420\u0410\u0411\u041E\u0422\u0410\u0415\u0422 \u041F\u0420\u0418\u041E\u0420\u0418\u0422\u0415\u0422"),
                        React.createElement("h3", null, "\u041D\u0438\u043A\u0430\u043A\u043E\u0439 \u0447\u0451\u0440\u043D\u043E\u0439 \u043C\u0430\u0433\u0438\u0438."),
                        React.createElement("p", null, "\u0421\u0438\u0441\u0442\u0435\u043C\u0430 \u0443\u0447\u0438\u0442\u044B\u0432\u0430\u0435\u0442 \u0444\u0430\u043A\u0442\u0438\u0447\u0435\u0441\u043A\u043E\u0435 \u043E\u0436\u0438\u0434\u0430\u043D\u0438\u0435 \u043A\u043B\u0438\u0435\u043D\u0442\u0430, \u043F\u0440\u0435\u0432\u044B\u0448\u0435\u043D\u0438\u0435 SLA, \u043D\u0435\u043F\u0440\u043E\u0447\u0438\u0442\u0430\u043D\u043D\u044B\u0435 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F \u0438 \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u043D\u044B\u0439 \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u043E\u043C \u043F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442."),
                        React.createElement("button", { onClick: () => this.changeView('rules') },
                            "\u041D\u0430\u0441\u0442\u0440\u043E\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u0438\u043B\u0430 ",
                            React.createElement(Icon, { name: "arrow", size: 14 }))))),
            React.createElement("div", { className: "command-footer" },
                "OSMANX OMNICHAT ",
                React.createElement("span", null, "\u00B7"),
                " \u041A\u041E\u041C\u041C\u0423\u041D\u0418\u041A\u0410\u0426\u0418\u0418 \u041F\u041E\u0414 \u041A\u041E\u041D\u0422\u0420\u041E\u041B\u0415\u041C ",
                React.createElement("span", null, "\u00B7"),
                " \u0412\u0415\u0420\u0421\u0418\u042F 1.0"));
    }
    renderInbox() {
        const s = this.state, d = s.detail, conv = d?.conversation, demo = s.me.organization.is_demo;
        const contact = s.contactDraft || d?.contact;
        const disabledReply = !s.reply.trim() || s.loading || !!(conv?.reply_lock_owner_id && conv?.reply_lock_owner_id !== s.me.user.id) || outgoingSize(conv?.channel || 'website', s.reply) > outgoingLimit(conv?.channel || 'website') || (conv?.channel === 'whatsapp' && conv?.channel_mode === 'live' && !conv?.whatsapp_window_open);
        const messages = d?.messages || [];
        const followupDate = contact?.next_followup_at ? new Date(contact.next_followup_at * 1000 - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '';
        return React.createElement("div", { className: 'inbox-layout quiet-layout ' + (s.mobilePane === 'chat' ? 'mobile-chat ' : '') + (s.customerOpen ? 'show-customer ' : '') + (s.advancedFilters ? 'show-advanced ' : '') + (s.chatActionsOpen ? 'show-actions ' : '') },
            React.createElement("section", { className: "inbox-list", "aria-label": "\u0412\u0441\u0435 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0438" },
                React.createElement("div", { className: "inbox-list-head" },
                    React.createElement("div", { className: "heading-line" },
                        React.createElement("button", { className: "icon-btn quiet-mobile-menu", "aria-label": "\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u043C\u0435\u043D\u044E", onClick: () => this.setState({ sidebarOpen: true }) },
                            React.createElement(Icon, { name: "menu", size: 21 })),
                        React.createElement("h1", null, "\u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0435"),
                        React.createElement("button", { className: "quiet-refresh", title: "\u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u0434\u0438\u0430\u043B\u043E\u0433\u0438", "aria-label": "\u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u0434\u0438\u0430\u043B\u043E\u0433\u0438", onClick: () => this.loadConvs() },
                            React.createElement(Icon, { name: "arrow", size: 18 }))),
                    React.createElement("div", { className: "search-wrap" },
                        React.createElement(Icon, { name: "search", size: 21 }),
                        React.createElement("input", { "aria-label": "\u041F\u043E\u0438\u0441\u043A \u043F\u043E \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0430\u043C", value: s.search, onChange: (e) => this.changeSearch(e.target.value), placeholder: "\u041F\u043E\u0438\u0441\u043A \u043F\u043E \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0430\u043C..." })),
                    React.createElement("div", { className: "quiet-quick-filters", "aria-label": "\u0411\u044B\u0441\u0442\u0440\u044B\u0435 \u0444\u0438\u043B\u044C\u0442\u0440\u044B \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043E\u043A" }, [['', 'Все'], ['new', 'Новые'], ['waiting', 'Ожидают']].map(([id, label]) => React.createElement("button", { key: id, className: s.statusFilter === id ? 'active' : '', "aria-pressed": s.statusFilter === id, onClick: () => this.changeFilter('statusFilter', id) }, label))),
                    React.createElement("div", { className: "quiet-channels" },
                        React.createElement("select", { "aria-label": "\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u043A\u0430\u043D\u0430\u043B", value: s.channelFilter, onChange: (e) => this.changeFilter('channelFilter', e.target.value) },
                            React.createElement("option", { value: "" }, "\u0412\u0441\u0435 \u043A\u0430\u043D\u0430\u043B\u044B"),
                            CHANNELS.map(type => React.createElement("option", { value: type, key: type }, providerName(type)))),
                        React.createElement("button", { className: 'quiet-filter-btn ' + (s.advancedFilters ? 'active' : ''), "aria-label": s.advancedFilters ? 'Скрыть расширенные фильтры' : 'Открыть расширенные фильтры', "aria-expanded": s.advancedFilters, onClick: () => this.setState({ advancedFilters: !s.advancedFilters }) },
                            React.createElement(Icon, { name: "filter", size: 17 }))),
                    s.advancedFilters && React.createElement("div", { className: "quiet-advanced-filters" },
                        React.createElement("label", null,
                            "\u0421\u0442\u0430\u0442\u0443\u0441 ",
                            React.createElement("select", { value: s.statusFilter, "aria-label": "\u0424\u0438\u043B\u044C\u0442\u0440 \u0441\u0442\u0430\u0442\u0443\u0441\u0430", onChange: (e) => this.changeFilter('statusFilter', e.target.value) },
                                React.createElement("option", { value: "" }, "\u0412\u0441\u0435 \u0441\u0442\u0430\u0442\u0443\u0441\u044B"),
                                Object.keys(STATUS).map(k => React.createElement("option", { value: k, key: k }, STATUS[k])))),
                        React.createElement("label", null,
                            "\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442",
                            React.createElement("select", { value: s.priorityFilter, "aria-label": "\u0424\u0438\u043B\u044C\u0442\u0440 \u043F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442\u0430", onChange: (e) => this.changeFilter('priorityFilter', e.target.value) },
                                React.createElement("option", { value: "" }, "\u0412\u0441\u0435 \u043F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442\u044B"),
                                Object.keys(PRIORITIES).map(k => React.createElement("option", { value: k, key: k }, PRIORITIES[k])))),
                        React.createElement("label", null,
                            "\u0421\u043E\u0440\u0442\u0438\u0440\u043E\u0432\u043A\u0430",
                            React.createElement("select", { value: s.sortFilter, "aria-label": "\u0421\u043E\u0440\u0442\u0438\u0440\u043E\u0432\u043A\u0430 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043E\u043A", onChange: (e) => this.changeFilter('sortFilter', e.target.value) },
                                React.createElement("option", { value: "recent" }, "\u0421\u043D\u0430\u0447\u0430\u043B\u0430 \u043D\u043E\u0432\u044B\u0435"),
                                React.createElement("option", { value: "priority" }, "\u041F\u043E \u0432\u0430\u0436\u043D\u043E\u0441\u0442\u0438"),
                                React.createElement("option", { value: "oldest" }, "\u0421\u043D\u0430\u0447\u0430\u043B\u0430 \u0441\u0442\u0430\u0440\u044B\u0435"))),
                        React.createElement("button", { className: "quiet-filter-action", onClick: () => this.changeFilter('archivedFilter', !s.archivedFilter) }, s.archivedFilter ? 'Показать активные' : 'Показать архив'),
                        React.createElement("button", { className: "quiet-filter-action", onClick: () => this.setState({ modal: 'view', viewName: '', viewShared: false }) }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0444\u0438\u043B\u044C\u0442\u0440\u044B"),
                        s.views.length > 0 && React.createElement("div", { className: "quiet-saved-views" }, s.views.map((v) => React.createElement("button", { key: v.id, onClick: () => this.applySavedView(v) }, v.name))))),
                React.createElement("div", { className: "conversation-scroll" }, s.convs.length === 0 ? React.createElement("div", { className: "empty-list" },
                    React.createElement(Icon, { name: "inbox", size: 30 }),
                    React.createElement("h3", null, s.me.organization.is_demo ? 'Нет диалогов по фильтру' : 'Здесь появятся сообщения'),
                    React.createElement("p", null, s.me.organization.is_demo ? 'Очистите фильтр, чтобы увидеть тестовые обращения.' : 'Когда клиент напишет в подключённый канал, обращение сразу появится здесь.'),
                    !s.me.organization.is_demo && ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn primary", onClick: () => this.changeView('start') },
                        "\u041D\u0430\u0441\u0442\u0440\u043E\u0438\u0442\u044C \u043F\u0435\u0440\u0432\u044B\u0439 \u043A\u0430\u043D\u0430\u043B ",
                        React.createElement(Icon, { name: "arrow", size: 15 })),
                    (s.channelFilter || s.statusFilter || s.search || s.priorityFilter) && React.createElement("button", { className: "btn ghost", onClick: () => this.setState({ search: '', channelFilter: '', statusFilter: '', priorityFilter: '' }, () => this.loadConvs()) }, "\u0421\u0431\u0440\u043E\u0441\u0438\u0442\u044C \u043F\u043E\u0438\u0441\u043A \u0438 \u0444\u0438\u043B\u044C\u0442\u0440\u044B")) : s.convs.map((item) => React.createElement("button", { key: item.id, className: 'conversation-card ' + (s.selected === item.id ? 'selected' : ''), onClick: () => this.select(item.id) },
                    React.createElement("div", { className: "conv-avatar" },
                        React.createElement(Provider, { type: item.channel })),
                    React.createElement("div", { className: "conv-body" },
                        React.createElement("div", { className: "conv-top" },
                            React.createElement("strong", null, item.contact_name),
                            React.createElement("time", null, fmt(item.last_message_at))),
                        React.createElement("div", { className: "conv-bottom" },
                            React.createElement("p", null, this.drafts[item.id] ? 'Черновик: ' + this.drafts[item.id] : item.last_message || 'Вложение'),
                            item.unread_count > 0 && React.createElement("span", { className: "unread-badge" }, item.unread_count)))))),
                demo && React.createElement("div", { className: "list-foot" },
                    React.createElement("span", { className: "online-dot" }),
                    "\u0414\u0435\u043C\u043E\u043D\u0441\u0442\u0440\u0430\u0446\u0438\u043E\u043D\u043D\u044B\u0435 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0438")),
            React.createElement("section", { className: "chat-pane", "aria-label": "\u0410\u043A\u0442\u0438\u0432\u043D\u0430\u044F \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0430" }, !conv ? React.createElement("div", { className: "chat-empty" },
                React.createElement("div", { className: "chat-empty-icon" },
                    React.createElement(Icon, { name: "inbox", size: 28 })),
                React.createElement("h2", null, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0438\u0430\u043B\u043E\u0433"),
                React.createElement("p", null, "\u0412\u0441\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u0432\u0430\u0448\u0438\u0445 \u043A\u0430\u043D\u0430\u043B\u043E\u0432 \u0441\u043E\u0431\u0440\u0430\u043D\u044B \u0432 \u043E\u0434\u043D\u043E\u043C \u043E\u043A\u043D\u0435.")) : React.createElement(React.Fragment, null,
                React.createElement("div", { className: "chat-topbar" },
                    React.createElement("button", { className: "icon-btn mobile-back", "aria-label": "\u041A \u0441\u043F\u0438\u0441\u043A\u0443 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043E\u043A", onClick: () => this.setState({ mobilePane: 'list', customerOpen: false }) },
                        React.createElement(Icon, { name: "back", size: 20 })),
                    React.createElement(Avatar, { name: conv.contact_name, size: 49 }),
                    React.createElement("div", { className: "chat-title" },
                        React.createElement("strong", null, conv.contact_name),
                        React.createElement("small", null,
                            React.createElement(Provider, { type: conv.channel, small: true }),
                            " ",
                            providerName(conv.channel),
                            demo && React.createElement("span", { className: "quiet-demo-inline" }, " \u00B7 \u0434\u0435\u043C\u043E"))),
                    React.createElement("button", { className: "customer-toggle", "aria-label": s.customerOpen ? 'Скрыть карточку клиента' : 'Показать карточку клиента', "aria-expanded": s.customerOpen, title: "\u041A\u0430\u0440\u0442\u043E\u0447\u043A\u0430 \u043A\u043B\u0438\u0435\u043D\u0442\u0430", onClick: () => this.setState({ customerOpen: !s.customerOpen }) },
                        React.createElement(Icon, { name: "users", size: 20 })),
                    React.createElement("button", { className: "chat-actions-toggle", "aria-label": "\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u044F \u0441 \u0434\u0438\u0430\u043B\u043E\u0433\u043E\u043C", "aria-expanded": s.chatActionsOpen, onClick: () => this.setState({ chatActionsOpen: !s.chatActionsOpen }) }, "\u2022\u2022\u2022"),
                    s.chatActionsOpen && React.createElement("div", { className: "quiet-actions-menu" },
                        React.createElement("strong", null, "\u0423\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u0434\u0438\u0430\u043B\u043E\u0433\u043E\u043C"),
                        React.createElement("label", null,
                            "\u0421\u0442\u0430\u0442\u0443\u0441",
                            React.createElement("select", { "aria-label": "\u0421\u0442\u0430\u0442\u0443\u0441 \u0434\u0438\u0430\u043B\u043E\u0433\u0430", value: conv.status, onChange: (e) => this.updateConv('status', e.target.value) }, Object.keys(STATUS).map(k => React.createElement("option", { value: k, key: k }, STATUS[k])))),
                        React.createElement("label", null,
                            "\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442",
                            React.createElement("select", { "aria-label": "\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442 \u0434\u0438\u0430\u043B\u043E\u0433\u0430", value: conv.priority || 'normal', onChange: (e) => this.setPriority(e.target.value) }, Object.keys(PRIORITIES).map(k => React.createElement("option", { value: k, key: k }, PRIORITIES[k])))),
                        React.createElement("button", { onClick: () => this.claimReply(conv.reply_lock_owner_id === s.me.user.id), disabled: s.loading || !!(conv.reply_lock_owner_id && conv.reply_lock_owner_id !== s.me.user.id) }, conv.reply_lock_owner_id === s.me.user.id ? 'Освободить диалог' : conv.reply_lock_owner_id ? 'Диалог занят коллегой' : 'Занять диалог на 2 минуты'),
                        React.createElement("button", { onClick: () => this.updateConv('pin', true) }, conv.pinned ? 'Открепить' : 'Закрепить диалог'),
                        React.createElement("button", { onClick: () => this.setState({ showQuickReplies: true, chatActionsOpen: false }) }, "\u0428\u0430\u0431\u043B\u043E\u043D\u044B \u043E\u0442\u0432\u0435\u0442\u043E\u0432"),
                        React.createElement("button", { onClick: () => this.setState({ customerOpen: true, tab: 'notes', chatActionsOpen: false }) }, "\u0412\u043D\u0443\u0442\u0440\u0435\u043D\u043D\u0438\u0435 \u0437\u0430\u043C\u0435\u0442\u043A\u0438"),
                        React.createElement("button", { onClick: () => { this.setState({ customerOpen: true, tab: 'activity', chatActionsOpen: false }); this.loadActivity(conv.id); } }, "\u0418\u0441\u0442\u043E\u0440\u0438\u044F \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439"))),
                React.createElement("div", { className: "chat-content" },
                    conv.reply_lock_owner_id && React.createElement("div", { className: "lease-hint" },
                        React.createElement(Icon, { name: "shield", size: 15 }),
                        conv.reply_lock_owner_id === s.me.user.id ? 'Вы отвечаете в этом диалоге' : 'Диалог занят другим сотрудником'),
                    React.createElement("div", { className: "chat-messages", ref: (el) => { this.chatScroll = el; } },
                        s.detail?.message_paging?.has_older && React.createElement("div", { className: "history-older-control" },
                            React.createElement("button", { type: "button", onClick: this.loadOlderMessages, disabled: s.olderLoading }, s.olderLoading ? 'Загружаем историю…' : 'Показать более ранние сообщения')),
                        messages.length > 0 && React.createElement("div", { className: "chat-date-divider" },
                            React.createElement("span", null, "\u041F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0430")),
                        messages.map((m) => React.createElement("div", { key: m.id, className: 'message-line ' + (m.direction === 'out' ? 'outbound' : 'inbound') },
                            m.direction !== 'out' && React.createElement(Avatar, { name: conv.contact_name, size: 34 }),
                            React.createElement("div", { className: "message-stack" },
                                React.createElement("div", { className: "message-bubble" },
                                    m.is_demo && React.createElement("span", { className: "message-demo-label" }, "\u0414\u0415\u041C\u041E"),
                                    React.createElement("div", { className: "message-text" }, m.body),
                                    m.kind === 'whatsapp_template' && React.createElement("div", { className: "wa-template-badge" }, "\u0428\u0430\u0431\u043B\u043E\u043D WhatsApp \u00B7 Meta API"),
                                    m.attachment && m.kind !== 'whatsapp_template' && React.createElement("div", { className: "message-attachment" }, (m.attachment.type === 'image' || m.attachment.type === 'sticker') ? React.createElement("img", { loading: "lazy", alt: "\u0412\u043B\u043E\u0436\u0435\u043D\u0438\u0435 \u0432 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0435", src: m.attachment.provider === 'whatsapp' ? '/api/media/' + m.id : m.attachment.url || '' }) : React.createElement("a", { href: m.attachment.provider === 'whatsapp' ? '/api/media/' + m.id : m.attachment.url || '#', target: "_blank", rel: "noreferrer noopener" },
                                        React.createElement(Icon, { name: "note", size: 14 }),
                                        " \u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0432\u043B\u043E\u0436\u0435\u043D\u0438\u0435"))),
                                React.createElement("div", { className: "message-meta" },
                                    fmt(m.created_at),
                                    " ",
                                    m.direction === 'out' && React.createElement("span", { className: 'delivery-indicator delivery-' + (m.delivery_status || 'unconfirmed'), title: deliveryLabel(m.delivery_status, conv.channel) }, deliveryLabel(m.delivery_status, conv.channel))))))),
                    React.createElement("div", { className: "composer" },
                        conv.outbound_paused && React.createElement("div", { className: "outbound-stop-note", role: "status" },
                            React.createElement(Icon, { name: "shield", size: 16 }),
                            React.createElement("span", null,
                                React.createElement("strong", null, conv.organization_outbound_paused ? 'Компания приостановила все новые исходящие.' : 'Отправка через этот аккаунт приостановлена.'),
                                " \u041E\u0442\u0432\u0435\u0442 \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u0441\u044F \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u0438, \u043D\u043E \u043D\u0435 \u0443\u0439\u0434\u0451\u0442 \u043A\u043B\u0438\u0435\u043D\u0442\u0443 \u0434\u043E \u0440\u0435\u0448\u0435\u043D\u0438\u044F \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440\u0430.")),
                        s.showQuickReplies && React.createElement("div", { className: "composer-quick" },
                            React.createElement("button", { className: "quick-close", "aria-label": "\u0421\u043A\u0440\u044B\u0442\u044C \u0448\u0430\u0431\u043B\u043E\u043D\u044B", onClick: () => this.setState({ showQuickReplies: false }) },
                                React.createElement(Icon, { name: "close", size: 14 })),
                            s.templates.length ? s.templates.map((t) => React.createElement("button", { key: t.id, onClick: () => { this.changeReply(t.body); this.setState({ showQuickReplies: false }); } }, t.title)) : React.createElement("button", { onClick: () => { this.changeReply('Здравствуйте! Чем можем вам помочь?'); this.setState({ showQuickReplies: false }); } }, "\u041F\u0440\u0438\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0435")),
                        React.createElement("div", { className: "composer-entry" },
                            React.createElement("button", { className: "quiet-attach", "aria-label": "\u041F\u0440\u0438\u043A\u0440\u0435\u043F\u0438\u0442\u044C \u0444\u0430\u0439\u043B", title: "\u041E\u0442\u043F\u0440\u0430\u0432\u043A\u0430 \u0432\u043B\u043E\u0436\u0435\u043D\u0438\u0439 \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u043F\u043E\u0441\u043B\u0435 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 API \u043A\u0430\u0436\u0434\u043E\u0433\u043E \u043A\u0430\u043D\u0430\u043B\u0430", onClick: () => this.notify('Исходящие вложения ещё не поддерживаются для всех каналов. Пока доступен текстовый ответ.') },
                                React.createElement("svg", { width: "23", height: "23", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.8", strokeLinecap: "round", strokeLinejoin: "round" },
                                    React.createElement("path", { d: "M20 12.5 11.5 21a6 6 0 0 1-8.5-8.5L13 2.5a4 4 0 0 1 5.7 5.7L8.2 18.7a2 2 0 0 1-2.8-2.8l9.2-9.2" }))),
                            React.createElement("textarea", { "aria-label": "\u0422\u0435\u043A\u0441\u0442 \u043E\u0442\u0432\u0435\u0442\u0430", rows: 1, placeholder: "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435...", value: s.reply, onChange: (e) => this.changeReply(e.target.value), onKeyDown: (e) => { if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    this.send();
                                } } }),
                            React.createElement("button", { className: "quiet-emoji", "aria-label": "\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u044C \u044D\u043C\u043E\u0434\u0437\u0438", "aria-expanded": s.showEmoji, onClick: () => this.setState({ showEmoji: !s.showEmoji }) }, "\u263A"),
                            s.showEmoji && React.createElement("div", { className: "quiet-emoji-menu" }, ['🙂', '😊', '👍', '❤️', '🙏', '👋'].map((emoji) => React.createElement("button", { key: emoji, onClick: () => this.appendEmoji(emoji) }, emoji))),
                            React.createElement("button", { className: "send-btn", "aria-label": "\u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043E\u0442\u0432\u0435\u0442", title: "\u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043E\u0442\u0432\u0435\u0442", disabled: disabledReply, onClick: this.send },
                                React.createElement(Icon, { name: "send", size: 23 }))),
                        conv.channel === 'whatsapp' && conv.channel_mode === 'live' && React.createElement("div", { className: "wa-composer-actions" },
                            conv.whatsapp_window_open === false && React.createElement("span", null, "\u041E\u043A\u043D\u043E \u043E\u0431\u044B\u0447\u043D\u044B\u0445 \u043E\u0442\u0432\u0435\u0442\u043E\u0432 \u0437\u0430\u043A\u0440\u044B\u0442\u043E. \u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043C\u043E\u0436\u043D\u043E \u0442\u043E\u043B\u044C\u043A\u043E \u043E\u0434\u043E\u0431\u0440\u0435\u043D\u043D\u044B\u0439 \u0448\u0430\u0431\u043B\u043E\u043D."),
                            React.createElement("button", { className: "btn secondary", onClick: this.openWaTemplates, disabled: s.loading },
                                React.createElement(Icon, { name: "note", size: 16 }),
                                " \u041E\u0434\u043E\u0431\u0440\u0435\u043D\u043D\u044B\u0439 \u0448\u0430\u0431\u043B\u043E\u043D WhatsApp")),
                        outgoingSize(conv.channel, s.reply) > outgoingLimit(conv.channel) && React.createElement("div", { className: "quiet-length-alert" },
                            "\u041F\u0440\u0435\u0432\u044B\u0448\u0435\u043D \u043B\u0438\u043C\u0438\u0442 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u0434\u043B\u044F ",
                            providerName(conv.channel)))),
                s.customerOpen && React.createElement("aside", { className: "details-pane", "aria-label": "\u041A\u0430\u0440\u0442\u043E\u0447\u043A\u0430 \u043A\u043B\u0438\u0435\u043D\u0442\u0430" },
                    React.createElement("div", { className: "quiet-detail-head" },
                        React.createElement("div", null,
                            React.createElement("h2", null, d.contact.name),
                            React.createElement("div", { className: "quiet-detail-channel" },
                                React.createElement(Provider, { type: conv.channel, small: true }),
                                providerName(conv.channel))),
                        React.createElement("button", { className: "quiet-detail-close", title: "\u0421\u0432\u0435\u0440\u043D\u0443\u0442\u044C \u043A\u0430\u0440\u0442\u043E\u0447\u043A\u0443 \u043A\u043B\u0438\u0435\u043D\u0442\u0430", "aria-label": "\u0421\u0432\u0435\u0440\u043D\u0443\u0442\u044C \u043A\u0430\u0440\u0442\u043E\u0447\u043A\u0443 \u043A\u043B\u0438\u0435\u043D\u0442\u0430", onClick: () => this.setState({ customerOpen: false }) },
                            React.createElement(Icon, { name: "chevron", size: 19 }))),
                    s.tab === 'info' ? React.createElement("div", { className: "details-scroll" },
                        React.createElement("div", { className: "detail-section quiet-tags" },
                            React.createElement("h3", null, "\u0422\u0435\u0433\u0438"),
                            React.createElement("div", { className: "quiet-tag-list" }, (contact?.tags || []).map((tag) => React.createElement("span", { className: "quiet-tag", key: tag },
                                tag,
                                React.createElement("button", { "aria-label": 'Удалить тег ' + tag, onClick: () => this.removeCustomerTag(tag) }, "\u00D7")))),
                            s.tagEditing ? React.createElement("div", { className: "quiet-tag-edit" },
                                React.createElement("input", { autoFocus: true, value: s.tagInput, "aria-label": "\u041D\u043E\u0432\u044B\u0439 \u0442\u0435\u0433", placeholder: "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0442\u0435\u0433\u0430", onChange: (e) => this.setState({ tagInput: e.target.value }), onKeyDown: (e) => { if (e.key === 'Enter')
                                        this.addCustomerTag(); if (e.key === 'Escape')
                                        this.setState({ tagEditing: false, tagInput: '' }); } }),
                                React.createElement("button", { onClick: this.addCustomerTag, disabled: !s.tagInput.trim() }, "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C")) : React.createElement("button", { className: "quiet-add-tag", onClick: () => this.setState({ tagEditing: true }) },
                                React.createElement(Icon, { name: "plus", size: 16 }),
                                " \u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0442\u0435\u0433")),
                        React.createElement("div", { className: "detail-section" },
                            React.createElement("h3", null, "\u0421\u0442\u0430\u0434\u0438\u044F \u0441\u0434\u0435\u043B\u043A\u0438"),
                            React.createElement("select", { "aria-label": "\u042D\u0442\u0430\u043F \u0441\u0434\u0435\u043B\u043A\u0438", value: contact?.stage || d.contact.stage, onChange: (e) => { const next = { ...contact, stage: e.target.value }; this.setState({ contactDraft: next }); this.saveContact(next); } }, Object.keys(STAGES).map(k => React.createElement("option", { value: k, key: k }, STAGES[k])))),
                        React.createElement("div", { className: "detail-section" },
                            React.createElement("h3", null, "\u041E\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043D\u043D\u044B\u0439"),
                            React.createElement("select", { "aria-label": "\u041E\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043D\u043D\u044B\u0439", value: conv.assigned_user_id || '', onChange: (e) => this.updateConv('assign', e.target.value || null), disabled: !['owner', 'admin', 'lead'].includes(s.me.role) },
                                React.createElement("option", { value: "" }, "\u041D\u0435 \u043D\u0430\u0437\u043D\u0430\u0447\u0435\u043D"),
                                s.team.map((m) => React.createElement("option", { value: m.id, key: m.id }, m.name)))),
                        React.createElement("div", { className: "detail-section" },
                            React.createElement("h3", null, "\u0421\u043B\u0435\u0434\u0443\u044E\u0449\u0438\u0439 \u043A\u043E\u043D\u0442\u0430\u043A\u0442"),
                            (s.followupEditing || followupDate) ? React.createElement("input", { className: "quiet-followup", type: "datetime-local", "aria-label": "\u0414\u0430\u0442\u0430 \u0441\u043B\u0435\u0434\u0443\u044E\u0449\u0435\u0433\u043E \u043A\u043E\u043D\u0442\u0430\u043A\u0442\u0430", value: followupDate, onChange: (e) => this.setState({ contactDraft: { ...contact, next_followup_at: e.target.value ? Date.parse(e.target.value) / 1000 : null } }), onBlur: () => { if (contact && contact.next_followup_at !== d.contact.next_followup_at)
                                    this.saveContact(contact); this.setState({ followupEditing: false }); } }) : React.createElement("button", { className: "quiet-followup-prompt", onClick: () => this.setState({ followupEditing: true }) },
                                React.createElement(Icon, { name: "clock", size: 18 }),
                                " \u0412\u044B\u0431\u0440\u0430\u0442\u044C \u0434\u0430\u0442\u0443 \u0438 \u0432\u0440\u0435\u043C\u044F")),
                        React.createElement("button", { className: "quiet-details-more", onClick: () => this.setState({ customerExtras: !s.customerExtras }), "aria-expanded": s.customerExtras },
                            s.customerExtras ? 'Скрыть дополнительные поля' : 'Дополнительные данные',
                            React.createElement(Icon, { name: "chevron", size: 15 })),
                        s.customerExtras && React.createElement("div", { className: "quiet-extra-fields" },
                            React.createElement("label", null,
                                "\u0421\u0443\u043C\u043C\u0430 \u0441\u0434\u0435\u043B\u043A\u0438",
                                React.createElement("input", { type: "number", min: "0", "aria-label": "\u0421\u0443\u043C\u043C\u0430 \u0441\u0434\u0435\u043B\u043A\u0438", value: contact?.deal_amount ?? '', placeholder: "\u041D\u0435 \u0443\u043A\u0430\u0437\u0430\u043D\u0430", onChange: (e) => this.setState({ contactDraft: { ...contact, deal_amount: e.target.value ? Number(e.target.value) : null } }) })),
                            React.createElement("label", { className: "tiny-check" },
                                React.createElement("input", { type: "checkbox", checked: !!contact?.deal_confirmed, onChange: (e) => this.setState({ contactDraft: { ...contact, deal_confirmed: e.target.checked } }) }),
                                " \u0421\u0434\u0435\u043B\u043A\u0430 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0430"),
                            React.createElement("label", null,
                                "\u0422\u0435\u043B\u0435\u0444\u043E\u043D",
                                React.createElement("input", { "aria-label": "\u0422\u0435\u043B\u0435\u0444\u043E\u043D", value: contact?.phone || '', placeholder: "\u041D\u0435 \u0443\u043A\u0430\u0437\u0430\u043D", onChange: (e) => this.setState({ contactDraft: { ...contact, phone: e.target.value } }) })),
                            React.createElement("button", { className: "btn secondary wide", onClick: () => this.saveContact(contact) },
                                React.createElement(Icon, { name: "check", size: 15 }),
                                " \u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F")),
                        s.customerExtras && demo && React.createElement("div", { className: "quiet-demo-incoming" },
                            React.createElement("h3", null, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0435"),
                            React.createElement("textarea", { rows: 2, "aria-label": "\u0422\u0435\u0441\u0442\u043E\u0432\u043E\u0435 \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0435", placeholder: "\u041D\u0430\u043F\u0438\u0448\u0438\u0442\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u043E\u0442 \u043A\u043B\u0438\u0435\u043D\u0442\u0430...", value: s.demoInbound, onChange: (e) => this.setState({ demoInbound: e.target.value }) }),
                            React.createElement("button", { className: "btn secondary wide", onClick: this.demoIncoming, disabled: !s.demoInbound.trim() }, "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0442\u0435\u0441\u0442\u043E\u0432\u043E\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435"))) : s.tab === 'notes' ? React.createElement("div", { className: "note-pane" },
                        React.createElement("button", { className: "quiet-back-detail", onClick: () => this.setState({ tab: 'info' }) },
                            React.createElement(Icon, { name: "back", size: 15 }),
                            " \u041A \u043A\u043B\u0438\u0435\u043D\u0442\u0443"),
                        React.createElement("h3", null, "\u0412\u043D\u0443\u0442\u0440\u0435\u043D\u043D\u0438\u0435 \u0437\u0430\u043C\u0435\u0442\u043A\u0438"),
                        React.createElement("p", { className: "note-caption" }, "\u0417\u0430\u043C\u0435\u0442\u043A\u0438 \u0432\u0438\u0434\u044F\u0442 \u0442\u043E\u043B\u044C\u043A\u043E \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u0438."),
                        React.createElement("div", { className: "notes-list" }, d.notes.length ? d.notes.map((n) => React.createElement("div", { key: n.id, className: "note-card" },
                            React.createElement("p", null, n.body),
                            React.createElement("small", null,
                                n.author,
                                " \u00B7 ",
                                dateFmt(n.created_at)))) : React.createElement("p", { className: "empty-note" }, "\u0417\u0430\u043C\u0435\u0442\u043E\u043A \u043F\u043E\u043A\u0430 \u043D\u0435\u0442")),
                        React.createElement("textarea", { rows: 4, "aria-label": "\u041D\u043E\u0432\u0430\u044F \u0437\u0430\u043C\u0435\u0442\u043A\u0430", placeholder: "\u041D\u0430\u043F\u0438\u0448\u0438\u0442\u0435 \u0437\u0430\u043C\u0435\u0442\u043A\u0443...", value: s.note, onChange: (e) => this.setState({ note: e.target.value }) }),
                        React.createElement("button", { className: "btn secondary wide", disabled: !s.note.trim(), onClick: this.addNote }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0437\u0430\u043C\u0435\u0442\u043A\u0443")) : React.createElement("div", { className: "activity-pane" },
                        React.createElement("button", { className: "quiet-back-detail", onClick: () => this.setState({ tab: 'info' }) },
                            React.createElement(Icon, { name: "back", size: 15 }),
                            " \u041A \u043A\u043B\u0438\u0435\u043D\u0442\u0443"),
                        React.createElement("h3", null, "\u0418\u0441\u0442\u043E\u0440\u0438\u044F \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439"),
                        s.activity.length ? s.activity.map((a) => React.createElement("div", { className: "activity-row", key: a.id },
                            React.createElement("div", null,
                                React.createElement("strong", null, a.title),
                                React.createElement("small", null,
                                    a.actor,
                                    " \u00B7 ",
                                    dateFmt(a.created_at),
                                    " \u00B7 ",
                                    fmt(a.created_at))))) : React.createElement("p", { className: "empty-note" }, "\u0417\u0430\u043F\u0438\u0441\u0435\u0439 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442"))))));
    }
    renderDeals() { const s = this.state; const stages = ['new', 'interested', 'negotiation', 'payment', 'success', 'lost']; return React.createElement("div", { className: "page-content quiet-deals" },
        React.createElement("div", { className: "section-head" },
            React.createElement("div", null,
                React.createElement("div", { className: "eyebrow" }, "CRM / \u0412\u041E\u0420\u041E\u041D\u041A\u0410"),
                React.createElement("h1", null, "\u0421\u0434\u0435\u043B\u043A\u0438"),
                React.createElement("p", null, "\u042D\u0442\u0430\u043F\u044B \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044E\u0442\u0441\u044F \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u0430\u043C\u0438, \u0441\u0438\u0441\u0442\u0435\u043C\u0430 \u043D\u0435 \u043F\u0440\u0438\u0434\u0443\u043C\u044B\u0432\u0430\u0435\u0442 \u043F\u0440\u043E\u0434\u0430\u0436\u0438.")),
            React.createElement("button", { className: "btn secondary", onClick: () => this.loadView('deals') },
                React.createElement(Icon, { name: "arrow", size: 16 }),
                " \u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C")),
        React.createElement("div", { className: "deals-board" }, stages.map((stage) => React.createElement("section", { className: "deals-stage", key: stage },
            React.createElement("h3", null,
                STAGES[stage],
                " ",
                React.createElement("span", null, s.contacts.filter((c) => c.stage === stage).length)),
            s.contacts.filter((c) => c.stage === stage).map((c) => React.createElement("div", { className: "deal-card", key: c.id },
                React.createElement("div", { className: "deal-person" },
                    React.createElement(Avatar, { name: c.name, size: 33 }),
                    React.createElement("strong", null, c.name)),
                React.createElement("small", null, c.deal_amount != null ? formatMoney(c.deal_amount, s.me.organization.currency) : 'Сумма не указана'),
                React.createElement("select", { "aria-label": 'Этап сделки ' + c.name, value: c.stage, onChange: (e) => this.saveContact({ ...c, stage: e.target.value, deal_confirmed: c.deal_confirmed && e.target.value === 'success' }) }, stages.map((k) => React.createElement("option", { value: k, key: k }, STAGES[k]))))),
            !s.contacts.some((c) => c.stage === stage) && React.createElement("p", { className: "deals-empty" }, "\u041F\u043E\u043A\u0430 \u043D\u0435\u0442 \u0441\u0434\u0435\u043B\u043E\u043A"))))); }
    renderContacts() { const s = this.state; return React.createElement("div", { className: "page-content" },
        React.createElement("div", { className: "section-head" },
            React.createElement("div", null,
                React.createElement("div", { className: "eyebrow" }, "\u041A\u041B\u0418\u0415\u041D\u0422\u042B / \u0412\u0417\u0410\u0418\u041C\u041E\u041E\u0422\u041D\u041E\u0428\u0415\u041D\u0418\u042F"),
                React.createElement("h1", null, "\u041A\u043B\u0438\u0435\u043D\u0442\u044B"),
                React.createElement("p", null, "\u041A\u043E\u043D\u0442\u0430\u043A\u0442\u044B, \u044D\u0442\u0430\u043F\u044B \u0441\u0434\u0435\u043B\u043E\u043A \u0438 \u0438\u0441\u0442\u043E\u0440\u0438\u044F \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439 \u0432 \u043E\u0434\u043D\u043E\u0439 \u0441\u0438\u0441\u0442\u0435\u043C\u0435.")),
            React.createElement("span", { className: "heading-count" },
                s.contacts.length,
                " \u043A\u043E\u043D\u0442\u0430\u043A\u0442\u043E\u0432")),
        React.createElement("div", { className: "table-card" },
            React.createElement("div", { className: "table-heading" },
                React.createElement("h3", null, "\u041A\u0430\u0440\u0442\u043E\u0447\u043A\u0438 \u043A\u043B\u0438\u0435\u043D\u0442\u043E\u0432"),
                React.createElement("span", null, "\u0412\u044B\u0440\u0443\u0447\u043A\u0430 \u0443\u0447\u0438\u0442\u044B\u0432\u0430\u0435\u0442\u0441\u044F \u0442\u043E\u043B\u044C\u043A\u043E \u043F\u043E\u0441\u043B\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F")),
            React.createElement("div", { className: "table-scroll" },
                React.createElement("table", null,
                    React.createElement("thead", null,
                        React.createElement("tr", null,
                            React.createElement("th", null, "\u041A\u041B\u0418\u0415\u041D\u0422"),
                            React.createElement("th", null, "\u042D\u0422\u0410\u041F"),
                            React.createElement("th", null, "\u0422\u0415\u0413\u0418"),
                            React.createElement("th", null, "\u0421\u0423\u041C\u041C\u0410"),
                            React.createElement("th", null, "\u0420\u0415\u0417\u0423\u041B\u042C\u0422\u0410\u0422"))),
                    React.createElement("tbody", null, s.contacts.map((c) => React.createElement("tr", { key: c.id },
                        React.createElement("td", null,
                            React.createElement("div", { className: "table-name" },
                                React.createElement(Avatar, { name: c.name, size: 33 }),
                                React.createElement("div", null,
                                    React.createElement("b", null, c.name),
                                    React.createElement("small", null, c.phone || 'Контакт не указан')))),
                        React.createElement("td", null,
                            React.createElement("select", { value: c.stage, onChange: (e) => this.saveContact({ ...c, stage: e.target.value, deal_confirmed: false }) }, Object.keys(STAGES).map(k => React.createElement("option", { key: k, value: k }, STAGES[k])))),
                        React.createElement("td", null,
                            c.tags?.map((tag) => React.createElement("span", { className: "tag", key: tag }, tag)),
                            !c.tags?.length && React.createElement("span", { className: "muted" }, "\u2014")),
                        React.createElement("td", { className: "number" }, c.deal_amount != null ? formatMoney(c.deal_amount, s.me.organization.currency) : '—'),
                        React.createElement("td", null, c.deal_confirmed ? React.createElement("span", { className: "pill green" },
                            React.createElement(Icon, { name: "check", size: 13 }),
                            " \u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u043E") : React.createElement("span", { className: "pill neutral" }, "\u041D\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u043E"))))))))); }
    renderAnalytics() {
        const a = this.state.analytics;
        const demo = this.state.me.organization.is_demo;
        if (!a)
            return React.createElement("div", { className: "page-content" },
                React.createElement("div", { className: "empty-list" }, "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043C \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443..."));
        const max = Math.max(1, ...a.days.map((x) => x.count));
        return React.createElement("div", { className: "page-content" },
            React.createElement("div", { className: "section-head" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow" }, "\u041C\u0415\u0422\u0420\u0418\u041A\u0418 / \u042D\u0424\u0424\u0415\u041A\u0422\u0418\u0412\u041D\u041E\u0421\u0422\u042C"),
                    React.createElement("h1", null, "\u0410\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430 \u043A\u043E\u043C\u043C\u0443\u043D\u0438\u043A\u0430\u0446\u0438\u0439"),
                    React.createElement("p", null, "\u0420\u0435\u0430\u043B\u044C\u043D\u044B\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u044F, \u0434\u043B\u0438\u0442\u0435\u043B\u044C\u043D\u043E\u0441\u0442\u044C \u043E\u0442\u0432\u0435\u0442\u0430 \u0438 \u043D\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u043D\u0430 \u043A\u0430\u043D\u0430\u043B\u044B \u2014 \u0431\u0435\u0437 \u0432\u044B\u0434\u0443\u043C\u0430\u043D\u043D\u044B\u0445 \u043F\u0440\u043E\u0434\u0430\u0436.")),
                React.createElement("span", { className: "pill neutral" },
                    React.createElement("span", { className: "dot green" }),
                    demo ? 'Демоданные' : 'Данные системы')),
            React.createElement("div", { className: "metric-grid" },
                React.createElement("div", { className: "metric-card" },
                    React.createElement("div", { className: "metric-icon" },
                        React.createElement(Icon, { name: "inbox" })),
                    React.createElement("small", null, "\u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F"),
                    React.createElement("strong", null, a.inbound),
                    React.createElement("span", null, "\u0417\u0430 \u0432\u0441\u0451 \u0432\u0440\u0435\u043C\u044F \u0432 \u0440\u0430\u0431\u043E\u0447\u0435\u0439 \u043E\u0431\u043B\u0430\u0441\u0442\u0438")),
                React.createElement("div", { className: "metric-card" },
                    React.createElement("div", { className: "metric-icon" },
                        React.createElement(Icon, { name: "clock" })),
                    React.createElement("small", null, "\u041F\u0440\u0438\u043D\u044F\u0442\u0438\u0435 \u043E\u0442\u0432\u0435\u0442\u0430"),
                    React.createElement("strong", null, a.avg_first_reply_min == null ? '—' : a.avg_first_reply_min + ' мин'),
                    React.createElement("span", null, "\u041E\u0442 \u043F\u0435\u0440\u0432\u043E\u0433\u043E \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F \u0434\u043E \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F API / \u0432\u0435\u0431-\u0447\u0430\u0442\u0430, \u0441 R28")),
                React.createElement("div", { className: "metric-card" },
                    React.createElement("div", { className: "metric-icon" },
                        React.createElement(Icon, { name: "bell" })),
                    React.createElement("small", null, "\u041E\u0436\u0438\u0434\u0430\u044E\u0442 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u043E\u0433\u043E \u043E\u0442\u0432\u0435\u0442\u0430"),
                    React.createElement("strong", null, a.no_response),
                    React.createElement("span", null, "\u0427\u0435\u0440\u043D\u043E\u0432\u0438\u043A \u0438 \u043E\u0447\u0435\u0440\u0435\u0434\u044C \u043D\u0435 \u0441\u0447\u0438\u0442\u0430\u044E\u0442\u0441\u044F \u043E\u0442\u0432\u0435\u0442\u043E\u043C")),
                React.createElement("div", { className: "metric-card" },
                    React.createElement("div", { className: "metric-icon" },
                        React.createElement(Icon, { name: "check" })),
                    React.createElement("small", null, "\u041D\u0443\u0436\u0434\u0430\u044E\u0442\u0441\u044F \u0432 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0435"),
                    React.createElement("strong", null, a.outgoing_attention || 0),
                    React.createElement("span", null, "\u041E\u0448\u0438\u0431\u043A\u0430 \u0438\u043B\u0438 \u043D\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043D\u044B\u0439 \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442 \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438"))),
            React.createElement("p", { className: "metrics-delivery-note", role: "status" },
                "\u0418\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u0438 \u0438\u043B\u0438 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0435: ",
                React.createElement("strong", null, a.outgoing_pending || 0),
                ". \u041F\u043E\u043A\u0430\u0437\u0430\u0442\u0435\u043B\u044C \u0432\u0440\u0435\u043C\u0435\u043D\u0438 \u0432\u043A\u043B\u044E\u0447\u0430\u0435\u0442 \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u043E\u0432\u044B\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u0441 R28; \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0443 \u0438 \u043F\u0440\u043E\u0447\u0442\u0435\u043D\u0438\u0435 \u043E\u0442\u0434\u0435\u043B\u044C\u043D\u043E \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0430."),
            React.createElement("div", { className: "analytics-grid" },
                React.createElement("div", { className: "chart-card" },
                    React.createElement("div", { className: "card-title" },
                        React.createElement("h3", null, "\u0414\u0438\u043D\u0430\u043C\u0438\u043A\u0430 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439"),
                        React.createElement("span", null, "\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 7 \u0434\u043D\u0435\u0439")),
                    React.createElement("div", { className: "chart-bars" }, a.days.map((d, i) => React.createElement("div", { className: "bar-column", key: i },
                        React.createElement("div", { className: "bar-number" }, d.count),
                        React.createElement("div", { className: "bar-track" },
                            React.createElement("div", { className: "bar-fill", style: { height: Math.max(4, (d.count / max) * 100) + '%' } })),
                        React.createElement("span", null, d.day))))),
                React.createElement("div", { className: "chart-card" },
                    React.createElement("div", { className: "card-title" },
                        React.createElement("h3", null, "\u0418\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0438 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439"),
                        React.createElement("span", null, "\u041F\u043E \u043A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u0443 \u0434\u0438\u0430\u043B\u043E\u0433\u043E\u0432")),
                    React.createElement("div", { className: "channel-chart" }, CHANNELS.map(ch => { const count = a.by_channel[ch] || 0; return React.createElement("div", { className: "channel-row", key: ch },
                        React.createElement("div", { className: "channel-name" },
                            React.createElement(Provider, { type: ch }),
                            React.createElement("strong", null, providerName(ch)),
                            React.createElement("span", null, count)),
                        React.createElement("div", { className: "progress-track" },
                            React.createElement("div", { className: 'progress-fill ' + ch, style: { width: (a.conversations ? count / a.conversations * 100 : 0) + '%' } }))); })))),
            React.createElement("div", { className: "revenue-row" },
                React.createElement("div", null,
                    React.createElement("div", { className: "revenue-head" }, "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u0430\u044F \u0432\u044B\u0440\u0443\u0447\u043A\u0430"),
                    React.createElement("strong", null, formatMoney(a.confirmed_revenue, a.currency)),
                    React.createElement("small", null, "\u0422\u043E\u043B\u044C\u043A\u043E \u0441\u0434\u0435\u043B\u043A\u0438, \u043E\u0442\u043C\u0435\u0447\u0435\u043D\u043D\u044B\u0435 \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u043E\u043C \u043A\u0430\u043A \u0443\u0441\u043F\u0435\u0448\u043D\u044B\u0435 \u0438 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u044B\u0435")),
                React.createElement("div", null,
                    React.createElement("div", { className: "revenue-head" }, "\u041F\u043E\u0442\u0435\u043D\u0446\u0438\u0430\u043B \u0441\u0434\u0435\u043B\u043E\u043A"),
                    React.createElement("strong", null, formatMoney(a.potential_revenue, a.currency)),
                    React.createElement("small", null, "\u041E\u0446\u0435\u043D\u043A\u0430 \u043F\u043E \u0441\u0443\u043C\u043C\u0430\u043C, \u0432\u0432\u0435\u0434\u0451\u043D\u043D\u044B\u043C \u0432\u0440\u0443\u0447\u043D\u0443\u044E \u2014 \u043D\u0435 \u0444\u0430\u043A\u0442\u0438\u0447\u0435\u0441\u043A\u0430\u044F \u0432\u044B\u0440\u0443\u0447\u043A\u0430")),
                React.createElement("div", null,
                    React.createElement("div", { className: "revenue-head" }, "\u041A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044F \u0432 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u0443\u044E \u0441\u0434\u0435\u043B\u043A\u0443"),
                    React.createElement("strong", null,
                        a.conversion_pct,
                        "%"),
                    React.createElement("small", null,
                        a.confirmed_deals,
                        " \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u044B\u0445 \u0441\u0434\u0435\u043B\u043E\u043A \u0438\u0437 ",
                        a.conversations,
                        " \u0434\u0438\u0430\u043B\u043E\u0433\u043E\u0432"))),
            React.createElement("div", { className: "analytics-disclaimer" },
                React.createElement(Icon, { name: "info", size: 17 }),
                " \u041F\u043E\u043A\u0430\u0437\u0430\u0442\u0435\u043B\u0438 \u043E\u0441\u043D\u043E\u0432\u0430\u043D\u044B \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430 \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0445 \u0441\u043E\u0431\u044B\u0442\u0438\u044F\u0445. \u0411\u0435\u0437 \u0434\u0430\u043D\u043D\u044B\u0445 \u043A\u0430\u0441\u0441\u044B \u0438\u043B\u0438 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440\u0430 \u043F\u043B\u0430\u0442\u0444\u043E\u0440\u043C\u0430 \u043D\u0435 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u044F\u0435\u0442 \u0440\u0435\u0430\u043B\u044C\u043D\u044B\u0435 \u043F\u0440\u043E\u0434\u0430\u0436\u0438."));
    }
    renderRules() { const s = this.state; return React.createElement("div", { className: "page-content" },
        React.createElement("div", { className: "section-head" },
            React.createElement("div", null,
                React.createElement("div", { className: "eyebrow" }, "\u0421\u0426\u0415\u041D\u0410\u0420\u0418\u0418 / \u0411\u0415\u0417 \u041E\u0411\u042F\u0417\u0410\u0422\u0415\u041B\u042C\u041D\u041E\u0413\u041E \u0418\u0418"),
                React.createElement("h1", null, "\u0410\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u044F"),
                React.createElement("p", null, "\u041F\u0440\u043E\u0437\u0440\u0430\u0447\u043D\u044B\u0435 \u043F\u0440\u0430\u0432\u0438\u043B\u0430 \u0431\u0435\u0437 \u0438\u0441\u043A\u0443\u0441\u0441\u0442\u0432\u0435\u043D\u043D\u043E\u0433\u043E \u0438\u043D\u0442\u0435\u043B\u043B\u0435\u043A\u0442\u0430: \u0441\u043E\u0431\u044B\u0442\u0438\u0435 \u2192 \u0443\u0441\u043B\u043E\u0432\u0438\u0435 \u2192 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435.")),
            React.createElement("button", { className: "btn primary", onClick: () => this.setState({ modal: 'rule' }) },
                React.createElement(Icon, { name: "plus", size: 17 }),
                " \u041D\u043E\u0432\u043E\u0435 \u043F\u0440\u0430\u0432\u0438\u043B\u043E")),
        React.createElement("div", { className: "flow-visual" },
            React.createElement("div", null,
                React.createElement("div", { className: "flow-step" }, "01"),
                React.createElement(Icon, { name: "bell", size: 20 }),
                React.createElement("strong", null, "\u0421\u043E\u0431\u044B\u0442\u0438\u0435"),
                React.createElement("small", null, "\u041D\u043E\u0432\u043E\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435")),
            React.createElement("span", { className: "flow-connector" },
                React.createElement(Icon, { name: "arrow" })),
            React.createElement("div", null,
                React.createElement("div", { className: "flow-step" }, "02"),
                React.createElement(Icon, { name: "filter", size: 20 }),
                React.createElement("strong", null, "\u0423\u0441\u043B\u043E\u0432\u0438\u0435"),
                React.createElement("small", null, "\u041A\u043B\u044E\u0447\u0435\u0432\u0430\u044F \u0444\u0440\u0430\u0437\u0430")),
            React.createElement("span", { className: "flow-connector" },
                React.createElement(Icon, { name: "arrow" })),
            React.createElement("div", null,
                React.createElement("div", { className: "flow-step" }, "03"),
                React.createElement(Icon, { name: "sparkles", size: 20 }),
                React.createElement("strong", null, "\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435"),
                React.createElement("small", null, "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0442\u0435\u0433"))),
        React.createElement("div", { className: "table-card" },
            React.createElement("div", { className: "table-heading" },
                React.createElement("h3", null, "\u0410\u043A\u0442\u0438\u0432\u043D\u044B\u0435 \u0441\u0446\u0435\u043D\u0430\u0440\u0438\u0438"),
                React.createElement("span", null,
                    s.rules.length,
                    " \u043F\u0440\u0430\u0432\u0438\u043B")),
            s.rules.length === 0 ? React.createElement("div", { className: "empty-list" },
                React.createElement("p", null, "\u0421\u043E\u0437\u0434\u0430\u0439\u0442\u0435 \u043F\u0435\u0440\u0432\u043E\u0435 \u043F\u0440\u0430\u0432\u0438\u043B\u043E \u0434\u043B\u044F \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439")) : s.rules.map((r) => React.createElement("div", { className: "rule-row", key: r.id },
                React.createElement("div", { className: "rule-icon" },
                    React.createElement(Icon, { name: "flow", size: 20 })),
                React.createElement("div", null,
                    React.createElement("strong", null, r.name),
                    React.createElement("p", null,
                        r.condition_type === 'always' ? 'Для каждого сообщения' : `Если содержит «${r.condition_value}»`,
                        " \u2192 ",
                        r.action_type === 'tag' ? `Добавить тег «${r.action_value}»` : r.action_type === 'priority' ? 'Закрепить диалог' : r.action_type === 'assign_least_busy' ? 'Назначить свободного менеджера' : `Изменить статус: ${r.action_value}`)),
                React.createElement("button", { className: 'toggle ' + (r.enabled ? 'on' : ''), onClick: () => this.toggleRule(r.id), title: r.enabled ? 'Выключить правило' : 'Включить правило', "aria-label": "\u0412\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u0438\u043B\u0438 \u0432\u044B\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u0438\u043B\u043E" },
                    React.createElement("span", null))))),
        React.createElement("div", { className: "analytics-disclaimer" },
            React.createElement(Icon, { name: "info", size: 16 }),
            " \u041F\u0440\u0430\u0432\u0438\u043B\u0430 \u0437\u0430\u043F\u0443\u0441\u043A\u0430\u044E\u0442\u0441\u044F \u043F\u0440\u0438 \u043D\u043E\u0432\u044B\u0445 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F\u0445; \u043D\u0435 \u043C\u0435\u043D\u044F\u044E\u0442 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044E\u0449\u0438\u0435 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0438 \u0437\u0430\u0434\u043D\u0438\u043C \u0447\u0438\u0441\u043B\u043E\u043C.")); }
    renderWebsites() {
        const s = this.state, selected = s.sites.find((w) => w.id === s.siteSelected);
        const canEdit = ['owner', 'admin'].includes(s.me.role);
        const snippet = (w) => '<script async src="' + (location.origin === 'null' ? 'https://your-omnichat-domain.example' : location.origin) + '/assets/embed.js" data-omnichat-key="' + w.key + '"></script>';
        return React.createElement("div", { className: "page-content website-page" },
            React.createElement("div", { className: "section-head" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow" }, "\u0421\u041E\u0411\u0421\u0422\u0412\u0415\u041D\u041D\u042B\u0419 \u041A\u0410\u041D\u0410\u041B / \u0411\u0415\u0417 \u0412\u041D\u0415\u0428\u041D\u0418\u0425 API-\u041A\u041B\u042E\u0427\u0415\u0419"),
                    React.createElement("h1", null, "\u0427\u0430\u0442 \u0434\u043B\u044F \u0432\u0430\u0448\u0435\u0433\u043E \u0441\u0430\u0439\u0442\u0430"),
                    React.createElement("p", null, "\u0421\u043E\u0431\u0441\u0442\u0432\u0435\u043D\u043D\u044B\u0439 \u0447\u0430\u0442 \u0434\u043B\u044F \u0441\u0430\u0439\u0442\u0430. \u0412\u0441\u0435 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F \u043F\u043E\u0441\u0435\u0442\u0438\u0442\u0435\u043B\u0435\u0439 \u043F\u043E\u043F\u0430\u0434\u0430\u044E\u0442 \u0432 \u0435\u0434\u0438\u043D\u044B\u0439 \u0446\u0435\u043D\u0442\u0440 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439.")),
                React.createElement("div", { className: "website-top-label" },
                    React.createElement("span", { className: "dot green" }),
                    " \u0421\u041E\u0411\u0421\u0422\u0412\u0415\u041D\u041D\u042B\u0419 \u041A\u0410\u041D\u0410\u041B")),
            React.createElement("div", { className: "site-feature-grid" },
                React.createElement("div", { className: "site-feature" },
                    React.createElement(Icon, { name: "shield", size: 21 }),
                    React.createElement("strong", null, "\u0417\u0430\u0449\u0438\u0442\u0430 \u043F\u043E \u0430\u0440\u0445\u0438\u0442\u0435\u043A\u0442\u0443\u0440\u0435"),
                    React.createElement("span", null, "\u041D\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043C\u044B\u0435 \u0441\u0435\u0441\u0441\u0438\u0438 \u043F\u043E\u0441\u0435\u0442\u0438\u0442\u0435\u043B\u0435\u0439 \u0438 \u0437\u0430\u0449\u0438\u0449\u0451\u043D\u043D\u044B\u0439 \u0434\u043E\u0441\u0442\u0443\u043F")),
                React.createElement("div", { className: "site-feature" },
                    React.createElement(Icon, { name: "inbox", size: 21 }),
                    React.createElement("strong", null, "\u0415\u0434\u0438\u043D\u0430\u044F \u043E\u0447\u0435\u0440\u0435\u0434\u044C \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439"),
                    React.createElement("span", null, "\u0421\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u043D\u0430\u0441\u0442\u043E\u044F\u0449\u0438\u0445 \u043F\u043E\u0441\u0435\u0442\u0438\u0442\u0435\u043B\u0435\u0439 \u0441\u0430\u0439\u0442\u0430, \u0430 \u043D\u0435 \u0438\u043C\u0438\u0442\u0430\u0446\u0438\u044F \u0432\u043D\u0435\u0448\u043D\u0435\u0433\u043E API")),
                React.createElement("div", { className: "site-feature" },
                    React.createElement(Icon, { name: "clock", size: 21 }),
                    React.createElement("strong", null, "\u041C\u0433\u043D\u043E\u0432\u0435\u043D\u043D\u044B\u0439 \u043A\u043E\u043D\u0442\u0430\u043A\u0442"),
                    React.createElement("span", null, "\u041E\u0442\u0432\u0435\u0442 \u043E\u043F\u0435\u0440\u0430\u0442\u043E\u0440\u0430 \u043F\u043E\u044F\u0432\u043B\u044F\u0435\u0442\u0441\u044F \u043F\u0440\u044F\u043C\u043E \u0432 \u0432\u0438\u0434\u0436\u0435\u0442\u0435"))),
            canEdit && React.createElement("div", { className: "site-config" },
                React.createElement("div", { className: "site-config-title" },
                    React.createElement("div", { className: "eyebrow" }, "01 / \u041D\u0410\u0421\u0422\u0420\u041E\u0419\u041A\u0410 \u041A\u0410\u041D\u0410\u041B\u0410"),
                    React.createElement("h2", null, selected ? 'Редактирование виджета' : 'Новый виджет сайта'),
                    React.createElement("p", null, "\u0414\u043B\u044F \u043F\u0443\u0431\u043B\u0438\u0447\u043D\u044B\u0445 \u0441\u0430\u0439\u0442\u043E\u0432 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043D\u044B \u0442\u043E\u043B\u044C\u043A\u043E \u0430\u0434\u0440\u0435\u0441\u0430 HTTPS. \u041B\u043E\u043A\u0430\u043B\u044C\u043D\u044B\u0439 HTTP \u2014 \u0434\u043B\u044F \u0440\u0430\u0437\u0440\u0430\u0431\u043E\u0442\u043A\u0438.")),
                React.createElement("div", { className: "site-form" },
                    React.createElement("label", null,
                        "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0432\u0438\u0434\u0436\u0435\u0442\u0430",
                        React.createElement("input", { placeholder: "\u041F\u043E\u0434\u0434\u0435\u0440\u0436\u043A\u0430 \u043A\u043B\u0438\u0435\u043D\u0442\u043E\u0432", value: s.siteName, onChange: (e) => this.setState({ siteName: e.target.value }) })),
                    React.createElement("label", null,
                        "\u0420\u0430\u0437\u0440\u0435\u0448\u0451\u043D\u043D\u044B\u0435 \u0430\u0434\u0440\u0435\u0441\u0430 \u0441\u0430\u0439\u0442\u043E\u0432",
                        React.createElement("textarea", { rows: 2, placeholder: 'https://store.example.com\nhttps://www.store.example.com', value: s.siteOrigins, onChange: (e) => this.setState({ siteOrigins: e.target.value }) })),
                    React.createElement("label", null,
                        "\u041F\u0440\u0438\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0435 \u043F\u043E\u0441\u0435\u0442\u0438\u0442\u0435\u043B\u044F",
                        React.createElement("input", { value: s.siteGreeting, onChange: (e) => this.setState({ siteGreeting: e.target.value }) })),
                    React.createElement("label", null,
                        "\u0410\u043A\u0446\u0435\u043D\u0442\u043D\u044B\u0439 \u0446\u0432\u0435\u0442",
                        React.createElement("input", { type: "color", value: s.siteAccent, onChange: (e) => this.setState({ siteAccent: e.target.value }) })),
                    React.createElement("div", { className: "site-form-actions" },
                        React.createElement("button", { className: "btn primary", disabled: s.loading || !s.siteName.trim() || !s.siteOrigins.trim(), onClick: () => this.saveSiteWidget() },
                            React.createElement(Icon, { name: selected ? 'check' : 'plus', size: 16 }),
                            selected ? 'Сохранить изменения' : 'Создать канал сайта'),
                        selected && React.createElement("button", { className: "btn secondary", onClick: () => this.clearSiteForm() }, "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F")))),
            React.createElement("div", { className: "site-channels-header" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow" }, "02 / \u0423\u0421\u0422\u0410\u041D\u041E\u0412\u041A\u0410"),
                    React.createElement("h2", null,
                        "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D\u043D\u044B\u0435 \u0441\u0430\u0439\u0442\u044B ",
                        React.createElement("span", null, s.sites.length)))),
            s.sites.length === 0 ? React.createElement("div", { className: "site-empty" },
                React.createElement("div", { className: "site-empty-icon" },
                    React.createElement(Icon, { name: "globe", size: 32 })),
                React.createElement("h3", null, "\u0421\u0430\u0439\u0442\u044B \u0435\u0449\u0451 \u043D\u0435 \u0434\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u044B"),
                React.createElement("p", null, "\u0421\u043E\u0437\u0434\u0430\u0439\u0442\u0435 \u043A\u0430\u043D\u0430\u043B \u0438 \u0434\u043E\u0431\u0430\u0432\u044C\u0442\u0435 \u043A\u043E\u0434 \u043D\u0430 \u0441\u0430\u0439\u0442. \u0421\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u0441\u0440\u0430\u0437\u0443 \u043F\u043E\u044F\u0432\u044F\u0442\u0441\u044F \u0432 \u0440\u0430\u0437\u0434\u0435\u043B\u0435 \u00AB\u0421\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F\u00BB \u0441 \u0444\u0438\u043B\u044C\u0442\u0440\u043E\u043C \u00AB\u0427\u0430\u0442 \u0441\u0430\u0439\u0442\u0430\u00BB.")) :
                React.createElement("div", { className: "site-cards" }, s.sites.map((w) => React.createElement("article", { className: "site-card", key: w.id },
                    React.createElement("div", { className: "site-card-heading" },
                        React.createElement("div", { className: "site-card-identity" },
                            React.createElement("div", { className: "site-card-logo" },
                                React.createElement(Icon, { name: "globe", size: 21 })),
                            React.createElement("div", null,
                                React.createElement("h3", null, w.name),
                                React.createElement("p", null, w.allowed_origins.join(' / ')))),
                        React.createElement("span", { className: 'pill ' + (w.enabled ? 'green' : 'neutral') },
                            React.createElement("span", { className: "dot" }),
                            !w.enabled ? 'Приостановлен' : w.is_demo ? 'Тестовый' : 'Активен')),
                    React.createElement("div", { className: "site-card-content" },
                        React.createElement("div", { className: "site-embed" },
                            React.createElement("div", { className: "site-small-label" }, "\u0423\u0421\u0422\u0410\u041D\u041E\u0412\u041A\u0410 \u041E\u0414\u041D\u041E\u0419 \u0421\u0422\u0420\u041E\u041A\u041E\u0419"),
                            React.createElement("pre", null, snippet(w)),
                            React.createElement("div", { className: "site-card-actions" },
                                React.createElement("button", { className: "btn secondary", onClick: () => this.copySnippet(snippet(w)) },
                                    React.createElement(Icon, { name: "copy", size: 16 }),
                                    " \u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043A\u043E\u0434"),
                                React.createElement("button", { className: "btn secondary", onClick: () => window.open('/widget/' + w.key, '_blank', 'noopener,noreferrer') },
                                    React.createElement(Icon, { name: "arrow", size: 15 }),
                                    " \u041E\u0442\u043A\u0440\u044B\u0442\u044C \u043F\u0440\u0435\u0434\u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440"),
                                canEdit && React.createElement("button", { className: "btn secondary", onClick: () => this.startEditSite(w) },
                                    React.createElement(Icon, { name: "settings", size: 15 }),
                                    " \u0418\u0437\u043C\u0435\u043D\u0438\u0442\u044C"),
                                canEdit && React.createElement("button", { className: "btn ghost", onClick: () => this.toggleSiteWidget(w) }, w.enabled ? 'Приостановить' : 'Включить'),
                                canEdit && React.createElement("button", { className: "btn ghost", onClick: () => this.rotateSiteWidget(w) },
                                    React.createElement(Icon, { name: "shield", size: 14 }),
                                    " \u0421\u043C\u0435\u043D\u0438\u0442\u044C \u043A\u043B\u044E\u0447")),
                            React.createElement("div", { className: "site-tip" }, "\u0412\u0441\u0442\u0430\u0432\u044C\u0442\u0435 \u0441\u043A\u0440\u0438\u043F\u0442 \u043F\u0435\u0440\u0435\u0434 \u0437\u0430\u043A\u0440\u044B\u0432\u0430\u044E\u0449\u0438\u043C \u0442\u0435\u0433\u043E\u043C body. \u0415\u0441\u043B\u0438 \u0441\u0430\u0439\u0442 \u0438\u0441\u043F\u043E\u043B\u044C\u0437\u0443\u0435\u0442 \u0441\u0442\u0440\u043E\u0433\u0443\u044E \u043F\u043E\u043B\u0438\u0442\u0438\u043A\u0443 \u0431\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E\u0441\u0442\u0438, \u0440\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u0435 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0443 \u0441\u043A\u0440\u0438\u043F\u0442\u043E\u0432 \u0432\u0430\u0448\u0435\u0433\u043E \u0434\u043E\u043C\u0435\u043D\u0430.")),
                        React.createElement("div", { className: "site-visual" },
                            React.createElement("div", { className: "site-preview-title" }, "\u041F\u0420\u0415\u0414\u041F\u0420\u041E\u0421\u041C\u041E\u0422\u0420 \u0412\u0418\u0414\u0416\u0415\u0422\u0410"),
                            React.createElement("iframe", { loading: "lazy", title: 'Предпросмотр: ' + w.name, src: '/widget/' + w.key })))))),
            React.createElement("div", { className: "analytics-disclaimer" },
                React.createElement(Icon, { name: "shield", size: 16 }),
                " \u041F\u0443\u0431\u043B\u0438\u0447\u043D\u044B\u0439 \u043A\u043B\u044E\u0447 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u044F\u0435\u0442 \u0432\u0438\u0434\u0436\u0435\u0442, \u043D\u043E \u043D\u0435 \u0440\u0430\u0441\u043A\u0440\u044B\u0432\u0430\u0435\u0442 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0438. \u041F\u043E\u0441\u0435\u0442\u0438\u0442\u0435\u043B\u0438 \u043F\u043E\u043B\u0443\u0447\u0430\u044E\u0442 \u043E\u0442\u0434\u0435\u043B\u044C\u043D\u044B\u0435 \u0442\u043E\u043A\u0435\u043D\u044B \u0434\u043E\u0441\u0442\u0443\u043F\u0430, \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u0435 \u0447\u0430\u0441\u0442\u043E\u0442\u044B \u0437\u0430\u043F\u0440\u043E\u0441\u043E\u0432 \u0438 \u0438\u0437\u043E\u043B\u0438\u0440\u043E\u0432\u0430\u043D\u043D\u044B\u0435 \u0437\u0430\u043F\u0438\u0441\u0438 \u0432 \u0431\u0430\u0437\u0435."));
    }
    renderOperations() {
        const s = this.state, o = s.operations;
        if (!o)
            return React.createElement("div", { className: "page-content" }, "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043C \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0443 \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0438...");
        const queues = [['queued', 'В очереди'], ['processing', 'Отправляется'], ['uncertain', 'Нужна проверка'], ['failed', 'Ошибка'], ['done', 'Принято API']];
        const humanStatus = { queued: 'В очереди', processing: 'Отправляется', uncertain: 'Требует проверки', failed: 'Ошибка', done: 'Принято API', cancelled: 'Отменено до отправки' };
        const inbound = o.inbound || {};
        const nextStep = o.organization_outbound_paused_at ? 'Все новые исходящие компании остановлены. Проверьте причины инцидента и разрешения аккаунтов перед возобновлением.' : o.reconciliation_required > 0
            ? 'Есть ответы с неизвестным результатом. Сначала проверьте их в исходной соцсети: повторная отправка может создать дубль.'
            : o.outbox_delayed_over_5_min > 0
                ? 'Некоторые ответы ждут больше пяти минут. Проверьте подключение канала и состояние фонового обработчика.'
                : inbound.failed > 0
                    ? 'Есть входящие события, которые не удалось обработать. Проверьте настройки канала и используйте повтор после устранения ошибки.'
                    : o.outbox.failed > 0
                        ? 'Есть сообщения с ошибкой. Откройте строку ниже и проверьте, почему площадка не приняла ответ.'
                        : 'Очередь не требует срочного вмешательства. Новые ответы будут обрабатываться автоматически.';
        return React.createElement("div", { className: "page-content operations-page" },
            React.createElement("div", { className: "section-head" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow" }, "\u041E\u041F\u0415\u0420\u0410\u0426\u0418\u0418 / \u041A\u041E\u041D\u0422\u0420\u041E\u041B\u042C \u0414\u041E\u0421\u0422\u0410\u0412\u041A\u0418"),
                    React.createElement("h1", null, "\u041A\u043E\u043D\u0442\u0440\u043E\u043B\u044C \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0438"),
                    React.createElement("p", null, "\u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u044F, \u0438\u0441\u0445\u043E\u0434\u044F\u0449\u0430\u044F \u043E\u0447\u0435\u0440\u0435\u0434\u044C \u0438 \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043A\u0430\u043D\u0430\u043B\u043E\u0432. \u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F \u043D\u0435 \u043F\u043E\u0434\u043C\u0435\u043D\u044F\u044E\u0442\u0441\u044F \u043F\u0440\u0435\u0434\u043F\u043E\u043B\u043E\u0436\u0435\u043D\u0438\u044F\u043C\u0438.")),
                React.createElement("button", { className: "btn secondary", onClick: () => this.loadView('operations') },
                    React.createElement(Icon, { name: "arrow", size: 16 }),
                    " \u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435")),
            React.createElement("section", { className: 'ops-global-guard ' + (o.organization_outbound_paused_at ? 'is-paused' : ''), "aria-label": "\u0410\u0432\u0430\u0440\u0438\u0439\u043D\u0430\u044F \u0437\u0430\u0449\u0438\u0442\u0430 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438", role: "status" },
                React.createElement("div", { className: "ops-global-guard-title" },
                    React.createElement(Icon, { name: "shield", size: 23 }),
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "\u0410\u0412\u0410\u0420\u0418\u0419\u041D\u0410\u042F \u0417\u0410\u0429\u0418\u0422\u0410 \u041A\u041E\u041C\u041F\u0410\u041D\u0418\u0418"),
                        React.createElement("strong", null, o.organization_outbound_paused_at ? 'Все новые исходящие приостановлены' : 'Отправка компании разрешена'),
                        React.createElement("p", null, o.organization_outbound_paused_at
                            ? 'Входящие сообщения работают. Новые ответы через соцсети ждут в очереди. Начатые до паузы запросы могли завершиться.'
                            : 'При инциденте можно остановить отправки всех аккаунтов одним действием. Отдельные паузы каналов сохранятся.'))),
                ['owner', 'admin'].includes(s.me.role) && !s.me.organization.is_demo && React.createElement("button", { className: 'btn ' + (o.organization_outbound_paused_at ? 'secondary' : 'ghost'), disabled: s.loading, onClick: () => this.pauseCompanyOutbound(o.organization_outbound_paused_at || null) },
                    React.createElement(Icon, { name: o.organization_outbound_paused_at ? 'check' : 'shield', size: 16 }),
                    o.organization_outbound_paused_at ? 'Возобновить все исходящие' : 'Остановить все исходящие')),
            React.createElement("section", { className: "ops-section ops-r36-safety", "aria-label": "\u0412\u0440\u0435\u043C\u0435\u043D\u043D\u044B\u0435 \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u044F \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438" },
                React.createElement("div", { className: "ops-title" },
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "R36 / \u041A\u041E\u041D\u0422\u0420\u041E\u041B\u042C \u0420\u0418\u0421\u041A\u041E\u0412"),
                        React.createElement("h2", null, "\u0412\u0440\u0435\u043C\u0435\u043D\u043D\u0430\u044F \u043F\u0430\u0443\u0437\u0430 \u043E\u0442\u043F\u0440\u0430\u0432\u043E\u043A"),
                        React.createElement("p", null, "\u0414\u043B\u044F \u0430\u0432\u0430\u0440\u0438\u0439 \u0438 \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0445 \u0440\u0430\u0431\u043E\u0442. \u041D\u043E\u0432\u044B\u0435 \u0437\u0430\u0445\u0432\u0430\u0442\u044B \u0431\u043B\u043E\u043A\u0438\u0440\u0443\u044E\u0442\u0441\u044F \u0432 \u0431\u0430\u0437\u0435; \u0443\u0436\u0435 \u043D\u0430\u0447\u0430\u0442\u044B\u0435 \u0437\u0430\u043F\u0440\u043E\u0441\u044B \u043A \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0435 \u043C\u043E\u0433\u0443\u0442 \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C\u0441\u044F.")),
                    ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn secondary", onClick: this.exportSafeSupport, disabled: s.loading },
                        React.createElement(Icon, { name: "shield", size: 16 }),
                        " \u0421\u043A\u0430\u0447\u0430\u0442\u044C \u043E\u0431\u0435\u0437\u043B\u0438\u0447\u0435\u043D\u043D\u044B\u0439 \u043E\u0442\u0447\u0451\u0442")),
                React.createElement("div", { className: "ops-r36-indicators", role: "status" },
                    React.createElement("div", null,
                        React.createElement("span", null, "\u0410\u043A\u0442\u0438\u0432\u043D\u044B\u0445 \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u0439"),
                        React.createElement("strong", null, s.dispatchPauses?.pauses?.length || 0)),
                    React.createElement("div", null,
                        React.createElement("span", null, "\u0418\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0441 \u043D\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043D\u044B\u043C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u043E\u043C"),
                        React.createElement("strong", null, s.deliveryTelemetry?.outbox?.uncertain || 0)),
                    React.createElement("div", null,
                        React.createElement("span", null, "\u041E\u0447\u0435\u0440\u0435\u0434\u044C \u0431\u043E\u043B\u0435\u0435 \u043F\u044F\u0442\u0438 \u043C\u0438\u043D\u0443\u0442"),
                        React.createElement("strong", null, s.deliveryTelemetry?.delayed_queued_over_5m || 0))),
                s.deliveryTelemetry?.alerts?.length > 0 && React.createElement("div", { className: "ops-r36-alerts", role: "status" }, s.deliveryTelemetry.alerts.map((a) => React.createElement("span", { className: "pill amber", key: a.code },
                    { uncertain: 'Нужна проверка отправок', worker_offline: 'Фоновый обработчик не отвечает', queue_delayed: 'Задержка очереди', recent_failures: 'Ошибки отправки', delivery_paused: 'Отправка приостановлена' }[a.code] || a.code,
                    ": ",
                    a.count))),
                ['owner', 'admin'].includes(s.me.role) && React.createElement("div", { className: "ops-r36-controls" },
                    React.createElement("label", null,
                        "\u041E\u0431\u043B\u0430\u0441\u0442\u044C",
                        React.createElement("select", { "aria-label": "\u041E\u0431\u043B\u0430\u0441\u0442\u044C \u0432\u0440\u0435\u043C\u0435\u043D\u043D\u043E\u0439 \u043F\u0430\u0443\u0437\u044B", value: s.opsPauseChannel, onChange: (e) => this.setState({ opsPauseChannel: e.target.value }) },
                            React.createElement("option", { value: "" }, "\u0412\u0441\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F"),
                            (o.channels || []).filter((c) => c.mode === 'live').map((c) => React.createElement("option", { key: c.id, value: c.id },
                                providerName(c.provider),
                                " \u00B7 ",
                                c.name)))),
                    React.createElement("label", null,
                        "\u041F\u0440\u0438\u0447\u0438\u043D\u0430",
                        React.createElement("select", { "aria-label": "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u0432\u0440\u0435\u043C\u0435\u043D\u043D\u043E\u0439 \u043F\u0430\u0443\u0437\u044B", value: s.opsPauseReason, onChange: (e) => this.setState({ opsPauseReason: e.target.value }) },
                            React.createElement("option", { value: "incident" }, "\u0418\u043D\u0446\u0438\u0434\u0435\u043D\u0442"),
                            React.createElement("option", { value: "provider_outage" }, "\u0421\u0431\u043E\u0439 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0438"),
                            React.createElement("option", { value: "credential_rotation" }, "\u0417\u0430\u043C\u0435\u043D\u0430 \u043A\u043B\u044E\u0447\u0430"),
                            React.createElement("option", { value: "maintenance" }, "\u041E\u0431\u0441\u043B\u0443\u0436\u0438\u0432\u0430\u043D\u0438\u0435"))),
                    React.createElement("label", null,
                        "\u0410\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u043E\u0435 \u0441\u043D\u044F\u0442\u0438\u0435",
                        React.createElement("select", { "aria-label": "\u0421\u0440\u043E\u043A \u0432\u0440\u0435\u043C\u0435\u043D\u043D\u043E\u0439 \u043F\u0430\u0443\u0437\u044B", value: s.opsPauseMinutes, onChange: (e) => this.setState({ opsPauseMinutes: e.target.value }) },
                            React.createElement("option", { value: "15" }, "15 \u043C\u0438\u043D\u0443\u0442"),
                            React.createElement("option", { value: "60" }, "1 \u0447\u0430\u0441"),
                            React.createElement("option", { value: "240" }, "4 \u0447\u0430\u0441\u0430"),
                            React.createElement("option", { value: "1440" }, "24 \u0447\u0430\u0441\u0430"),
                            React.createElement("option", { value: "unlimited" }, "\u0422\u043E\u043B\u044C\u043A\u043E \u0432\u0440\u0443\u0447\u043D\u0443\u044E"))),
                    React.createElement("button", { className: "btn secondary", disabled: s.loading, onClick: this.pauseDispatch },
                        React.createElement(Icon, { name: "shield", size: 16 }),
                        " \u0412\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u043F\u0430\u0443\u0437\u0443")),
                (s.dispatchPauses?.pauses || []).length > 0 && React.createElement("div", { className: "ops-r36-pauses" }, s.dispatchPauses.pauses.map((entry, i) => React.createElement("div", { key: (entry.channel_id || 'all') + i },
                    React.createElement("span", { className: "pill amber" }, "\u041F\u0430\u0443\u0437\u0430"),
                    React.createElement("strong", null, entry.channel_id ? ((o.channels || []).find((v) => v.id === entry.channel_id)?.name || 'Аккаунт') : 'Вся компания'),
                    React.createElement("small", null,
                        { incident: 'Инцидент', provider_outage: 'Сбой площадки', credential_rotation: 'Замена ключа', maintenance: 'Обслуживание' }[entry.reason_code] || 'Обслуживание',
                        " \u00B7 ",
                        entry.expires_at ? ('до ' + new Date(entry.expires_at * 1000).toLocaleString('ru-RU')) : 'снятие вручную'),
                    ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn ghost", onClick: () => this.resumeDispatch(entry.channel_id), disabled: s.loading }, "\u0421\u043D\u044F\u0442\u044C"))))),
            React.createElement("section", { className: "ops-next-step", "aria-label": "\u0421\u043B\u0435\u0434\u0443\u044E\u0449\u0435\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435" },
                React.createElement("div", null,
                    React.createElement("strong", null, "\u0427\u0442\u043E \u0441\u0434\u0435\u043B\u0430\u0442\u044C \u0441\u0435\u0439\u0447\u0430\u0441"),
                    React.createElement("p", null, nextStep)),
                o.reconciliation_required > 0 && React.createElement("span", { className: "pill amber" },
                    o.reconciliation_required,
                    " ",
                    o.reconciliation_required === 1 ? 'требует' : 'требуют',
                    " \u0441\u0432\u0435\u0440\u043A\u0438")),
            React.createElement("div", { className: "ops-metrics" }, queues.map(([key, label]) => React.createElement("div", { className: 'ops-metric ' + (key === 'uncertain' && o.outbox[key] ? 'warning' : ''), key: key },
                React.createElement("span", null, label),
                React.createElement("strong", null, o.outbox[key] || 0),
                React.createElement("small", null, key === 'uncertain' ? 'Требуется ручная проверка' : key === 'done' ? 'Принято сервисом / проверено' : 'Надёжная очередь отправки')))),
            React.createElement("div", { className: 'worker-signal ' + ((o.worker?.code === 'working' || o.worker?.code === 'not_needed') ? 'healthy' : 'attention'), role: "status", "aria-live": "polite" },
                React.createElement(Icon, { name: o.worker?.code === 'working' ? 'check' : 'activity', size: 20 }),
                React.createElement("div", null,
                    React.createElement("strong", null, o.worker?.summary || 'Состояние обработчика неизвестно'),
                    React.createElement("p", null, o.worker?.code === 'working' ? 'Фоновая отправка работает. Принятие внешним API не равно доставке клиенту.' :
                        o.worker?.code === 'not_needed' ? 'Новые сообщения с сайтов обрабатываются отдельно. Подключённые соцсети требуют работающего обработчика.' :
                            o.worker?.code === 'checking' ? 'Сервер запущен, но завершённого цикла пока нет. Подождите немного и обновите страницу.' :
                                'Если внешние ответы стоят в очереди, проверьте запуск фонового обработчика на сервере.')),
                React.createElement("button", { className: "btn secondary", onClick: () => this.loadView('operations'), disabled: s.loading }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0441\u043D\u043E\u0432\u0430")),
            React.createElement("div", { className: "ops-stats" },
                React.createElement("div", null,
                    React.createElement(Icon, { name: "globe", size: 20 }),
                    React.createElement("strong", null, o.channel_total),
                    React.createElement("span", null, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D\u043D\u044B\u0435 \u0438 \u0442\u0435\u0441\u0442\u043E\u0432\u044B\u0435 \u043A\u0430\u043D\u0430\u043B\u044B")),
                React.createElement("div", null,
                    React.createElement(Icon, { name: "inbox", size: 20 }),
                    React.createElement("strong", null, o.messages_total),
                    React.createElement("span", null, "\u0421\u043E\u0445\u0440\u0430\u043D\u0451\u043D\u043D\u044B\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F")),
                React.createElement("div", null,
                    React.createElement(Icon, { name: "clock", size: 20 }),
                    React.createElement("strong", null, o.outbox_delayed_over_5_min),
                    React.createElement("span", null, "\u041E\u0436\u0438\u0434\u0430\u044E\u0442 \u0431\u043E\u043B\u0435\u0435 5 \u043C\u0438\u043D\u0443\u0442"))),
            React.createElement("section", { className: "ops-section" },
                React.createElement("div", { className: "ops-title" },
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "01 / \u0421\u041E\u0421\u0422\u041E\u042F\u041D\u0418\u0415 \u041E\u0422\u041F\u0420\u0410\u0412\u041A\u0418"),
                        React.createElement("h2", null, "\u0418\u0441\u0445\u043E\u0434\u044F\u0449\u0430\u044F \u043E\u0447\u0435\u0440\u0435\u0434\u044C")),
                    React.createElement("div", { className: "ops-title-tags" },
                        React.createElement("span", { className: "pill neutral" },
                            "\u041E\u0442\u043C\u0435\u043D\u0435\u043D\u043E \u0434\u043E \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438: ",
                            o.outbox.cancelled || 0),
                        o.active_sender_accounts > 0 && React.createElement("span", { className: "pill green" },
                            "\u0421\u0435\u0439\u0447\u0430\u0441 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u044E\u0442: ",
                            o.active_sender_accounts,
                            " ",
                            o.active_sender_accounts === 1 ? 'аккаунт' : 'аккаунтов'),
                        o.outbound_paused_channels > 0 && React.createElement("span", { className: "pill amber" },
                            "\u0410\u043A\u043A\u0430\u0443\u043D\u0442\u043E\u0432 \u0441 \u043F\u0430\u0443\u0437\u043E\u0439 \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438: ",
                            o.outbound_paused_channels),
                        o.safe_recoveries_last_7_days > 0 && React.createElement("span", { className: "pill green" },
                            "\u0412\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u043E \u0431\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E: ",
                            o.safe_recoveries_last_7_days),
                        o.whatsapp_receipts_last_24h > 0 && React.createElement("span", { className: "pill neutral" },
                            "\u041A\u0432\u0438\u0442\u0430\u043D\u0446\u0438\u0439 WhatsApp \u0437\u0430 24 \u0447: ",
                            o.whatsapp_receipts_last_24h),
                        React.createElement("span", { className: "pill neutral" }, "\u0421\u0442\u0430\u0442\u0443\u0441\u044B \u043E\u0441\u043D\u043E\u0432\u0430\u043D\u044B \u043D\u0430 \u0441\u043E\u0431\u044B\u0442\u0438\u044F\u0445 \u0432 \u0431\u0430\u0437\u0435"))),
                s.operationsJobs.length === 0 ? React.createElement("div", { className: "ops-empty" }, "\u0418\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0437\u0430\u0434\u0430\u043D\u0438\u0439 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442. \u041E\u0442\u0432\u0435\u0442\u044B \u0432 \u0447\u0430\u0442 \u0441\u0430\u0439\u0442\u0430 \u0434\u043E\u0441\u0442\u0430\u0432\u043B\u044F\u044E\u0442\u0441\u044F \u043D\u0430\u043F\u0440\u044F\u043C\u0443\u044E \u0438 \u043D\u0435 \u043F\u043E\u043F\u0430\u0434\u0430\u044E\u0442 \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u044C \u0432\u043D\u0435\u0448\u043D\u0438\u0445 API.") :
                    React.createElement("div", { className: "table-scroll" },
                        React.createElement("table", null,
                            React.createElement("thead", null,
                                React.createElement("tr", null,
                                    React.createElement("th", null, "\u0418\u0414\u0415\u041D\u0422\u0418\u0424\u0418\u041A\u0410\u0422\u041E\u0420"),
                                    React.createElement("th", null, "\u0421\u0422\u0410\u0422\u0423\u0421"),
                                    React.createElement("th", null, "\u041F\u041E\u041F\u042B\u0422\u041A\u0418"),
                                    React.createElement("th", null, "\u041E\u0422\u0412\u0415\u0422 \u041F\u041B\u041E\u0429\u0410\u0414\u041A\u0418"),
                                    React.createElement("th", null, "\u041F\u0420\u041E\u0412\u0415\u0420\u041A\u0410"))),
                            React.createElement("tbody", null, s.operationsJobs.map((j) => React.createElement("tr", { key: j.id },
                                React.createElement("td", { className: "ops-mono" },
                                    j.message_id.slice(0, 13),
                                    "..."),
                                React.createElement("td", null,
                                    React.createElement("span", { className: 'pill ' + (j.status === 'uncertain' || j.status === 'failed' ? 'amber' : j.status === 'done' ? 'green' : 'neutral') }, j.processing_phase || humanStatus[j.status] || 'Неизвестно')),
                                React.createElement("td", null, j.attempts),
                                React.createElement("td", { className: "ops-error" }, j.last_error || '—'),
                                React.createElement("td", null,
                                    React.createElement("div", { className: "ops-job-actions" },
                                        j.status === 'uncertain' && ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn secondary", onClick: () => this.setState({ modal: 'reconcile', reconcileJob: j, reconcileStatus: 'accepted', reconcileEvidence: '', reconcileExternalId: '' }) }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442"),
                                        React.createElement("button", { className: "btn ghost", disabled: s.loading, onClick: () => this.loadJobEvents(j.id) }, "\u0418\u0441\u0442\u043E\u0440\u0438\u044F"),
                                        j.can_cancel && ['owner', 'admin', 'lead'].includes(s.me.role) && React.createElement("button", { className: "btn secondary", disabled: s.loading, onClick: () => this.cancelQueued(j) }, "\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C \u0434\u043E \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438"),
                                        j.can_retry_verified && ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn secondary", disabled: s.loading, onClick: () => this.setState({ modal: 'retry-outbox', outboxRetryJob: j, outboxRetryEvidence: '', outboxRetryVerified: false }) }, "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C \u043F\u043E\u0441\u043B\u0435 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438"),
                                        !['uncertain', 'queued', 'failed'].includes(j.status) && React.createElement("span", { className: "muted" }, "\u2014"))))))))),
            s.selectedJobEvents && React.createElement("section", { className: "ops-section ops-r36-history", "aria-label": "\u0418\u0441\u0442\u043E\u0440\u0438\u044F \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0445 \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0439" },
                React.createElement("div", { className: "ops-title" },
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "R36 / \u0418\u0421\u0422\u041E\u0420\u0418\u042F"),
                        React.createElement("h2", null, "\u041F\u0435\u0440\u0435\u0445\u043E\u0434\u044B \u0438\u0441\u0445\u043E\u0434\u044F\u0449\u0435\u0433\u043E \u0437\u0430\u0434\u0430\u043D\u0438\u044F"),
                        React.createElement("p", null, "\u0422\u043E\u043B\u044C\u043A\u043E \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0441\u0442\u0430\u0442\u0443\u0441\u044B \u0438 \u0432\u0440\u0435\u043C\u044F. \u0422\u0435\u043A\u0441\u0442 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u0438 \u0434\u0430\u043D\u043D\u044B\u0435 \u043A\u043B\u0438\u0435\u043D\u0442\u0430 \u043D\u0435 \u0441\u043E\u0445\u0440\u0430\u043D\u044F\u044E\u0442\u0441\u044F.")),
                    React.createElement("button", { className: "btn ghost", onClick: () => this.setState({ selectedJobEvents: null }) }, "\u0421\u043A\u0440\u044B\u0442\u044C")),
                React.createElement("div", { className: "ops-r36-timeline" },
                    s.selectedJobEvents.events.length === 0 ? React.createElement("span", { className: "muted" }, "\u0421\u043E\u0431\u044B\u0442\u0438\u0439 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442: \u0436\u0443\u0440\u043D\u0430\u043B \u043D\u0430\u0447\u0438\u043D\u0430\u0435\u0442\u0441\u044F \u0441 \u043E\u0431\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F R36.") : s.selectedJobEvents.events.map((item, i) => React.createElement("div", { key: i },
                        React.createElement("span", null, new Date(item.at * 1000).toLocaleString('ru-RU')),
                        React.createElement("strong", null, item.event_code),
                        React.createElement("small", null,
                            item.from_status,
                            " \u2192 ",
                            item.to_status,
                            " \u00B7 \u043F\u043E\u043F\u044B\u0442\u043A\u0438: ",
                            item.attempts))),
                    s.selectedJobEvents.truncated && React.createElement("span", { className: "muted" }, "\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u044B \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 100 \u0441\u043E\u0431\u044B\u0442\u0438\u0439"))),
            React.createElement("section", { className: "ops-section ops-inbound-section", "aria-label": "\u041D\u0430\u0434\u0451\u0436\u043D\u043E\u0441\u0442\u044C \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0441\u043E\u0431\u044B\u0442\u0438\u0439" },
                React.createElement("div", { className: "ops-title" },
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "02 / \u0417\u0410\u0429\u0418\u0422\u0410 \u0412\u0425\u041E\u0414\u042F\u0429\u0418\u0425"),
                        React.createElement("h2", null, "\u041F\u0440\u0438\u0451\u043C \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u0439"),
                        React.createElement("p", { className: "ops-inbound-intro" }, "\u0421\u043E\u0431\u044B\u0442\u0438\u0435 \u0441\u043D\u0430\u0447\u0430\u043B\u0430 \u0441\u043E\u0445\u0440\u0430\u043D\u044F\u0435\u0442\u0441\u044F \u0437\u0430\u0448\u0438\u0444\u0440\u043E\u0432\u0430\u043D\u043D\u044B\u043C. \u041F\u0440\u0438 \u0441\u0431\u043E\u0435 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0430 \u043F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u0441\u044F. \u0422\u0435\u043A\u0441\u0442 \u043A\u043B\u0438\u0435\u043D\u0442\u0430 \u0432 \u0436\u0443\u0440\u043D\u0430\u043B\u0435 \u043D\u0435 \u043E\u0442\u043E\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044F.")),
                    React.createElement("div", { className: "ops-title-tags" },
                        (inbound.failed || 0) > 0 && React.createElement("span", { className: "pill amber" },
                            "\u0422\u0440\u0435\u0431\u0443\u044E\u0442 \u0440\u0430\u0437\u0431\u043E\u0440\u0430: ",
                            inbound.failed),
                        (inbound.dismissed || 0) > 0 && React.createElement("span", { className: "pill neutral" },
                            "\u0417\u0430\u043A\u0440\u044B\u0442\u044B \u0441 \u0443\u0434\u0430\u043B\u0435\u043D\u0438\u0435\u043C: ",
                            inbound.dismissed),
                        (inbound.queued || 0) + (inbound.retrying || 0) + (inbound.processing || 0) > 0 && React.createElement("span", { className: "pill neutral" },
                            "\u0412 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0435: ",
                            (inbound.queued || 0) + (inbound.retrying || 0) + (inbound.processing || 0)))),
                React.createElement("div", { className: "ops-inbound-control", "aria-label": "\u0423\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u043E\u0439 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445" },
                    React.createElement("div", { className: "ops-control-copy" },
                        React.createElement("strong", null, "\u0423\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u043F\u0440\u0438 \u0438\u043D\u0446\u0438\u0434\u0435\u043D\u0442\u0435"),
                        React.createElement("span", null, "\u041F\u0430\u0443\u0437\u0430 \u043E\u0441\u0442\u0430\u043D\u0430\u0432\u043B\u0438\u0432\u0430\u0435\u0442 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0443, \u043D\u043E \u043D\u0435 \u043F\u0440\u0438\u0451\u043C \u043F\u0440\u043E\u0432\u0435\u0440\u0435\u043D\u043D\u044B\u0445 webhook. \u0421\u043E\u0431\u044B\u0442\u0438\u044F \u043E\u0441\u0442\u0430\u044E\u0442\u0441\u044F \u0437\u0430\u0448\u0438\u0444\u0440\u043E\u0432\u0430\u043D\u043D\u044B\u043C\u0438 \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u0438."),
                        !!o.inbound_delayed_over_10_min && React.createElement("span", { className: "ops-aging-alert" },
                            "\u041E\u0436\u0438\u0434\u0430\u044E\u0442 \u0431\u043E\u043B\u0435\u0435 10 \u043C\u0438\u043D\u0443\u0442: ",
                            o.inbound_delayed_over_10_min)),
                    React.createElement("div", { className: "ops-control-actions" },
                        React.createElement("label", { className: "ops-control-select" },
                            "\u041E\u0431\u043B\u0430\u0441\u0442\u044C",
                            React.createElement("select", { "aria-label": "\u041E\u0431\u043B\u0430\u0441\u0442\u044C \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0438 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445", value: s.inboundControlScope, onChange: (e) => this.setState({ inboundControlScope: e.target.value }) },
                                React.createElement("option", { value: "organization" }, "\u0412\u0441\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F"),
                                (o.channels || []).filter((c) => c.mode === 'live').map((c) => React.createElement("option", { key: c.id, value: c.id },
                                    providerName(c.provider),
                                    " \u00B7 ",
                                    c.name)))),
                        (() => {
                            const item = (o.channels || []).find((c) => c.id === s.inboundControlScope);
                            const paused = s.inboundControlScope === 'organization' ? !!o.organization_inbound_paused_at : !!item?.inbound_paused_at;
                            return React.createElement("button", { className: 'btn ' + (paused ? 'secondary' : 'ghost'), disabled: s.loading || !['owner', 'admin'].includes(s.me.role), onClick: () => this.setState({ modal: 'inbound-pause', inboundPauseAction: paused ? 'resume' : 'pause', inboundPauseReason: '' }) }, paused ? 'Возобновить обработку' : 'Поставить входящие на паузу');
                        })()),
                    (!!o.organization_inbound_paused_at || o.inbound_paused_channels > 0) && React.createElement("p", { className: "ops-paused-notice", role: "status" },
                        React.createElement(Icon, { name: "info", size: 16 }),
                        " \u0412\u0445\u043E\u0434\u044F\u0449\u0430\u044F \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0430 \u043F\u0440\u0438\u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0430: ",
                        o.organization_inbound_paused_at ? 'вся компания' : 'отдельные каналы',
                        ". \u041D\u043E\u0432\u044B\u0435 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F \u0441\u043E\u0445\u0440\u0430\u043D\u044F\u044E\u0442\u0441\u044F, \u043D\u043E \u043D\u0435 \u043F\u043E\u044F\u0432\u043B\u044F\u044E\u0442\u0441\u044F \u0432 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0430\u0445 \u0434\u043E \u0432\u043E\u0437\u043E\u0431\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F. \u0422\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0439 \u0441\u0440\u043E\u043A \u0445\u0440\u0430\u043D\u0435\u043D\u0438\u044F \u2014 14 \u0434\u043D\u0435\u0439.")),
                React.createElement("div", { className: "ops-inbound-metrics" },
                    React.createElement("div", null,
                        React.createElement("span", null, "\u041E\u0431\u0440\u0430\u0431\u043E\u0442\u0430\u043D\u043E"),
                        React.createElement("strong", null, inbound.done || 0),
                        React.createElement("small", null, "\u0421\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u043E \u0432 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0430\u0445")),
                    React.createElement("div", null,
                        React.createElement("span", null, "\u041E\u0436\u0438\u0434\u0430\u044E\u0442 / \u043F\u043E\u0432\u0442\u043E\u0440\u044F\u044E\u0442\u0441\u044F"),
                        React.createElement("strong", null, (inbound.queued || 0) + (inbound.retrying || 0) + (inbound.processing || 0)),
                        React.createElement("small", null, "\u041F\u043E\u0441\u043B\u0435 \u043E\u0448\u0438\u0431\u043A\u0438 \u043F\u043E\u0432\u0442\u043E\u0440 \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u0438")),
                    React.createElement("div", { className: (inbound.failed || 0) ? 'warn' : '' },
                        React.createElement("span", null, "\u0422\u0440\u0435\u0431\u0443\u044E\u0442 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438"),
                        React.createElement("strong", null, inbound.failed || 0),
                        React.createElement("small", null, "\u041F\u043E\u0441\u043B\u0435 \u043F\u044F\u0442\u0438 \u043D\u0435\u0443\u0434\u0430\u0447\u043D\u044B\u0445 \u043F\u043E\u043F\u044B\u0442\u043E\u043A")),
                    React.createElement("div", null,
                        React.createElement("span", null, "\u0410\u043A\u043A\u0430\u0443\u043D\u0442\u044B \u043E\u0431\u0440\u0430\u0431\u0430\u0442\u044B\u0432\u0430\u044E\u0442"),
                        React.createElement("strong", null, o.inbound_active_accounts || 0),
                        React.createElement("small", null, o.inbound_stalled_claims > 0 ? 'Зависшие захваты: ' + o.inbound_stalled_claims : 'Отправка входящих в Inbox'))),
                s.inboundIntegrity && React.createElement("div", { className: "ops-r35-integrity", role: "region", "aria-label": "\u0426\u0435\u043B\u043E\u0441\u0442\u043D\u043E\u0441\u0442\u044C \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0439 \u043E\u0447\u0435\u0440\u0435\u0434\u0438" },
                    React.createElement("div", { className: "ops-r35-integrity-copy" },
                        React.createElement("div", { className: "eyebrow small" }, "\u041F\u0420\u041E\u0412\u0415\u0420\u041A\u0410 \u0426\u0415\u041B\u041E\u0421\u0422\u041D\u041E\u0421\u0422\u0418 R35"),
                        React.createElement("strong", null, "\u0411\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E\u0441\u0442\u044C \u0438 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435 SQL-\u043E\u0447\u0435\u0440\u0435\u0434\u0438"),
                        React.createElement("p", null,
                            "\u041F\u0440\u043E\u0441\u0440\u043E\u0447\u0435\u043D\u043D\u044B\u0435 \u0437\u0430\u0445\u0432\u0430\u0442\u044B: ",
                            React.createElement("b", null, s.inboundIntegrity.expired_claims || 0),
                            " \u00B7 \u0417\u0430\u0432\u0438\u0441\u0448\u0438\u0435 \u0431\u043B\u043E\u043A\u0438\u0440\u043E\u0432\u043A\u0438: ",
                            React.createElement("b", null, s.inboundIntegrity.expired_channel_slots || 0),
                            " \u00B7 \u0417\u0430\u043F\u0438\u0441\u0438 \u0431\u0435\u0437 \u0441\u043E\u0434\u0435\u0440\u0436\u0438\u043C\u043E\u0433\u043E: ",
                            React.createElement("b", null, s.inboundIntegrity.missing_payload || 0)),
                        s.inboundIntegrity.invalid_channel_bindings > 0 && React.createElement("p", { className: "ops-r35-alert" },
                            "\u041D\u0430\u0440\u0443\u0448\u0435\u043D\u044B \u0441\u0432\u044F\u0437\u0438 \u043A\u0430\u043D\u0430\u043B\u043E\u0432: ",
                            s.inboundIntegrity.invalid_channel_bindings,
                            ". \u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u0440\u0443\u0447\u043D\u0430\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0430; \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u043E\u0435 \u0438\u0441\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u0437\u0430\u043F\u0440\u0435\u0449\u0435\u043D\u043E."),
                        React.createElement("small", null, "\u041F\u0440\u043E\u0432\u0435\u0440\u043A\u0430 \u043D\u0435 \u0440\u0430\u0441\u043A\u0440\u044B\u0432\u0430\u0435\u0442 \u0442\u0435\u043A\u0441\u0442\u044B \u043A\u043B\u0438\u0435\u043D\u0442\u043E\u0432. \u0412\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435 \u043D\u0435 \u0437\u0430\u0442\u0440\u0430\u0433\u0438\u0432\u0430\u0435\u0442 \u0430\u043A\u0442\u0438\u0432\u043D\u044B\u0435 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0438.")),
                    ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn secondary", disabled: s.loading, onClick: () => this.setState({ modal: 'inbound-repair', inboundRepairReason: '', inboundRepairConfirmed: false }) },
                        React.createElement(Icon, { name: "shield", size: 16 }),
                        " \u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0438 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C")),
                React.createElement("div", { className: "ops-inbound-health", "aria-label": "\u0417\u0434\u043E\u0440\u043E\u0432\u044C\u0435 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u043F\u043E \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430\u043C" },
                    React.createElement("div", { className: "ops-inbound-health-title" },
                        React.createElement("strong", null, "\u0414\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0430 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u043F\u043E \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430\u043C"),
                        React.createElement("span", null,
                            s.inboundHealth?.critical_count || 0,
                            " \u043A\u0440\u0438\u0442\u0438\u0447\u0435\u0441\u043A\u0438\u0445 \u00B7 ",
                            s.inboundHealth?.warning_count || 0,
                            " \u0442\u0440\u0435\u0431\u0443\u044E\u0442 \u0432\u043D\u0438\u043C\u0430\u043D\u0438\u044F \u00B7 \u043B\u0438\u043C\u0438\u0442 ",
                            s.inboundHealth?.capacity_per_channel || 5000,
                            " \u043D\u0430 \u043A\u0430\u043D\u0430\u043B")),
                    (s.inboundHealth?.channels || []).length === 0 ? React.createElement("p", { className: "muted" }, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D\u043D\u044B\u0445 \u0440\u0430\u0431\u043E\u0447\u0438\u0445 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u043E\u0432 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442.") :
                        React.createElement("div", { className: "ops-inbound-health-grid" }, (s.inboundHealth?.channels || []).slice(0, 8).map((ch) => React.createElement("div", { className: 'ops-inbound-health-card ' + ch.severity, key: ch.channel_id },
                            React.createElement("div", { className: "ops-inbound-health-header" },
                                React.createElement(Provider, { type: ch.provider, small: true }),
                                React.createElement("strong", null, ch.channel_name),
                                React.createElement("span", { className: 'pill ' + (ch.severity === 'critical' ? 'amber' : 'neutral') }, ch.severity === 'critical' ? 'Проверить' : ch.severity === 'warning' ? 'Задержка' : 'В норме')),
                            React.createElement("div", { className: "ops-inbound-health-stats" },
                                React.createElement("span", null,
                                    "\u041E\u0436\u0438\u0434\u0430\u044E\u0442: ",
                                    React.createElement("b", null, ch.pending)),
                                React.createElement("span", null,
                                    "\u041E\u0448\u0438\u0431\u043A\u0438: ",
                                    React.createElement("b", null, ch.failed)),
                                React.createElement("span", null,
                                    "\u0412\u043E\u0437\u0440\u0430\u0441\u0442: ",
                                    React.createElement("b", null, ch.oldest_pending_seconds == null ? '—' : Math.floor(ch.oldest_pending_seconds / 60) + ' мин'))),
                            React.createElement("div", { className: "ops-inbound-lease-info", "aria-live": "polite" }, ch.stalled_claims > 0
                                ? 'Зависшие обработки: ' + ch.stalled_claims + ' · требуется проверка'
                                : ch.actively_processing ? 'Обработка аккаунта выполняется · новые события ждут своей очереди' : 'Аккаунт свободен для обработки'),
                            React.createElement("div", { className: "ops-inbound-meter", "aria-label": 'Заполнение очереди ' + ch.capacity_percent + '%' },
                                React.createElement("span", { style: { width: Math.min(100, ch.capacity_percent) + '%' } })),
                            React.createElement("small", null,
                                "\u0417\u0430\u043F\u043E\u043B\u043D\u0435\u043D\u0438\u0435: ",
                                ch.capacity_percent,
                                "% ",
                                ch.paused ? '· Канал на паузе' : '')))),
                    s.inboundHealth?.truncated && React.createElement("p", { className: "muted" }, "\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u044B \u0434\u043E 50 \u043A\u0430\u043D\u0430\u043B\u043E\u0432 \u0441 \u043D\u0430\u0438\u0431\u043E\u043B\u044C\u0448\u0438\u043C \u0440\u0438\u0441\u043A\u043E\u043C. \u0421\u0447\u0451\u0442\u0447\u0438\u043A\u0438 \u0443\u0447\u0438\u0442\u044B\u0432\u0430\u044E\u0442 \u0432\u0441\u0435 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u044B \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438.")),
                React.createElement("div", { className: "ops-triage-head" },
                    React.createElement("div", { className: "ops-triage-filters", role: "group", "aria-label": "\u0424\u0438\u043B\u044C\u0442\u0440 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u0441\u043E\u0431\u044B\u0442\u0438\u0439" }, [['', 'Все'], ['failed', 'Ошибки'], ['queued', 'В очереди'], ['retrying', 'Повторяются'], ['done', 'Обработаны'], ['dismissed', 'Закрыты']].map(([code, label]) => React.createElement("button", { key: code, className: 'btn ' + (s.inboundTriageStatus === code ? 'primary' : 'ghost'), disabled: s.loading, onClick: () => this.loadInboundTriage(code, false) }, label))),
                    ['owner', 'admin'].includes(s.me.role) && React.createElement("div", { className: "ops-batch-controls" },
                        React.createElement("select", { "aria-label": "\u0410\u043A\u043A\u0430\u0443\u043D\u0442 \u0434\u043B\u044F \u043F\u0430\u043A\u0435\u0442\u043D\u043E\u0433\u043E \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F", value: s.inboundBatchChannel, onChange: (e) => this.setState({ inboundBatchChannel: e.target.value }) },
                            React.createElement("option", { value: "" }, "\u0410\u043A\u043A\u0430\u0443\u043D\u0442 \u0441 \u043E\u0448\u0438\u0431\u043A\u0430\u043C\u0438"),
                            (o.channels || []).filter((c) => c.inbound_failed > 0).map((c) => React.createElement("option", { key: c.id, value: c.id },
                                providerName(c.provider),
                                " \u00B7 ",
                                c.name,
                                " (",
                                c.inbound_failed,
                                ")"))),
                        React.createElement("button", { className: "btn secondary", disabled: !s.inboundBatchChannel || s.loading, onClick: this.openInboundBatchPreview }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0434\u043E 20 \u043E\u0448\u0438\u0431\u043E\u043A"))),
                (s.operationsInboundJobs || []).length === 0 ? React.createElement("div", { className: "ops-empty" }, "\u0421\u043E\u0431\u044B\u0442\u0438\u0439 \u0434\u043B\u044F \u0432\u044B\u0431\u0440\u0430\u043D\u043D\u043E\u0433\u043E \u0444\u0438\u043B\u044C\u0442\u0440\u0430 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442.") :
                    React.createElement("div", { className: "table-scroll" },
                        React.createElement("table", { className: "ops-inbound-table" },
                            React.createElement("thead", null,
                                React.createElement("tr", null,
                                    React.createElement("th", null, "\u0418\u0421\u0422\u041E\u0427\u041D\u0418\u041A"),
                                    React.createElement("th", null, "\u0421\u0422\u0410\u0422\u0423\u0421"),
                                    React.createElement("th", null, "\u041F\u041E\u041F\u042B\u0422\u041A\u0418"),
                                    React.createElement("th", null, "\u041F\u041E\u041B\u0423\u0427\u0415\u041D\u041E"),
                                    React.createElement("th", null, "\u0414\u0415\u0419\u0421\u0422\u0412\u0418\u0415"))),
                            React.createElement("tbody", null, (s.operationsInboundJobs || []).map((j) => React.createElement("tr", { key: j.id },
                                React.createElement("td", null,
                                    React.createElement("div", { className: "ops-inbound-source" },
                                        React.createElement(Provider, { type: j.provider, small: true }),
                                        React.createElement("span", null, providerName(j.provider)))),
                                React.createElement("td", null,
                                    React.createElement("span", { className: 'pill ' + (j.status === 'failed' ? 'amber' : j.status === 'done' ? 'green' : 'neutral') }, { queued: 'В очереди', retrying: 'Ожидает повтора', processing: 'Обрабатывается', failed: 'Требует проверки', done: 'Сохранено', expired: 'Истёк срок хранения', dismissed: 'Закрыто с удалением' }[j.status] || j.status)),
                                React.createElement("td", null, j.attempts),
                                React.createElement("td", { className: "ops-time" },
                                    dateFmt(j.created_at),
                                    " \u00B7 ",
                                    fmt(j.created_at)),
                                React.createElement("td", null,
                                    React.createElement("div", { className: "ops-job-actions" },
                                        j.can_retry && ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn secondary", disabled: s.loading, onClick: () => this.setState({ modal: 'retry-inbound', inboundRetryJob: j, inboundRetryReason: '' }) }, "\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C"),
                                        j.can_dismiss && ['owner', 'admin'].includes(s.me.role) && React.createElement("button", { className: "btn ghost", disabled: s.loading, onClick: () => this.setState({ modal: 'inbound-dismiss', inboundDismissJob: j, inboundDismissReason: '', inboundDismissCode: 'unrecoverable', inboundDismissConfirmed: false }) }, "\u0417\u0430\u043A\u0440\u044B\u0442\u044C \u0438 \u0443\u0434\u0430\u043B\u0438\u0442\u044C"),
                                        (!j.can_retry && !j.can_dismiss || !['owner', 'admin'].includes(s.me.role)) && React.createElement("span", { className: "muted" }, j.status === 'done' ? 'Готово' : j.status === 'dismissed' ? 'Без восстановления' : j.status === 'expired' ? 'Содержимое удалено' : 'Автоматически')))))))),
                s.inboundTriageCursor && React.createElement("button", { className: "btn secondary ops-more-button", disabled: s.loading, onClick: () => this.loadInboundTriage(s.inboundTriageStatus, true) }, "\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u0435\u0449\u0451 30 \u0441\u043E\u0431\u044B\u0442\u0438\u0439"),
                React.createElement("p", { className: "ops-inbound-footnote" }, "\u041F\u043E\u0432\u0442\u043E\u0440\u043D\u0430\u044F \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0430 \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0433\u043E \u043D\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u0442 \u043A\u043B\u0438\u0435\u043D\u0442\u0443 \u043E\u0442\u0432\u0435\u0442. \u0422\u0435\u043A\u0441\u0442 \u0441\u043E\u0431\u044B\u0442\u0438\u044F \u0443\u0434\u0430\u043B\u044F\u0435\u0442\u0441\u044F \u0438\u0437 \u043E\u0447\u0435\u0440\u0435\u0434\u0438 \u043F\u043E\u0441\u043B\u0435 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u044F \u0432 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0435.")),
            React.createElement("section", { className: "ops-section" },
                React.createElement("div", { className: "ops-title" },
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "03 / \u0417\u0414\u041E\u0420\u041E\u0412\u042C\u0415 \u041A\u0410\u041D\u0410\u041B\u041E\u0412"),
                        React.createElement("h2", null, "\u0421\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0439"))),
                React.createElement("div", { className: "ops-connections" }, o.channels.map((c) => React.createElement("div", { className: "ops-channel", key: c.id },
                    React.createElement(Provider, { type: c.provider }),
                    React.createElement("div", null,
                        React.createElement("strong", null, c.name),
                        React.createElement("small", null,
                            providerName(c.provider),
                            " \u00B7 ",
                            c.mode === 'demo' ? 'Демоканал' : c.status === 'connected' ? 'Подключён' : c.status === 'disconnected' ? 'Отключён' : c.status === 'error' ? 'Ошибка' : 'Ожидает проверки'),
                        c.outbound_paused_at && React.createElement("span", null, "\u041D\u043E\u0432\u044B\u0435 \u0438\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u043D\u0430 \u043F\u0430\u0443\u0437\u0435. \u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u0440\u0430\u0431\u043E\u0442\u0430\u044E\u0442."),
                        c.inbound_paused_at && React.createElement("span", null, "\u041E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0430 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445 \u044D\u0442\u043E\u0433\u043E \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430 \u043F\u0440\u0438\u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0430."),
                        c.inbound_failed > 0 && React.createElement("span", null,
                            "\u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u043D\u0430 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0435: ",
                            c.inbound_failed),
                        c.last_error && React.createElement("span", null, c.last_error)),
                    React.createElement("time", null, c.last_sync_at ? dateFmt(c.last_sync_at) : 'Нет синхронизации')))),
                o.channels_truncated && React.createElement("p", { className: "muted" }, "\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u044B \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 200 \u043A\u0430\u043D\u0430\u043B\u043E\u0432. \u041E\u0431\u0449\u0438\u0435 \u0441\u0447\u0451\u0442\u0447\u0438\u043A\u0438 \u0443\u0447\u0438\u0442\u044B\u0432\u0430\u044E\u0442 \u0432\u0441\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438.")),
            React.createElement("div", { className: "analytics-disclaimer" },
                React.createElement(Icon, { name: "shield", size: 16 }),
                " \u041E\u0447\u0435\u0440\u0435\u0434\u044C \u0440\u0430\u0441\u043F\u0440\u0435\u0434\u0435\u043B\u044F\u0435\u0442 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0443 \u043C\u0435\u0436\u0434\u0443 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F\u043C\u0438. \u0421\u0431\u043E\u0439 \u0434\u043E \u043D\u0430\u0447\u0430\u043B\u0430 \u0432\u043D\u0435\u0448\u043D\u0435\u0439 \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0438 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u0430\u0432\u043B\u0438\u0432\u0430\u0435\u0442\u0441\u044F \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u0438, \u0430 \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0430 \u0441 \u0432\u043E\u0437\u043C\u043E\u0436\u043D\u044B\u043C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u043E\u043C \u0442\u0440\u0435\u0431\u0443\u0435\u0442 \u0441\u0432\u0435\u0440\u043A\u0438. \u041F\u0440\u0438\u043D\u044F\u0442\u0438\u0435 API \u043D\u0435 \u0440\u0430\u0432\u043D\u043E \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0435 \u043A\u043B\u0438\u0435\u043D\u0442\u0443."));
    }
    renderIntegrations() {
        const s = this.state;
        const data = s.integrations;
        const guide = s.integrationGuide;
        if (!data)
            return React.createElement("div", { className: "page-content" }, "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043C \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F...");
        const demo = !!s.me.organization.is_demo;
        const owner = ['owner', 'admin'].includes(s.me.role);
        const oauth = new URLSearchParams(location.search).get('oauth');
        const types = ['avito', 'instagram', 'whatsapp', 'telegram', 'vk', 'max', 'messenger'];
        const liveConnections = data.connections.filter((c) => c.mode === 'live' && c.status !== 'disconnected');
        const counts = { ready: liveConnections.filter((c) => c.readiness?.ready_for_api_use).length,
            pending: liveConnections.filter((c) => !c.readiness?.ready_for_api_use).length };
        return React.createElement("div", { className: "page-content onboarding-page" },
            React.createElement("div", { className: "section-head" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow" }, "\u0412\u0410\u0428\u0418 \u0410\u041A\u041A\u0410\u0423\u041D\u0422\u042B / \u0415\u0414\u0418\u041D\u042B\u0419 INBOX"),
                    React.createElement("h1", null, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 \u043A\u0430\u043D\u0430\u043B\u043E\u0432"),
                    React.createElement("p", null, "\u041A\u0430\u0436\u0434\u0430\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0430\u0435\u0442 \u0441\u043E\u0431\u0441\u0442\u0432\u0435\u043D\u043D\u044B\u0435 \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0435 \u0431\u0438\u0437\u043D\u0435\u0441-\u0430\u043A\u043A\u0430\u0443\u043D\u0442\u044B. \u041F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0438 \u043E\u0440\u0433\u0430\u043D\u0438\u0437\u0430\u0446\u0438\u0439 \u043D\u0435 \u0441\u043C\u0435\u0448\u0438\u0432\u0430\u044E\u0442\u0441\u044F."))),
            demo && React.createElement("div", { className: "demo-notice" },
                React.createElement(Icon, { name: "info", size: 20 }),
                React.createElement("div", null,
                    React.createElement("strong", null, "\u0421\u0435\u0439\u0447\u0430\u0441 \u0432\u044B \u0432 \u0434\u0435\u043C\u043E\u043D\u0441\u0442\u0440\u0430\u0446\u0438\u0438"),
                    React.createElement("p", null, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 \u043D\u0430\u0441\u0442\u043E\u044F\u0449\u0438\u0445 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u043E\u0432 \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u043E \u043F\u043E\u0441\u043B\u0435 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438 \u0440\u0430\u0431\u043E\u0447\u0435\u0439 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438."))),
            oauth && React.createElement("div", { className: "demo-notice" },
                React.createElement(Icon, { name: "info", size: 18 }),
                oauth === 'pages' ? 'Facebook подтвердил вход. Выберите страницу ниже.' : oauth === 'connected' ? 'Аккаунт подтверждён, выполните проверку доставки.' : oauth === 'denied' ? 'Вы не предоставили разрешения.' : 'Авторизация не завершена. Проверьте права приложения.'),
            !demo && React.createElement("section", { className: "onboarding-intro" },
                React.createElement("div", null,
                    React.createElement("span", { className: "onboarding-step" }, "1"),
                    React.createElement("strong", null, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u0435 \u0430\u043A\u043A\u0430\u0443\u043D\u0442"),
                    React.createElement("small", null, "\u0410\u0432\u0442\u043E\u0440\u0438\u0437\u0443\u0439\u0442\u0435\u0441\u044C \u0447\u0435\u0440\u0435\u0437 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0443 \u0438\u043B\u0438 \u0432\u044B\u0434\u0430\u0439\u0442\u0435 \u0442\u043E\u043A\u0435\u043D \u0431\u043E\u0442\u0430.")),
                React.createElement("div", null,
                    React.createElement("span", { className: "onboarding-step" }, "2"),
                    React.createElement("strong", null, "\u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0435"),
                    React.createElement("small", null, "\u041F\u043E\u0434\u043F\u0438\u0448\u0438\u0442\u0435\u0441\u044C \u043D\u0430 \u0441\u043E\u0431\u044B\u0442\u0438\u044F \u0438 \u043E\u0442\u043F\u0440\u0430\u0432\u044C\u0442\u0435 \u043A\u043E\u043D\u0442\u0440\u043E\u043B\u044C\u043D\u043E\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435.")),
                React.createElement("div", null,
                    React.createElement("span", { className: "onboarding-step" }, "3"),
                    React.createElement("strong", null, "\u041E\u0442\u0432\u0435\u0442\u044C\u0442\u0435 \u0438\u0437 Inbox"),
                    React.createElement("small", null, "\u041E\u0442\u0432\u0435\u0442 \u0434\u043E\u043B\u0436\u0435\u043D \u043F\u043E\u044F\u0432\u0438\u0442\u044C\u0441\u044F \u0432 \u0438\u0441\u0445\u043E\u0434\u043D\u043E\u0439 \u0441\u043E\u0446\u0438\u0430\u043B\u044C\u043D\u043E\u0439 \u0441\u0435\u0442\u0438."))),
            !demo && guide && (!guide.https_ready || !guide.encryption_ready) && React.createElement("details", { className: "setup-preflight" },
                React.createElement("summary", null,
                    React.createElement(Icon, { name: "shield", size: 18 }),
                    React.createElement("span", null, "\u041D\u0443\u0436\u043D\u043E \u043F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C \u0441\u0435\u0440\u0432\u0435\u0440 \u0434\u043B\u044F \u043D\u0430\u0441\u0442\u043E\u044F\u0449\u0438\u0445 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439"),
                    React.createElement("strong", null,
                        Number(!guide.https_ready) + Number(!guide.encryption_ready),
                        " \u0448\u0430\u0433\u0430"),
                    React.createElement(Icon, { name: "chevron", size: 16 })),
                React.createElement("div", { className: "setup-preflight-details" },
                    React.createElement("p", null, "\u041F\u043E\u043A\u0430 \u043C\u043E\u0436\u043D\u043E \u0438\u0437\u0443\u0447\u0438\u0442\u044C \u0438\u043D\u0442\u0435\u0440\u0444\u0435\u0439\u0441 \u0438 \u043F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u0438\u0442\u044C \u0441\u0432\u043E\u0438 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u044B. \u041D\u0430\u0441\u0442\u043E\u044F\u0449\u0438\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u044F \u043F\u043E\u0441\u0442\u0443\u043F\u044F\u0442 \u0442\u043E\u043B\u044C\u043A\u043E \u043F\u043E\u0441\u043B\u0435 \u0431\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E\u0439 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u0430."),
                    !guide.https_ready && React.createElement("div", null,
                        React.createElement("strong", null, "\u041F\u0443\u0431\u043B\u0438\u0447\u043D\u044B\u0439 \u0437\u0430\u0449\u0438\u0449\u0451\u043D\u043D\u044B\u0439 \u0430\u0434\u0440\u0435\u0441"),
                        React.createElement("span", null, "\u0412\u043B\u0430\u0434\u0435\u043B\u0435\u0446 \u043F\u043B\u0430\u0442\u0444\u043E\u0440\u043C\u044B \u0434\u043E\u043B\u0436\u0435\u043D \u0443\u043A\u0430\u0437\u0430\u0442\u044C \u0430\u0434\u0440\u0435\u0441 OSMANX \u0441 HTTPS \u0432 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0435 PUBLIC_BASE_URL.")),
                    !guide.encryption_ready && React.createElement("div", null,
                        React.createElement("strong", null, "\u0417\u0430\u0449\u0438\u0442\u0430 \u043A\u043B\u044E\u0447\u0435\u0439 \u0441\u043E\u0446\u0441\u0435\u0442\u0435\u0439"),
                        React.createElement("span", null, "\u0412\u043B\u0430\u0434\u0435\u043B\u0435\u0446 \u043F\u043B\u0430\u0442\u0444\u043E\u0440\u043C\u044B \u0434\u043E\u043B\u0436\u0435\u043D \u043D\u0430\u0441\u0442\u0440\u043E\u0438\u0442\u044C INTEGRATION_ENCRYPTION_KEY \u043D\u0430 \u0441\u0435\u0440\u0432\u0435\u0440\u0435.")))),
            liveConnections.length > 0 && React.createElement("div", { className: "onboarding-summary" },
                React.createElement("span", null,
                    React.createElement("b", null, counts.ready),
                    " \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0430 \u0440\u0430\u0431\u043E\u0442\u0430 API"),
                React.createElement("span", null,
                    React.createElement("b", null, counts.pending),
                    " \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0439 \u043E\u0436\u0438\u0434\u0430\u044E\u0442 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438")),
            s.channelDiagnostics && React.createElement("section", { className: "onboarding-diagnostics", "aria-live": "polite", id: "channel-checkup" },
                React.createElement("div", { className: "onboarding-page-row" },
                    React.createElement("div", null,
                        React.createElement("h2", null, "\u041F\u0440\u043E\u0432\u0435\u0440\u043A\u0430 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F"),
                        React.createElement("p", null,
                            providerName(s.channelDiagnostics.provider || 'vk'),
                            " \u00B7 ",
                            s.channelDiagnostics.name || '')),
                    React.createElement("button", { className: "btn ghost", onClick: () => this.setState({ channelDiagnostics: null }) }, "\u0417\u0430\u043A\u0440\u044B\u0442\u044C")),
                React.createElement("div", { className: "channel-step-list" }, (s.channelDiagnostics.stages || []).map((stage, i) => React.createElement("div", { key: stage.key, className: 'channel-step ' + (stage.done ? 'is-complete' : 'is-pending') },
                    React.createElement("span", { className: "channel-step-mark" }, stage.done ? React.createElement(Icon, { name: "check", size: 16 }) : String(i + 1)),
                    React.createElement("div", null,
                        React.createElement("strong", null, stage.title),
                        React.createElement("p", null, stage.hint)),
                    React.createElement("span", { className: "channel-step-status" }, stage.done ? 'Подтверждено' : 'Ожидает')))),
                React.createElement("p", { className: "channel-next" },
                    React.createElement(Icon, { name: "info", size: 16 }),
                    s.channelDiagnostics.next_step),
                s.channelDiagnostics.provider_check_available && React.createElement("div", { className: "channel-live-check" },
                    React.createElement("div", null,
                        React.createElement("strong", null, "\u0421\u0432\u0435\u0440\u043A\u0430 \u0441 \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u043C API"),
                        React.createElement("small", null, s.channelDiagnostics.webhook_provider_verified ? 'Провайдер подтвердил адрес webhook' : 'Адрес webhook пока не сверялся с провайдером'),
                        s.channelDiagnostics.provider_error && React.createElement("small", null, s.channelDiagnostics.provider_error)),
                    React.createElement("button", { className: "btn secondary", onClick: () => this.verifyProviderHook(s.channelDiagnostics.id), disabled: s.loading }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u043F\u043E\u0434\u043F\u0438\u0441\u043A\u0443")),
                s.channelDiagnostics.global_meta_webhook_url && React.createElement("div", { className: "onboarding-copy" },
                    React.createElement("code", null, s.channelDiagnostics.global_meta_webhook_url),
                    React.createElement("button", { className: "btn ghost", onClick: () => navigator.clipboard?.writeText(s.channelDiagnostics.global_meta_webhook_url) }, "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C URL Meta")),
                s.channelDiagnostics.webhook_url && React.createElement("div", { className: "onboarding-copy" },
                    React.createElement("code", null, s.channelDiagnostics.webhook_url),
                    React.createElement("button", { className: "btn ghost", onClick: () => navigator.clipboard?.writeText(s.channelDiagnostics.webhook_url) }, "\u041A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C webhook")),
                s.channelDiagnostics.secretVisible && React.createElement("p", { className: "onboarding-secret" },
                    "\u041A\u043E\u043D\u0444\u0438\u0434\u0435\u043D\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0439 \u043A\u043E\u0434 VK: ",
                    React.createElement("code", null, s.channelDiagnostics.confirmation_token),
                    " \u00B7 \u0421\u0435\u043A\u0440\u0435\u0442 Callback: ",
                    React.createElement("code", null, s.channelDiagnostics.secret)),
                React.createElement("p", { className: "channel-disclaimer" }, "\u041F\u0440\u0438\u043D\u044F\u0442\u043E \u0432\u043D\u0435\u0448\u043D\u0438\u043C API \u2260 \u0434\u043E\u0441\u0442\u0430\u0432\u043B\u0435\u043D\u043E \u0438 \u043F\u0440\u043E\u0447\u0438\u0442\u0430\u043D\u043E \u043A\u043B\u0438\u0435\u043D\u0442\u043E\u043C. \u0414\u043B\u044F \u043E\u043A\u043E\u043D\u0447\u0430\u0442\u0435\u043B\u044C\u043D\u043E\u0439 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 \u043E\u0442\u0432\u0435\u0442 \u0434\u043E\u043B\u0436\u0435\u043D \u043F\u043E\u044F\u0432\u0438\u0442\u044C\u0441\u044F \u0432 \u043E\u0440\u0438\u0433\u0438\u043D\u0430\u043B\u044C\u043D\u043E\u043C \u043F\u0440\u0438\u043B\u043E\u0436\u0435\u043D\u0438\u0438.")),
            owner && s.messengerPages?.length > 0 && React.createElement("section", { className: "onboarding-pages" },
                React.createElement("h2", null, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u0443 Facebook"),
                React.createElement("p", null, "\u041F\u043E\u043A\u0430\u0437\u044B\u0432\u0430\u044E\u0442\u0441\u044F \u0442\u043E\u043B\u044C\u043A\u043E \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u044B, \u0434\u043B\u044F \u043A\u043E\u0442\u043E\u0440\u044B\u0445 \u0432\u044B \u0434\u0430\u043B\u0438 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043D\u0438\u0435 \u043D\u0430 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F Messenger."),
                s.messengerPages.map((page) => React.createElement("div", { className: "onboarding-page-row", key: page.id },
                    React.createElement("div", null,
                        React.createElement("strong", null, page.name),
                        React.createElement("small", null,
                            "ID \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u044B: ",
                            page.id)),
                    React.createElement("button", { className: "btn primary", onClick: () => this.connectMessengerPage(page.id), disabled: s.loading }, "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u0443")))),
            React.createElement("div", { className: "channel-chooser", role: "group", "aria-label": "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u043A\u0430\u043D\u0430\u043B \u0434\u043B\u044F \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438" },
                React.createElement("div", { className: "channel-chooser-title" },
                    React.createElement("strong", null, "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435, \u0447\u0442\u043E \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C"),
                    React.createElement("span", null, "\u041F\u043E\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u043C \u043E\u0434\u0438\u043D \u043A\u0430\u043D\u0430\u043B \u0437\u0430 \u0440\u0430\u0437, \u0447\u0442\u043E\u0431\u044B \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0430 \u0431\u044B\u043B\u0430 \u043F\u043E\u043D\u044F\u0442\u043D\u043E\u0439.")),
                React.createElement("div", { className: "channel-chooser-options" },
                    types.map(type => React.createElement("button", { key: type, type: "button", className: s.focusedProvider === type ? 'selected' : '', "aria-pressed": s.focusedProvider === type, onClick: () => this.setState({ focusedProvider: type, channelDiagnostics: null, channelDiagnosticsFor: '' }) },
                        React.createElement(Provider, { type: type, small: true }),
                        providerName(type),
                        data.connections.some((c) => c.provider === type && c.mode === 'live' && c.status !== 'disconnected') && React.createElement("span", { className: "channel-chooser-dot" }))),
                    React.createElement("button", { type: "button", className: s.focusedProvider === 'all' ? 'selected' : '', "aria-pressed": s.focusedProvider === 'all', onClick: () => this.setState({ focusedProvider: 'all' }) }, "\u0412\u0441\u0435 \u043A\u0430\u043D\u0430\u043B\u044B"))),
            React.createElement("div", { className: 'integration-grid ' + (s.focusedProvider === 'all' ? '' : 'focused-integration') }, types.filter(type => s.focusedProvider === 'all' || s.focusedProvider === type).map(type => {
                const cs = data.connections.filter((c) => c.provider === type);
                const active = cs.some((c) => c.mode === 'live' && c.status === 'connected');
                const readyForWork = cs.some((c) => c.mode === 'live' && c.readiness?.ready_for_api_use);
                const pending = cs.some((c) => c.mode === 'live' && c.status.startsWith('pending'));
                const instructions = guide?.providers?.[type];
                const descriptions = { avito: 'Сообщения покупателей по вашим объявлениям', instagram: 'Direct профессионального Instagram', whatsapp: 'Номер WhatsApp Business Platform', telegram: 'Сообщения вашего Telegram-бота', vk: 'Сообщения сообщества ВКонтакте', max: 'Диалоги с ботом MAX', messenger: 'Сообщения Facebook-страницы' };
                const ready = !!data.available[type];
                return React.createElement("div", { className: "integration-card", key: type },
                    React.createElement("div", { className: "integration-top" },
                        React.createElement(Provider, { type: type }),
                        React.createElement("span", { className: 'pill ' + (active ? 'green' : pending ? 'amber' : 'neutral') },
                            React.createElement("span", { className: "dot" }),
                            readyForWork ? 'API-обмен проверен' : active ? 'Входящие получены' : pending ? 'Ожидает проверки' : cs.some((c) => c.mode === 'demo') ? 'Демоканал' : 'Не подключён')),
                    React.createElement("h3", null, providerName(type)),
                    React.createElement("p", null, descriptions[type]),
                    cs.filter((c) => c.mode === 'live' || demo).map((c) => React.createElement("div", { className: "onboarding-connected", key: c.id },
                        React.createElement("strong", null, c.name),
                        React.createElement("small", null, c.mode === 'demo' ? 'Только тестовые сообщения' : c.last_error || c.readiness?.next_step || 'Откройте проверку подключения'),
                        c.mode === 'live' && c.outbound_paused_at && React.createElement("div", { className: "outbound-stop-note", role: "status" },
                            React.createElement(Icon, { name: "shield", size: 16 }),
                            React.createElement("span", null,
                                React.createElement("strong", null, "\u041D\u043E\u0432\u044B\u0435 \u0438\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u043F\u0440\u0438\u043E\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u044B."),
                                " \u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u0440\u0430\u0431\u043E\u0442\u0430\u044E\u0442; \u0437\u0430\u043F\u0440\u043E\u0441\u044B, \u043F\u0440\u043E\u0448\u0435\u0434\u0448\u0438\u0435 \u043A\u043E\u043D\u0442\u0440\u043E\u043B\u044C\u043D\u0443\u044E \u0442\u043E\u0447\u043A\u0443, \u043C\u043E\u0433\u0443\u0442 \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C\u0441\u044F.")),
                        c.mode === 'live' && c.readiness && React.createElement("div", { className: "channel-progress", role: "group", "aria-label": "\u041F\u0440\u043E\u0433\u0440\u0435\u0441\u0441 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438" },
                            React.createElement("span", null,
                                "\u042D\u0442\u0430\u043F\u044B: ",
                                c.readiness.stages.filter((x) => x.done).length,
                                " \u0438\u0437 4"),
                            React.createElement("div", { "aria-hidden": "true" }, c.readiness.stages.map((x) => React.createElement("i", { key: x.key, className: x.done ? 'complete' : '' })))),
                        c.mode === 'live' && owner && React.createElement("div", { className: "onboarding-actions" },
                            React.createElement("button", { className: "btn secondary", onClick: () => this.probeChannel(c.id) }, '\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435'),
                            React.createElement("button", { className: 'btn ' + (c.outbound_paused_at ? 'secondary' : 'ghost'), "aria-label": c.outbound_paused_at ? 'Возобновить исходящие' : 'Приостановить исходящие', onClick: () => this.pauseOutbound(c.id, !!c.outbound_paused_at), disabled: s.loading }, c.outbound_paused_at ? 'Возобновить исходящие' : 'Пауза исходящих'),
                            ['pending_webhook', 'needs_attention'].includes(c.status) && c.provider !== 'avito' && React.createElement("button", { className: "btn ghost", onClick: () => this.activateBot(c.id) }, "\u041D\u0430\u0441\u0442\u0440\u043E\u0438\u0442\u044C \u0441\u043E\u0431\u044B\u0442\u0438\u044F"),
                            ['telegram', 'max'].includes(c.provider) && React.createElement("button", { className: "btn ghost", onClick: () => this.verifyProviderHook(c.id) }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C webhook \u0443 \u0441\u0435\u0440\u0432\u0438\u0441\u0430"),
                            c.provider === 'avito' && React.createElement("button", { className: "btn ghost", onClick: () => this.syncAvito(c.id) }, "\u0421\u0438\u043D\u0445\u0440\u043E\u043D\u0438\u0437\u0438\u0440\u043E\u0432\u0430\u0442\u044C"),
                            React.createElement("details", { className: "channel-more" },
                                React.createElement("summary", null, "\u0414\u043E\u043F\u043E\u043B\u043D\u0438\u0442\u0435\u043B\u044C\u043D\u043E"),
                                React.createElement("div", null,
                                    React.createElement("button", { className: "btn ghost", onClick: () => this.diagnoseChannel(c.id) }, "\u0428\u0430\u0433\u0438 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438"),
                                    React.createElement("button", { className: "btn ghost", onClick: () => this.checkChannel(c.id) }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u0430"),
                                    ['telegram', 'vk', 'max', 'whatsapp'].includes(c.provider) && React.createElement("button", { className: "btn ghost", onClick: () => this.setState({ modal: 'rotate', rotateChannel: c.id, rotateToken: '' }) }, "\u0421\u043C\u0435\u043D\u0438\u0442\u044C \u0442\u043E\u043A\u0435\u043D"),
                                    c.provider === 'whatsapp' && React.createElement("button", { className: "btn ghost", onClick: () => this.setState({ modal: 'register-phone', registerPhoneChannel: c.id, registrationPin: '' }) }, "\u0417\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u043D\u043E\u043C\u0435\u0440"),
                                    c.provider === 'vk' && React.createElement("button", { className: "btn ghost", onClick: () => this.vkCallback(c.id) }, "\u0421\u0435\u043A\u0440\u0435\u0442 Callback"),
                                    React.createElement("button", { className: "btn ghost", onClick: () => this.disconnect(c.id) }, "\u041E\u0442\u043A\u043B\u044E\u0447\u0438\u0442\u044C")))))),
                    owner && React.createElement("div", { className: "onboarding-connect-actions" },
                        React.createElement("button", { className: "btn secondary wide", disabled: demo || !ready || s.loading, onClick: () => type === 'whatsapp' ? this.setState({ modal: 'whatsapp', connectToken: '', connectPhone: '', connectWaba: '' }) :
                                ['telegram', 'vk', 'max'].includes(type) ? this.setState({ modal: 'bot', botProvider: type, connectToken: '', botGroupId: '', botConfirmation: '' }) : this.oauth(type) },
                            demo ? 'Только в рабочей компании' : !ready ? 'Администратор должен настроить API' : cs.some((c) => c.mode === 'live' && c.status !== 'disconnected') ? 'Добавить ещё аккаунт' : 'Подключить ' + providerName(type),
                            " ",
                            React.createElement(Icon, { name: "arrow", size: 14 })),
                        type === 'whatsapp' && React.createElement("button", { className: "btn ghost wide", onClick: s.metaSession ? this.launchMetaWhatsApp : this.prepareMetaWhatsApp, disabled: demo || !guide?.meta_embedded_signup_ready || s.loading }, s.metaSession ? 'Продолжить в Meta' : 'Подготовить Meta')),
                    instructions && React.createElement("details", { className: "onboarding-instructions" },
                        React.createElement("summary", null, "\u0427\u0442\u043E \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u0434\u043B\u044F \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F?"),
                        React.createElement("ol", null, instructions.steps.map((step, i) => React.createElement("li", { key: i }, step)))));
            })),
            React.createElement("div", { className: "onboarding-disclaimer" },
                React.createElement(Icon, { name: "shield", size: 17 }),
                " \u0412 OSMANX \u043D\u0435\u043B\u044C\u0437\u044F \u0447\u0438\u0442\u0430\u0442\u044C \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0438 \u043B\u0438\u0447\u043D\u044B\u0445 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u043E\u0432 \u0447\u0435\u0440\u0435\u0437 \u0431\u043E\u0442. \u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043D\u044B \u0442\u043E\u043B\u044C\u043A\u043E \u0432\u043B\u0430\u0434\u0435\u043B\u044C\u0446\u0443 \u043E\u0440\u0433\u0430\u043D\u0438\u0437\u0430\u0446\u0438\u0438 \u0447\u0435\u0440\u0435\u0437 \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0435 API. \u0423\u0441\u043F\u0435\u0448\u043D\u0430\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0430 \u0442\u043E\u043A\u0435\u043D\u0430 \u043D\u0435 \u044F\u0432\u043B\u044F\u0435\u0442\u0441\u044F \u0434\u043E\u043A\u0430\u0437\u0430\u0442\u0435\u043B\u044C\u0441\u0442\u0432\u043E\u043C \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0438 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439."));
    }
    renderTeam() { const s = this.state; return React.createElement("div", { className: "page-content" },
        React.createElement("div", { className: "section-head" },
            React.createElement("div", null,
                React.createElement("div", { className: "eyebrow" }, "\u041A\u041E\u041C\u0410\u041D\u0414\u0410 / \u041F\u0420\u0410\u0412\u0410 \u0414\u041E\u0421\u0422\u0423\u041F\u0410"),
                React.createElement("h1", null, "\u041A\u043E\u043C\u0430\u043D\u0434\u0430"),
                React.createElement("p", null, "\u041D\u0430\u0437\u043D\u0430\u0447\u0435\u043D\u0438\u0435 \u0434\u0438\u0430\u043B\u043E\u0433\u043E\u0432, \u0440\u043E\u043B\u0438 \u0438 \u0440\u0430\u0437\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u0435 \u0434\u043E\u0441\u0442\u0443\u043F\u0430 \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u043E\u0432.")),
            React.createElement("button", { className: "btn primary", onClick: () => this.setState({ modal: 'invite', inviteToken: '' }) },
                React.createElement(Icon, { name: "plus", size: 16 }),
                " \u041F\u0440\u0438\u0433\u043B\u0430\u0441\u0438\u0442\u044C")),
        React.createElement("div", { className: "table-card" },
            React.createElement("div", { className: "table-heading" },
                React.createElement("h3", null, "\u0421\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u0438"),
                React.createElement("span", null,
                    s.team.length,
                    " \u0443\u0447\u0430\u0441\u0442\u043D\u0438\u043A\u043E\u0432")),
            s.team.map((m) => React.createElement("div", { className: "member-row", key: m.id },
                React.createElement(Avatar, { name: m.name, size: 39 }),
                React.createElement("div", null,
                    React.createElement("strong", null, m.name),
                    React.createElement("small", null, m.email)),
                React.createElement("button", { className: 'availability ' + (m.available ? 'on' : 'off'), onClick: () => this.changeAvailability(m.id, !m.available), disabled: !['owner', 'admin', 'lead'].includes(s.me.role) && m.id !== s.me.user.id }, m.available ? 'На связи' : 'Недоступен'),
                React.createElement("span", { className: "pill neutral" }, m.role === 'owner' ? 'Владелец' : m.role === 'admin' ? 'Администратор' : m.role === 'lead' ? 'Руководитель' : m.role === 'manager' ? 'Менеджер' : 'Оператор')))),
        React.createElement("div", { className: "analytics-disclaimer" },
            React.createElement(Icon, { name: "shield", size: 17 }),
            " \u0414\u043E\u0441\u0442\u0443\u043F \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440\u043E\u0432 \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D \u043D\u0430\u0437\u043D\u0430\u0447\u0435\u043D\u043D\u044B\u043C\u0438 \u0434\u0438\u0430\u043B\u043E\u0433\u0430\u043C\u0438. \u0420\u0443\u043A\u043E\u0432\u043E\u0434\u0438\u0442\u0435\u043B\u044C, \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440 \u0438 \u0432\u043B\u0430\u0434\u0435\u043B\u0435\u0446 \u0438\u043C\u0435\u044E\u0442 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043D\u043D\u044B\u0439 \u043E\u0431\u0437\u043E\u0440.")); }
    renderSettings() {
        const me = this.state.me, p = this.state.plans, s = this.state;
        return React.createElement("div", { className: "page-content" },
            React.createElement("div", { className: "section-head" },
                React.createElement("div", null,
                    React.createElement("div", { className: "eyebrow" }, "\u0420\u0410\u0411\u041E\u0427\u0410\u042F \u041E\u0411\u041B\u0410\u0421\u0422\u042C / \u041F\u0410\u0420\u0410\u041C\u0415\u0422\u0420\u042B"),
                    React.createElement("h1", null, "\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438"),
                    React.createElement("p", null, "\u041E\u0440\u0433\u0430\u043D\u0438\u0437\u0430\u0446\u0438\u044F, \u0431\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E\u0441\u0442\u044C, \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u044B\u0435 \u0444\u0443\u043D\u043A\u0446\u0438\u0438 \u0438 \u043F\u043E\u0434\u043F\u0438\u0441\u043A\u0430."))),
            React.createElement("div", { className: "settings-panel" },
                React.createElement("div", { className: "detail-label" }, "\u041E\u0420\u0413\u0410\u041D\u0418\u0417\u0410\u0426\u0418\u042F"),
                React.createElement("h2", null, me.organization.name),
                React.createElement("p", null,
                    "\u0422\u0435\u043A\u0443\u0449\u0438\u0439 \u0442\u0430\u0440\u0438\u0444: ",
                    React.createElement("strong", null, me.organization.plan.toUpperCase()),
                    " \u00B7 ",
                    me.organization.is_demo ? 'Демонстрационная организация' : 'Рабочая организация'),
                React.createElement("button", { className: "btn secondary", onClick: this.toggleTheme },
                    React.createElement(Icon, { name: this.state.light ? 'moon' : 'sun' }),
                    " \u041F\u0435\u0440\u0435\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u0442\u0435\u043C\u0443")),
            !me.organization.is_demo && React.createElement(React.Fragment, null,
                React.createElement("h3", { className: "settings-subtitle" }, "\u0412\u0430\u0448\u0438 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438"),
                React.createElement("div", { className: "settings-panel" },
                    React.createElement("p", null, "\u041A\u0430\u0436\u0434\u0430\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F \u0432\u0438\u0434\u0438\u0442 \u0442\u043E\u043B\u044C\u043A\u043E \u0441\u0432\u043E\u0438 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F, \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u043E\u0432 \u0438 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D\u043D\u044B\u0435 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u044B."),
                    me.organizations.map((org) => React.createElement("div", { className: "onboarding-page-row", key: org.id },
                        React.createElement("div", null,
                            React.createElement("strong", null, org.name),
                            React.createElement("small", null, org.role === 'owner' ? 'Владелец' : org.role === 'admin' ? 'Администратор' : 'Сотрудник')),
                        React.createElement("button", { className: "btn secondary", disabled: s.loading || org.id === me.organization.id, onClick: () => this.switchCompany(org.id) }, org.id === me.organization.id ? 'Текущая' : 'Переключиться'))),
                    React.createElement("div", { className: "onboarding-neworg" },
                        React.createElement("label", null,
                            "\u041D\u043E\u0432\u0430\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044F",
                            React.createElement("input", { placeholder: "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438", value: s.newOrganization, maxLength: 120, onChange: (e) => this.setState({ newOrganization: e.target.value }) })),
                        React.createElement("button", { className: "btn primary", disabled: s.loading || s.newOrganization.trim().length < 2, onClick: this.createCompany }, "\u0421\u043E\u0437\u0434\u0430\u0442\u044C \u043E\u0442\u0434\u0435\u043B\u044C\u043D\u0443\u044E \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u044E")))),
            React.createElement("h3", { className: "settings-subtitle" }, "\u0411\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E\u0441\u0442\u044C \u0432\u0445\u043E\u0434\u0430"),
            React.createElement("div", { className: "settings-panel security-session-panel" },
                React.createElement("div", { className: "session-info" },
                    React.createElement(Icon, { name: "shield", size: 21 }),
                    React.createElement("div", null,
                        React.createElement("strong", null, "\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430 \u0438 \u0441\u0435\u0430\u043D\u0441\u044B"),
                        React.createElement("p", null, "\u041C\u043E\u0436\u043D\u043E \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C \u0432\u0445\u043E\u0434 \u043D\u0430 \u0434\u0440\u0443\u0433\u0438\u0445 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430\u0445, \u0435\u0441\u043B\u0438 \u043A\u0442\u043E-\u0442\u043E \u043F\u043E\u043B\u0443\u0447\u0438\u043B \u0434\u043E\u0441\u0442\u0443\u043F \u043A \u0432\u0430\u0448\u0435\u043C\u0443 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0443. \u0421\u0435\u0430\u043D\u0441\u044B \u0432\u0441\u0435\u0445 \u0432\u0430\u0448\u0438\u0445 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0439 \u0437\u0430\u0449\u0438\u0449\u0435\u043D\u044B \u043E\u0434\u043D\u043E\u0439 \u0443\u0447\u0451\u0442\u043D\u043E\u0439 \u0437\u0430\u043F\u0438\u0441\u044C\u044E."))),
                s.sessions && React.createElement("div", { className: "session-status", "aria-live": "polite" },
                    "\u0410\u043A\u0442\u0438\u0432\u043D\u044B\u0445 \u0441\u0435\u0430\u043D\u0441\u043E\u0432: ",
                    React.createElement("strong", null, s.sessions.count),
                    ". \u0422\u0435\u043A\u0443\u0449\u0438\u0439 \u0441\u0435\u0430\u043D\u0441 \u043E\u0431\u043E\u0437\u043D\u0430\u0447\u0435\u043D \u043A\u0430\u043A \u0430\u043A\u0442\u0438\u0432\u043D\u044B\u0439."),
                React.createElement("div", { className: "session-actions" },
                    React.createElement("button", { className: "btn secondary", onClick: this.loadSessions, disabled: s.loading }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0441\u0435\u0430\u043D\u0441\u044B"),
                    React.createElement("button", { className: "btn secondary", onClick: this.revokeOtherSessions, disabled: s.loading }, "\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C \u0434\u0440\u0443\u0433\u0438\u0435 \u0441\u0435\u0430\u043D\u0441\u044B"),
                    React.createElement("button", { className: "btn secondary", onClick: this.revokeAllSessions, disabled: s.loading }, "\u0412\u044B\u0439\u0442\u0438 \u043D\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430\u0445"))),
            React.createElement("h3", { className: "settings-subtitle" }, "\u0422\u0430\u0440\u0438\u0444\u043D\u044B\u0435 \u0432\u043E\u0437\u043C\u043E\u0436\u043D\u043E\u0441\u0442\u0438"),
            React.createElement("div", { className: "plan-grid" }, p?.plans.map((plan) => React.createElement("div", { key: plan.id, className: 'plan-card ' + (plan.id === p.current ? 'selected' : '') },
                React.createElement("div", { className: "plan-title" }, plan.id.toUpperCase()),
                React.createElement("h3", null,
                    plan.employees === 99999 ? 'Без лимита' : plan.employees,
                    " ",
                    React.createElement("small", null, "\u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u043E\u0432")),
                React.createElement("p", null,
                    plan.channels === 99999 ? 'Без лимита' : plan.channels,
                    " \u043A\u0430\u043D\u0430\u043B\u043E\u0432"),
                React.createElement("p", null, plan.analytics ? 'Аналитика включена' : 'Базовый Inbox'),
                React.createElement("p", null, plan.automation ? 'Движок правил' : 'Без автоматизации'),
                React.createElement("div", { className: "plan-badge" }, plan.id === p.current ? 'Текущий тариф' : 'Доступен по запросу')))),
            React.createElement("div", { className: "analytics-disclaimer" }, "\u041F\u043E\u0434\u043F\u0438\u0441\u043A\u0438 \u043F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u043B\u0435\u043D\u044B \u043D\u0430 \u0443\u0440\u043E\u0432\u043D\u0435 \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u0439, \u043D\u043E \u043F\u043B\u0430\u0442\u0435\u0436\u0438 \u043D\u0435 \u043F\u0440\u0438\u043D\u0438\u043C\u0430\u044E\u0442\u0441\u044F: \u043F\u043B\u0430\u0442\u0451\u0436\u043D\u044B\u0439 \u043F\u0440\u043E\u0432\u0430\u0439\u0434\u0435\u0440 \u0435\u0449\u0451 \u043D\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0451\u043D."),
            React.createElement("h3", { className: "settings-subtitle" }, "\u0428\u0430\u0431\u043B\u043E\u043D\u044B \u0431\u044B\u0441\u0442\u0440\u044B\u0445 \u043E\u0442\u0432\u0435\u0442\u043E\u0432"),
            React.createElement("div", { className: "settings-panel" },
                React.createElement("div", { className: "template-list" }, this.state.templates.map((t) => React.createElement("div", { className: "template-entry", key: t.id },
                    React.createElement("div", null,
                        React.createElement("b", null, t.title),
                        React.createElement("p", null, t.body)),
                    ['owner', 'admin', 'lead'].includes(me.role) && React.createElement("button", { className: "icon-btn", title: "\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0448\u0430\u0431\u043B\u043E\u043D", onClick: () => this.deleteTemplate(t.id) },
                        React.createElement(Icon, { name: "close", size: 16 }))))),
                ['owner', 'admin', 'lead'].includes(me.role) && React.createElement("div", { className: "template-form" },
                    React.createElement("input", { "aria-label": "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043D\u043E\u0432\u043E\u0433\u043E \u0448\u0430\u0431\u043B\u043E\u043D\u0430", placeholder: "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0448\u0430\u0431\u043B\u043E\u043D\u0430", value: this.state.templateName, onChange: (e) => this.setState({ templateName: e.target.value }) }),
                    React.createElement("textarea", { "aria-label": "\u0422\u0435\u043A\u0441\u0442 \u043D\u043E\u0432\u043E\u0433\u043E \u0448\u0430\u0431\u043B\u043E\u043D\u0430", placeholder: "\u0422\u0435\u043A\u0441\u0442 \u0431\u044B\u0441\u0442\u0440\u043E\u0433\u043E \u043E\u0442\u0432\u0435\u0442\u0430...", rows: 2, value: this.state.templateBody, onChange: (e) => this.setState({ templateBody: e.target.value }) }),
                    React.createElement("button", { className: "btn secondary", onClick: this.saveTemplate, disabled: !this.state.templateName.trim() || !this.state.templateBody.trim() }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0448\u0430\u0431\u043B\u043E\u043D"))),
            this.state.localization && React.createElement(React.Fragment, null,
                React.createElement("h3", { className: "settings-subtitle" }, "\u0420\u0435\u0433\u0438\u043E\u043D \u0438 \u043B\u043E\u043A\u0430\u043B\u0438\u0437\u0430\u0446\u0438\u044F"),
                React.createElement("div", { className: "settings-panel privacy-panel" },
                    React.createElement("label", null,
                        "\u0412\u0430\u043B\u044E\u0442\u0430 \u0441\u0434\u0435\u043B\u043E\u043A",
                        React.createElement("select", { "aria-label": "\u0412\u0430\u043B\u044E\u0442\u0430 \u0441\u0434\u0435\u043B\u043E\u043A", value: this.state.localization.currency, onChange: (e) => this.setState({ localization: { ...this.state.localization, currency: e.target.value } }) }, this.state.localization.currencies.map((c) => React.createElement("option", { key: c, value: c }, c)))),
                    React.createElement("label", null,
                        "\u0427\u0430\u0441\u043E\u0432\u043E\u0439 \u043F\u043E\u044F\u0441 IANA",
                        React.createElement("input", { "aria-label": "\u0427\u0430\u0441\u043E\u0432\u043E\u0439 \u043F\u043E\u044F\u0441 IANA", value: this.state.localization.timezone, placeholder: "Europe/Moscow", onChange: (e) => this.setState({ localization: { ...this.state.localization, timezone: e.target.value } }) })),
                    React.createElement("button", { className: "btn primary", onClick: this.saveLocalization }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u0440\u0435\u0433\u0438\u043E\u043D"),
                    React.createElement("p", { className: "site-localization-note" }, "\u0412\u0430\u043B\u044E\u0442\u0443 \u043D\u0435\u043B\u044C\u0437\u044F \u043C\u0435\u043D\u044F\u0442\u044C, \u0435\u0441\u043B\u0438 \u0443\u0436\u0435 \u0435\u0441\u0442\u044C \u0441\u0434\u0435\u043B\u043A\u0438 \u0441 \u0441\u0443\u043C\u043C\u0430\u043C\u0438: \u044D\u0442\u043E \u0437\u0430\u0449\u0438\u0449\u0430\u0435\u0442 \u0440\u0430\u0441\u0447\u0451\u0442\u044B. \u0414\u0430\u0442\u044B \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0438 \u0440\u0430\u0441\u0441\u0447\u0438\u0442\u044B\u0432\u0430\u044E\u0442\u0441\u044F \u0432 \u0432\u044B\u0431\u0440\u0430\u043D\u043D\u043E\u043C \u0447\u0430\u0441\u043E\u0432\u043E\u043C \u043F\u043E\u044F\u0441\u0435."))),
            this.state.privacy && React.createElement(React.Fragment, null,
                React.createElement("h3", { className: "settings-subtitle" }, "\u041A\u043E\u043D\u0444\u0438\u0434\u0435\u043D\u0446\u0438\u0430\u043B\u044C\u043D\u043E\u0441\u0442\u044C \u0438 \u043E\u0431\u0441\u043B\u0443\u0436\u0438\u0432\u0430\u043D\u0438\u0435"),
                React.createElement("div", { className: "settings-panel privacy-panel" },
                    React.createElement("label", null,
                        "\u0425\u0440\u0430\u043D\u0435\u043D\u0438\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439 ",
                        React.createElement("select", { value: this.state.privacy.retention_days, onChange: (e) => this.setState({ privacy: { ...this.state.privacy, retention_days: Number(e.target.value) } }) }, [30, 90, 120, 180, 365, 730, 1095].map(n => React.createElement("option", { key: n, value: n },
                            n,
                            " \u0434\u043D\u0435\u0439")))),
                    React.createElement("label", null,
                        "\u041F\u0440\u0435\u0434\u0443\u043F\u0440\u0435\u0436\u0434\u0435\u043D\u0438\u0435, \u0435\u0441\u043B\u0438 \u043D\u0435\u0442 \u043E\u0442\u0432\u0435\u0442\u0430 ",
                        React.createElement("select", { value: this.state.privacy.sla_minutes, onChange: (e) => this.setState({ privacy: { ...this.state.privacy, sla_minutes: Number(e.target.value) } }) }, [1, 3, 5, 7, 10, 15, 30, 60].map(n => React.createElement("option", { key: n, value: n },
                            n,
                            " \u043C\u0438\u043D\u0443\u0442")))),
                    React.createElement("button", { className: "btn primary", onClick: this.savePrivacy }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438"),
                    React.createElement("button", { className: "btn secondary", onClick: this.exportWorkspace },
                        React.createElement(Icon, { name: "note", size: 15 }),
                        " \u042D\u043A\u0441\u043F\u043E\u0440\u0442\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0434\u0430\u043D\u043D\u044B\u0435 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438"))));
    }
    renderModal() {
        const s = this.state;
        return React.createElement("div", { className: "modal-cover", onClick: () => this.setState({ modal: '' }) },
            React.createElement("div", { className: "modal", role: "dialog", "aria-modal": "true", onClick: (e) => e.stopPropagation() },
                React.createElement("div", { className: "modal-header" },
                    React.createElement("div", null,
                        React.createElement("div", { className: "eyebrow" }, "OSMANX / \u041D\u0410\u0421\u0422\u0420\u041E\u0419\u041A\u0410"),
                        React.createElement("h2", null, s.modal === 'view' ? 'Сохранить представление' : s.modal === 'rule' ? 'Новое правило' : s.modal === 'whatsapp' ? 'WhatsApp Cloud API' : s.modal === 'wa-template' ? 'Одобренный шаблон WhatsApp' : s.modal === 'rotate' ? 'Замена токена' : s.modal === 'register-phone' ? 'Регистрация номера WhatsApp' : s.modal === 'bot' ? 'Подключить ' + providerName(s.botProvider) : s.modal === 'reconcile' ? 'Проверка отправки' : s.modal === 'retry-outbox' ? 'Повтор после отказа площадки' : s.modal === 'retry-inbound' ? 'Восстановление входящего события' : s.modal === 'inbound-batch' ? 'Пакетное восстановление входящих' : s.modal === 'inbound-dismiss' ? 'Необратимое закрытие входящего' : s.modal === 'inbound-pause' ? 'Управление входящими при инциденте' : s.modal === 'inbound-repair' ? 'Восстановление просроченных захватов' : 'Приглашение сотрудника')),
                    React.createElement("button", { className: "icon-btn", "aria-label": "\u0417\u0430\u043A\u0440\u044B\u0442\u044C", onClick: () => this.setState({ modal: '' }) },
                        React.createElement(Icon, { name: "close" }))),
                s.modal === 'view' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u0435 \u0442\u0435\u043A\u0443\u0449\u0438\u0435 \u0444\u0438\u043B\u044C\u0442\u0440\u044B \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043E\u043A, \u0447\u0442\u043E\u0431\u044B \u0432\u043E\u0437\u0432\u0440\u0430\u0449\u0430\u0442\u044C\u0441\u044F \u043A \u043D\u0438\u043C \u043E\u0434\u043D\u0438\u043C \u043D\u0430\u0436\u0430\u0442\u0438\u0435\u043C."),
                    React.createElement("label", null,
                        "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043F\u043E\u0434\u0431\u043E\u0440\u043A\u0438",
                        React.createElement("input", { "aria-label": "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043F\u043E\u0434\u0431\u043E\u0440\u043A\u0438", value: s.viewName, onChange: (e) => this.setState({ viewName: e.target.value }), placeholder: "\u041D\u0430\u043F\u0440\u0438\u043C\u0435\u0440: \u0421\u0440\u043E\u0447\u043D\u044B\u0435 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F", maxLength: 64 })),
                    ['owner', 'admin', 'lead'].includes(s.me.role) && React.createElement("label", { className: "view-share" },
                        React.createElement("input", { type: "checkbox", checked: s.viewShared, onChange: (e) => this.setState({ viewShared: e.target.checked }) }),
                        " \u0414\u043E\u0441\u0442\u0443\u043F\u043D\u043E \u0432\u0441\u0435\u0439 \u043A\u043E\u043C\u0430\u043D\u0434\u0435"),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || s.viewName.trim().length < 2, onClick: this.createSavedView }, "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C \u043F\u043E\u0434\u0431\u043E\u0440\u043A\u0443")),
                s.modal === 'rule' && React.createElement("div", { className: "modal-form" },
                    React.createElement("label", null,
                        "\u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043F\u0440\u0430\u0432\u0438\u043B\u0430",
                        React.createElement("input", { value: s.ruleName, onChange: (e) => this.setState({ ruleName: e.target.value }), placeholder: "\u041D\u0430\u043F\u0440\u0438\u043C\u0435\u0440: \u0421\u0440\u043E\u0447\u043D\u044B\u0435 \u0437\u0430\u043F\u0440\u043E\u0441\u044B" })),
                    React.createElement("div", { className: "modal-flow" },
                        React.createElement("div", { className: "flow-input" },
                            React.createElement("small", null, "\u0421\u041E\u0411\u042B\u0422\u0418\u0415"),
                            React.createElement("strong", null, "\u041D\u043E\u0432\u043E\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435")),
                        React.createElement("div", { className: "flow-input" },
                            React.createElement("small", null, "\u0423\u0421\u041B\u041E\u0412\u0418\u0415"),
                            React.createElement("select", { value: s.ruleCondition, onChange: (e) => this.setState({ ruleCondition: e.target.value }) },
                                React.createElement("option", { value: "contains" }, "\u0421\u043E\u0434\u0435\u0440\u0436\u0438\u0442 \u0441\u043B\u043E\u0432\u0430"),
                                React.createElement("option", { value: "always" }, "\u041B\u044E\u0431\u043E\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435"))),
                        React.createElement("div", { className: "flow-input" },
                            React.createElement("small", null, "\u0414\u0415\u0419\u0421\u0422\u0412\u0418\u0415"),
                            React.createElement("select", { value: s.ruleAction, onChange: (e) => this.setState({ ruleAction: e.target.value }) },
                                React.createElement("option", { value: "tag" }, "\u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0442\u0435\u0433"),
                                React.createElement("option", { value: "priority" }, "\u0417\u0430\u043A\u0440\u0435\u043F\u0438\u0442\u044C"),
                                React.createElement("option", { value: "status" }, "\u0418\u0437\u043C\u0435\u043D\u0438\u0442\u044C \u0441\u0442\u0430\u0442\u0443\u0441"),
                                React.createElement("option", { value: "assign_least_busy" }, "\u041D\u0430\u0437\u043D\u0430\u0447\u0438\u0442\u044C \u0441\u0432\u043E\u0431\u043E\u0434\u043D\u043E\u0433\u043E \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440\u0430")))),
                    s.ruleCondition === 'contains' && React.createElement("label", null,
                        "\u041A\u043B\u044E\u0447\u0435\u0432\u043E\u0435 \u0441\u043B\u043E\u0432\u043E \u0438\u043B\u0438 \u0444\u0440\u0430\u0437\u0430",
                        React.createElement("input", { value: s.ruleTerm, onChange: (e) => this.setState({ ruleTerm: e.target.value }), placeholder: "\u0441\u0440\u043E\u0447\u043D\u043E" })),
                    !['priority', 'assign_least_busy'].includes(s.ruleAction) && React.createElement("label", null,
                        s.ruleAction === 'tag' ? 'Название тега' : 'Код статуса',
                        React.createElement("input", { value: s.ruleActionValue, onChange: (e) => this.setState({ ruleActionValue: e.target.value }), placeholder: "VIP" })),
                    React.createElement("button", { className: "btn primary wide", onClick: this.createRule, disabled: s.loading }, "\u0421\u043E\u0437\u0434\u0430\u0442\u044C \u0438 \u0432\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u043F\u0440\u0430\u0432\u0438\u043B\u043E")),
                s.modal === 'wa-template' && React.createElement("div", { className: "modal-form wa-template-modal" },
                    React.createElement("p", { className: "modal-help" }, "\u0428\u0430\u0431\u043B\u043E\u043D\u044B \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u044E\u0442\u0441\u044F \u0438\u0437 \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u043E\u0433\u043E \u043A\u0430\u0442\u0430\u043B\u043E\u0433\u0430 Meta \u0438 \u043D\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u044E\u0442\u0441\u044F \u0431\u0435\u0437 \u0437\u0430\u0444\u0438\u043A\u0441\u0438\u0440\u043E\u0432\u0430\u043D\u043D\u043E\u0433\u043E \u0441\u043E\u0433\u043B\u0430\u0441\u0438\u044F \u043A\u043B\u0438\u0435\u043D\u0442\u0430. \u041F\u043E\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442\u0441\u044F \u0442\u043E\u043B\u044C\u043A\u043E \u043E\u0431\u044B\u0447\u043D\u044B\u0439 \u0442\u0435\u043A\u0441\u0442\u043E\u0432\u044B\u0439 \u0448\u0430\u0431\u043B\u043E\u043D \u0431\u0435\u0437 \u043A\u043D\u043E\u043F\u043E\u043A \u0438 \u0432\u043B\u043E\u0436\u0435\u043D\u0438\u0439."),
                    s.waLoading ? React.createElement("p", { role: "status" }, "\u041F\u0440\u043E\u0432\u0435\u0440\u044F\u0435\u043C \u0448\u0430\u0431\u043B\u043E\u043D\u044B \u0432 Meta...") : React.createElement(React.Fragment, null,
                        !s.waTemplates.length ? React.createElement("p", { className: "wa-empty" }, "\u041E\u0434\u043E\u0431\u0440\u0435\u043D\u043D\u044B\u0445 \u043F\u0440\u043E\u0441\u0442\u044B\u0445 \u0442\u0435\u043A\u0441\u0442\u043E\u0432\u044B\u0445 \u0448\u0430\u0431\u043B\u043E\u043D\u043E\u0432 \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u043E. \u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 WABA ID, \u0434\u043E\u0441\u0442\u0443\u043F \u043A \u043A\u0430\u0442\u0430\u043B\u043E\u0433\u0443 \u0438 \u043E\u0434\u043E\u0431\u0440\u0435\u043D\u0438\u0435 \u0448\u0430\u0431\u043B\u043E\u043D\u0430 \u0432 WhatsApp Manager.") : React.createElement(React.Fragment, null,
                            React.createElement("label", null,
                                "\u041E\u0434\u043E\u0431\u0440\u0435\u043D\u043D\u044B\u0439 \u0448\u0430\u0431\u043B\u043E\u043D",
                                React.createElement("select", { "aria-label": "\u041E\u0434\u043E\u0431\u0440\u0435\u043D\u043D\u044B\u0439 \u0448\u0430\u0431\u043B\u043E\u043D WhatsApp", value: s.waSelected, onChange: (e) => {
                                        const selection = s.waTemplates.find((t) => t.name + '|' + t.language === e.target.value);
                                        this.setState({ waSelected: e.target.value, waParams: Array(selection?.param_count || 0).fill('') });
                                    } }, s.waTemplates.map((t) => React.createElement("option", { key: t.name + '|' + t.language, value: t.name + '|' + t.language },
                                    t.name,
                                    " \u00B7 ",
                                    t.language)))),
                            (() => {
                                const chosen = s.waTemplates.find((t) => t.name + '|' + t.language === s.waSelected);
                                if (!chosen)
                                    return null;
                                const preview = String(chosen.body || '').replace(/\{\{([1-9][0-9]*)\}\}/g, (_, n) => s.waParams[Number(n) - 1] || '…');
                                return React.createElement(React.Fragment, null,
                                    React.createElement("div", { className: "wa-preview" },
                                        React.createElement("small", null, "\u041F\u0420\u0415\u0414\u041F\u0420\u041E\u0421\u041C\u041E\u0422\u0420"),
                                        React.createElement("p", null, preview)),
                                    Array.from({ length: chosen.param_count }, (_, i) => React.createElement("label", { key: i },
                                        "\u041F\u0430\u0440\u0430\u043C\u0435\u0442\u0440 ",
                                        i + 1,
                                        React.createElement("input", { value: s.waParams[i] || '', maxLength: 200, placeholder: 'Значение ' + (i + 1), onChange: (e) => this.setState({ waParams: s.waParams.map((value, j) => j === i ? e.target.value : value) }) }))));
                            })()),
                        !s.waConsent ? React.createElement("div", { className: "wa-consent" },
                            React.createElement("strong", null, "\u041D\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u043E \u0441\u043E\u0433\u043B\u0430\u0441\u0438\u0435 \u043A\u043B\u0438\u0435\u043D\u0442\u0430"),
                            React.createElement("p", null, "\u0421\u043E\u0433\u043B\u0430\u0441\u0438\u0435 \u0434\u043E\u043B\u0436\u043D\u043E \u0431\u044B\u0442\u044C \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u044C\u043D\u043E \u043F\u043E\u043B\u0443\u0447\u0435\u043D\u043E \u0432\u0430\u043C\u0438. OSMANX \u0442\u043E\u043B\u044C\u043A\u043E \u0444\u0438\u043A\u0441\u0438\u0440\u0443\u0435\u0442 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435 \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u0430."),
                            ['owner', 'admin', 'lead'].includes(s.me.role) ? React.createElement(React.Fragment, null,
                                React.createElement("label", null,
                                    "\u0418\u0441\u0442\u043E\u0447\u043D\u0438\u043A \u0438 \u0434\u0430\u0442\u0430 \u0441\u043E\u0433\u043B\u0430\u0441\u0438\u044F",
                                    React.createElement("input", { value: s.waConsentSource, maxLength: 240, placeholder: "\u041D\u0430\u043F\u0440\u0438\u043C\u0435\u0440: \u0444\u043E\u0440\u043C\u0430 \u0437\u0430\u043F\u0438\u0441\u0438 01.11.2026", onChange: (e) => this.setState({ waConsentSource: e.target.value }) })),
                                React.createElement("label", { className: "wa-check" },
                                    React.createElement("input", { type: "checkbox", checked: s.waConsentCheckbox, onChange: (e) => this.setState({ waConsentCheckbox: e.target.checked }) }),
                                    "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044E, \u0447\u0442\u043E \u043A\u043B\u0438\u0435\u043D\u0442 \u0434\u0430\u043B \u0441\u043E\u0433\u043B\u0430\u0441\u0438\u0435 \u043D\u0430 \u0442\u0430\u043A\u0438\u0435 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F."),
                                React.createElement("button", { className: "btn secondary", disabled: !s.waConsentCheckbox || s.waConsentSource.trim().length < 8 || s.loading, onClick: this.recordWaConsent }, "\u0417\u0430\u0444\u0438\u043A\u0441\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0441\u043E\u0433\u043B\u0430\u0441\u0438\u0435")) : React.createElement("p", null, "\u041F\u043E\u043F\u0440\u043E\u0441\u0438\u0442\u0435 \u0432\u043B\u0430\u0434\u0435\u043B\u044C\u0446\u0430, \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440\u0430 \u0438\u043B\u0438 \u0440\u0443\u043A\u043E\u0432\u043E\u0434\u0438\u0442\u0435\u043B\u044F \u0437\u0430\u0444\u0438\u043A\u0441\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0441\u043E\u0433\u043B\u0430\u0441\u0438\u0435 \u043A\u043B\u0438\u0435\u043D\u0442\u0430.")) : React.createElement("div", { className: "wa-consent-valid" },
                            React.createElement(Icon, { name: "check", size: 16 }),
                            " \u0421\u043E\u0433\u043B\u0430\u0441\u0438\u0435 \u0437\u0430\u0444\u0438\u043A\u0441\u0438\u0440\u043E\u0432\u0430\u043D\u043E \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u043E\u043C. ",
                            ['owner', 'admin', 'lead'].includes(s.me.role) && React.createElement("button", { className: "btn ghost", onClick: this.revokeWaConsent }, "\u041E\u0442\u043E\u0437\u0432\u0430\u0442\u044C")),
                        React.createElement("button", { className: "btn primary wide wa-submit", onClick: this.sendWaTemplate, disabled: !s.waConsent || !s.waTemplates.length || s.waLoading || s.loading ||
                                s.waParams.some((x) => !x.trim()) }, "\u041F\u043E\u0441\u0442\u0430\u0432\u0438\u0442\u044C \u0448\u0430\u0431\u043B\u043E\u043D \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u044C"),
                        React.createElement("p", { className: "modal-help" }, "Meta \u043C\u043E\u0436\u0435\u0442 \u043E\u0442\u043A\u043B\u043E\u043D\u0438\u0442\u044C \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0443 \u0438\u0437-\u0437\u0430 \u043F\u0440\u0430\u0432\u0438\u043B \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0438. \u0421\u0442\u0430\u0442\u0443\u0441 \u00AB\u043F\u0440\u0438\u043D\u044F\u0442\u043E API\u00BB \u043D\u0435 \u0440\u0430\u0432\u0435\u043D \u00AB\u0434\u043E\u0441\u0442\u0430\u0432\u043B\u0435\u043D\u043E\u00BB."))),
                s.modal === 'whatsapp' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0442\u043E\u043B\u044C\u043A\u043E \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u044C\u043D\u044B\u0439 \u0442\u043E\u043A\u0435\u043D Meta WhatsApp Cloud API \u0438 \u0418\u0434\u0435\u043D\u0442\u0438\u0444\u0438\u043A\u0430\u0442\u043E\u0440 \u043D\u043E\u043C\u0435\u0440\u0430 \u0442\u0435\u043B\u0435\u0444\u043E\u043D\u0430. \u0421\u0435\u0440\u0432\u0435\u0440 \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u0442 \u0438\u0445 \u0443 Meta \u043F\u0435\u0440\u0435\u0434 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u0435\u043C."),
                    React.createElement("label", null,
                        "\u0418\u0434\u0435\u043D\u0442\u0438\u0444\u0438\u043A\u0430\u0442\u043E\u0440 \u043D\u043E\u043C\u0435\u0440\u0430 \u0442\u0435\u043B\u0435\u0444\u043E\u043D\u0430",
                        React.createElement("input", { value: s.connectPhone, onChange: (e) => this.setState({ connectPhone: e.target.value }), placeholder: "123456789012345" })),
                    React.createElement("label", null,
                        "WABA ID (\u0434\u043B\u044F \u043F\u043E\u0434\u043F\u0438\u0441\u043A\u0438 \u043D\u0430 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0435)",
                        React.createElement("input", { value: s.connectWaba, onChange: (e) => this.setState({ connectWaba: e.target.value }), placeholder: "ID \u0431\u0438\u0437\u043D\u0435\u0441-\u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430 WhatsApp" })),
                    React.createElement("label", null,
                        "\u0422\u043E\u043A\u0435\u043D \u0434\u043E\u0441\u0442\u0443\u043F\u0430 Meta",
                        React.createElement("input", { type: "password", autoComplete: "off", value: s.connectToken, onChange: (e) => this.setState({ connectToken: e.target.value }), placeholder: "EAAG..." })),
                    React.createElement("button", { className: "btn primary wide", onClick: this.connectWhatsApp, disabled: !s.connectPhone || !s.connectToken || s.loading }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0438 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C")),
                s.modal === 'register-phone' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u0417\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0443\u0439\u0442\u0435 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u044B\u0439 \u0443 Meta \u043D\u043E\u043C\u0435\u0440 \u0441 \u0448\u0435\u0441\u0442\u0438\u0437\u043D\u0430\u0447\u043D\u044B\u043C PIN \u0434\u0432\u0443\u0445\u044D\u0442\u0430\u043F\u043D\u043E\u0439 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438. PIN \u043D\u0435 \u0441\u043E\u0445\u0440\u0430\u043D\u044F\u0435\u0442\u0441\u044F \u0432 OSMANX. \u041F\u043E\u0441\u043B\u0435 \u043E\u043F\u0435\u0440\u0430\u0446\u0438\u0438 \u043F\u043E\u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0439 \u0442\u0435\u0441\u0442."),
                    React.createElement("label", null,
                        "PIN \u0438\u0437 6 \u0446\u0438\u0444\u0440",
                        React.createElement("input", { type: "password", autoComplete: "one-time-code", inputMode: "numeric", maxLength: 6, value: s.registrationPin, onChange: (e) => this.setState({ registrationPin: e.target.value.replace(/[^0-9]/g, '') }), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022" })),
                    React.createElement("button", { className: "btn primary wide", disabled: s.registrationPin.length !== 6 || s.loading, onClick: this.registerWhatsAppPhone }, "\u0417\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0443 Meta")),
                s.modal === 'rotate' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u041D\u043E\u0432\u044B\u0439 \u0442\u043E\u043A\u0435\u043D \u0434\u043E\u043B\u0436\u0435\u043D \u043F\u0440\u0438\u043D\u0430\u0434\u043B\u0435\u0436\u0430\u0442\u044C \u0442\u043E\u043C\u0443 \u0436\u0435 \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0443. \u041F\u043E\u0441\u043B\u0435 \u0437\u0430\u043C\u0435\u043D\u044B \u0431\u043E\u0442\u0430\u043C \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u043F\u043E\u0432\u0442\u043E\u0440\u043D\u043E \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u043F\u043E\u0434\u043F\u0438\u0441\u043A\u0443 \u043D\u0430 \u0441\u043E\u0431\u044B\u0442\u0438\u044F."),
                    React.createElement("label", null,
                        "\u041D\u043E\u0432\u044B\u0439 \u0442\u043E\u043A\u0435\u043D",
                        React.createElement("input", { type: "password", autoComplete: "off", value: s.rotateToken, onChange: (e) => this.setState({ rotateToken: e.target.value }), placeholder: "\u041D\u043E\u0432\u044B\u0439 \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0439 \u0442\u043E\u043A\u0435\u043D" })),
                    React.createElement("button", { className: "btn primary wide", disabled: s.rotateToken.length < 10 || s.loading, onClick: this.rotateChannelToken }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0438 \u0437\u0430\u043C\u0435\u043D\u0438\u0442\u044C")),
                s.modal === 'bot' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" },
                        "\u041E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u043E\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 ",
                        providerName(s.botProvider),
                        ". \u0421\u043D\u0430\u0447\u0430\u043B\u0430 \u0431\u0443\u0434\u0435\u0442 \u043F\u0440\u043E\u0432\u0435\u0440\u0435\u043D \u0442\u043E\u043A\u0435\u043D; \u043F\u0440\u0438\u0451\u043C \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439 \u0437\u0430\u0440\u0430\u0431\u043E\u0442\u0430\u0435\u0442 \u043F\u043E\u0441\u043B\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u0437\u0430\u0449\u0438\u0449\u0451\u043D\u043D\u043E\u0433\u043E webhook \u043D\u0430 HTTPS."),
                    React.createElement("label", null,
                        "\u0422\u043E\u043A\u0435\u043D ",
                        s.botProvider === 'vk' ? 'сообщества' : 'бота',
                        React.createElement("input", { type: "password", autoComplete: "off", value: s.connectToken, onChange: (e) => this.setState({ connectToken: e.target.value }), placeholder: "\u0422\u043E\u043A\u0435\u043D \u043E\u0444\u0438\u0446\u0438\u0430\u043B\u044C\u043D\u043E\u0433\u043E API" })),
                    s.botProvider === 'vk' && React.createElement(React.Fragment, null,
                        React.createElement("label", null,
                            "ID \u0441\u043E\u043E\u0431\u0449\u0435\u0441\u0442\u0432\u0430",
                            React.createElement("input", { value: s.botGroupId, onChange: (e) => this.setState({ botGroupId: e.target.value }), placeholder: "123456789" })),
                        React.createElement("label", null,
                            "\u041A\u043E\u0434 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F Callback API",
                            React.createElement("input", { value: s.botConfirmation, onChange: (e) => this.setState({ botConfirmation: e.target.value }), placeholder: "\u0421\u0442\u0440\u043E\u043A\u0430 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u044F VK" }))),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || !s.connectToken.trim() || (s.botProvider === 'vk' && (!s.botGroupId || !s.botConfirmation)), onClick: this.connectBot }, "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C \u0442\u043E\u043A\u0435\u043D")),
                s.modal === 'reconcile' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u041F\u043E\u0441\u043B\u0435 \u0441\u0431\u043E\u044F \u0441\u0435\u0442\u0438 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u043C\u043E\u0433\u043B\u043E \u0434\u043E\u0439\u0442\u0438 \u0434\u043E \u0441\u0435\u0440\u0432\u0438\u0441\u0430. \u041F\u0435\u0440\u0435\u0434 \u043F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435\u043C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u0430 \u043F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 \u0435\u0433\u043E \u043D\u0435\u043F\u043E\u0441\u0440\u0435\u0434\u0441\u0442\u0432\u0435\u043D\u043D\u043E \u043D\u0430 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0435. \u041F\u043E\u0432\u0442\u043E\u0440\u043D\u0430\u044F \u043E\u0442\u043F\u0440\u0430\u0432\u043A\u0430 \u043D\u0435 \u0432\u044B\u043F\u043E\u043B\u043D\u044F\u0435\u0442\u0441\u044F."),
                    React.createElement("label", null,
                        "\u041F\u0440\u043E\u0432\u0435\u0440\u0435\u043D\u043D\u044B\u0439 \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442",
                        React.createElement("select", { value: s.reconcileStatus, onChange: (e) => this.setState({ reconcileStatus: e.target.value }) },
                            React.createElement("option", { value: "accepted" }, "\u0414\u043E\u0441\u0442\u0430\u0432\u043B\u0435\u043D\u043E \u0438\u043B\u0438 \u043F\u0440\u0438\u043D\u044F\u0442\u043E \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u043E\u0439"),
                            React.createElement("option", { value: "failed" }, "\u041D\u0435 \u0434\u043E\u0441\u0442\u0430\u0432\u043B\u0435\u043D\u043E"))),
                    React.createElement("label", null,
                        "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 (\u043E\u0431\u044F\u0437\u0430\u0442\u0435\u043B\u044C\u043D\u043E)",
                        React.createElement("textarea", { rows: 3, value: s.reconcileEvidence, placeholder: "\u0421\u0441\u044B\u043B\u043A\u0430 \u043D\u0430 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0443, \u0434\u0430\u0442\u0430 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 \u0438 \u0438\u043C\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u044F\u044E\u0449\u0435\u0433\u043E", onChange: (e) => this.setState({ reconcileEvidence: e.target.value }) })),
                    React.createElement("label", null,
                        "\u0418\u0434\u0435\u043D\u0442\u0438\u0444\u0438\u043A\u0430\u0442\u043E\u0440 \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u043D\u0430 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0435 (\u043F\u0440\u0438 \u043D\u0430\u043B\u0438\u0447\u0438\u0438)",
                        React.createElement("input", { value: s.reconcileExternalId, onChange: (e) => this.setState({ reconcileExternalId: e.target.value }) })),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || s.reconcileEvidence.trim().length < 8, onClick: this.reconcileDelivery }, "\u0417\u0430\u0444\u0438\u043A\u0441\u0438\u0440\u043E\u0432\u0430\u0442\u044C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442")),
                s.modal === 'retry-outbox' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u041F\u043B\u043E\u0449\u0430\u0434\u043A\u0430 \u043E\u0434\u043D\u043E\u0437\u043D\u0430\u0447\u043D\u043E \u043E\u0442\u043A\u043B\u043E\u043D\u0438\u043B\u0430 \u0437\u0430\u043F\u0440\u043E\u0441. \u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 \u0432 \u0438\u0441\u0445\u043E\u0434\u043D\u043E\u043C \u0441\u0435\u0440\u0432\u0438\u0441\u0435, \u0447\u0442\u043E \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435 \u043D\u0435 \u0431\u044B\u043B\u043E \u0434\u043E\u0441\u0442\u0430\u0432\u043B\u0435\u043D\u043E. \u041D\u0435 \u0438\u0441\u043F\u043E\u043B\u044C\u0437\u0443\u0439\u0442\u0435 \u044D\u0442\u0443 \u0444\u0443\u043D\u043A\u0446\u0438\u044E \u0434\u043B\u044F \u0442\u0430\u0439\u043C\u0430\u0443\u0442\u043E\u0432 \u0438 \u043D\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043D\u043E\u0433\u043E \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u0430."),
                    React.createElement("label", null,
                        "\u0427\u0442\u043E \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u043B\u0438 \u0438 \u0433\u0434\u0435 (\u043C\u0438\u043D\u0438\u043C\u0443\u043C 12 \u0441\u0438\u043C\u0432\u043E\u043B\u043E\u0432)",
                        React.createElement("textarea", { "aria-label": "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435 \u043E\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u044F \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0438", rows: 3, minLength: 12, maxLength: 500, value: s.outboxRetryEvidence, onChange: (e) => this.setState({ outboxRetryEvidence: e.target.value }), placeholder: "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u043B \u0434\u0438\u0430\u043B\u043E\u0433 \u043A\u043B\u0438\u0435\u043D\u0442\u0430 \u0432 \u0438\u0441\u0445\u043E\u0434\u043D\u043E\u0439 \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0435, \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F \u043D\u0435\u0442" })),
                    React.createElement("label", { className: "wa-check" },
                        React.createElement("input", { type: "checkbox", checked: s.outboxRetryVerified, onChange: (e) => this.setState({ outboxRetryVerified: e.target.checked }) }),
                        " \u042F \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u043B \u043E\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u0435 \u0434\u043E\u0441\u0442\u0430\u0432\u043A\u0438 \u0438 \u043F\u043E\u043D\u0438\u043C\u0430\u044E \u0440\u0438\u0441\u043A \u043F\u043E\u0432\u0442\u043E\u0440\u043D\u043E\u0433\u043E \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F."),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || !s.outboxRetryVerified || s.outboxRetryEvidence.trim().length < 12, onClick: this.retryVerified }, "\u041F\u043E\u0441\u0442\u0430\u0432\u0438\u0442\u044C \u043F\u043E\u0432\u0442\u043E\u0440 \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u044C")),
                s.modal === 'retry-inbound' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u0438 \u043F\u0440\u0438\u0447\u0438\u043D\u0443 \u043E\u0448\u0438\u0431\u043A\u0438 \u043F\u0435\u0440\u0435\u0434 \u043F\u043E\u0432\u0442\u043E\u0440\u043E\u043C. \u0412\u0445\u043E\u0434\u044F\u0449\u0435\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u0435 \u0445\u0440\u0430\u043D\u0438\u0442\u0441\u044F \u0437\u0430\u0448\u0438\u0444\u0440\u043E\u0432\u0430\u043D\u043D\u044B\u043C. \u041F\u043E\u0432\u0442\u043E\u0440\u043D\u0430\u044F \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0430 \u043D\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u0442 \u0438\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0439 \u043E\u0442\u0432\u0435\u0442 \u043A\u043B\u0438\u0435\u043D\u0442\u0443."),
                    React.createElement("label", null,
                        "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u043F\u043E\u0432\u0442\u043E\u0440\u043D\u043E\u0439 \u043F\u043E\u043F\u044B\u0442\u043A\u0438",
                        React.createElement("textarea", { "aria-label": "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u043F\u043E\u0432\u0442\u043E\u0440\u0430 \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0433\u043E", rows: 3, minLength: 8, maxLength: 300, value: s.inboundRetryReason, onChange: (e) => this.setState({ inboundRetryReason: e.target.value }), placeholder: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u043E, \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u043B \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438 \u0438 \u0440\u0430\u0437\u0440\u0435\u0448\u0430\u044E \u043F\u043E\u0432\u0442\u043E\u0440" })),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || s.inboundRetryReason.trim().length < 8, onClick: this.retryInbound }, "\u0412\u0435\u0440\u043D\u0443\u0442\u044C \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0435 \u0432 \u043E\u0447\u0435\u0440\u0435\u0434\u044C")),
                s.modal === 'inbound-dismiss' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" },
                        React.createElement("strong", null, "\u041D\u0435\u043E\u0431\u0440\u0430\u0442\u0438\u043C\u0430\u044F \u043E\u043F\u0435\u0440\u0430\u0446\u0438\u044F."),
                        " \u0417\u0430\u0448\u0438\u0444\u0440\u043E\u0432\u0430\u043D\u043D\u043E\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u0435 \u0431\u0443\u0434\u0435\u0442 \u0443\u0434\u0430\u043B\u0435\u043D\u043E \u0438\u0437 \u043E\u0447\u0435\u0440\u0435\u0434\u0438. \u041E\u043D\u043E \u043D\u0435 \u043F\u043E\u043F\u0430\u0434\u0451\u0442 \u0432 \u043F\u0435\u0440\u0435\u043F\u0438\u0441\u043A\u0443 \u0438 \u0435\u0433\u043E \u043D\u0435\u043B\u044C\u0437\u044F \u0431\u0443\u0434\u0435\u0442 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C \u043A\u043D\u043E\u043F\u043A\u043E\u0439 \u043F\u043E\u0432\u0442\u043E\u0440\u0430. \u0418\u0441\u043F\u043E\u043B\u044C\u0437\u0443\u0439\u0442\u0435 \u0442\u043E\u043B\u044C\u043A\u043E \u043F\u043E\u0441\u043B\u0435 \u0434\u043E\u043A\u0443\u043C\u0435\u043D\u0442\u0438\u0440\u043E\u0432\u0430\u043D\u043D\u043E\u0439 \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0430."),
                    React.createElement("label", null,
                        "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u0437\u0430\u043A\u0440\u044B\u0442\u0438\u044F",
                        React.createElement("select", { "aria-label": "\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0438\u044F \u0437\u0430\u043A\u0440\u044B\u0442\u0438\u044F \u0432\u0445\u043E\u0434\u044F\u0449\u0435\u0433\u043E", value: s.inboundDismissCode, onChange: (e) => this.setState({ inboundDismissCode: e.target.value }) },
                            React.createElement("option", { value: "unrecoverable" }, "\u0418\u0441\u0442\u043E\u0447\u043D\u0438\u043A \u043D\u0435 \u043C\u043E\u0436\u0435\u0442 \u0431\u044B\u0442\u044C \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D"),
                            React.createElement("option", { value: "duplicate" }, "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043D\u043D\u044B\u0439 \u0434\u0443\u0431\u043B\u044C"),
                            React.createElement("option", { value: "invalid_event" }, "\u041D\u0435\u043A\u043E\u0440\u0440\u0435\u043A\u0442\u043D\u043E\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u0435"),
                            React.createElement("option", { value: "other" }, "\u0414\u0440\u0443\u0433\u0430\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u0435\u043D\u043D\u0430\u044F \u043F\u0440\u0438\u0447\u0438\u043D\u0430"))),
                    React.createElement("label", null,
                        "\u0427\u0442\u043E \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u043B\u0438 (\u0431\u0435\u0437 \u043F\u0435\u0440\u0441\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0445 \u0434\u0430\u043D\u043D\u044B\u0445)",
                        React.createElement("textarea", { "aria-label": "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u043D\u0435\u043E\u0431\u0440\u0430\u0442\u0438\u043C\u043E\u0433\u043E \u0437\u0430\u043A\u0440\u044B\u0442\u0438\u044F", rows: 3, minLength: 12, maxLength: 300, value: s.inboundDismissReason, onChange: (e) => this.setState({ inboundDismissReason: e.target.value }), placeholder: "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u043B \u0436\u0443\u0440\u043D\u0430\u043B \u043F\u043B\u043E\u0449\u0430\u0434\u043A\u0438; \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435 \u044D\u0442\u043E\u0433\u043E \u0441\u043E\u0431\u044B\u0442\u0438\u044F \u043D\u0435\u0432\u043E\u0437\u043C\u043E\u0436\u043D\u043E" })),
                    React.createElement("label", { className: "wa-check" },
                        React.createElement("input", { type: "checkbox", checked: s.inboundDismissConfirmed, onChange: (e) => this.setState({ inboundDismissConfirmed: e.target.checked }) }),
                        " \u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044E, \u0447\u0442\u043E \u0441\u043E\u0431\u044B\u0442\u0438\u0435 \u0431\u0443\u0434\u0435\u0442 \u0443\u0434\u0430\u043B\u0435\u043D\u043E \u0431\u0435\u0437 \u0432\u043E\u0437\u043C\u043E\u0436\u043D\u043E\u0441\u0442\u0438 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F."),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || !s.inboundDismissConfirmed || s.inboundDismissReason.trim().length < 12, onClick: this.dismissInbound }, "\u041D\u0435\u043E\u0431\u0440\u0430\u0442\u0438\u043C\u043E \u0437\u0430\u043A\u0440\u044B\u0442\u044C \u0438 \u0443\u0434\u0430\u043B\u0438\u0442\u044C")),
                s.modal === 'inbound-repair' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u0418\u0441\u043F\u0440\u0430\u0432\u043B\u044F\u044E\u0442\u0441\u044F \u0442\u043E\u043B\u044C\u043A\u043E \u043F\u0440\u043E\u0441\u0440\u043E\u0447\u0435\u043D\u043D\u044B\u0435 \u0437\u0430\u0445\u0432\u0430\u0442\u044B \u0438 \u043F\u0443\u0441\u0442\u044B\u0435 \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u0437\u0430\u043F\u0438\u0441\u0438. \u0420\u0430\u0431\u043E\u0442\u0430\u044E\u0449\u0438\u0435 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u0447\u0438\u043A\u0438 \u043D\u0435 \u043E\u0441\u0442\u0430\u043D\u0430\u0432\u043B\u0438\u0432\u0430\u044E\u0442\u0441\u044F, \u0442\u0435\u043A\u0441\u0442\u044B \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439 \u043D\u0435 \u043F\u0440\u043E\u0441\u043C\u0430\u0442\u0440\u0438\u0432\u0430\u044E\u0442\u0441\u044F. \u041D\u0430\u0440\u0443\u0448\u0435\u043D\u043D\u044B\u0435 \u0441\u0432\u044F\u0437\u0438 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0439 \u0442\u0440\u0435\u0431\u0443\u044E\u0442 \u043E\u0442\u0434\u0435\u043B\u044C\u043D\u043E\u0433\u043E \u0430\u0443\u0434\u0438\u0442\u0430."),
                    React.createElement("label", null,
                        "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u0441\u043B\u0443\u0436\u0435\u0431\u043D\u043E\u0433\u043E \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F",
                        React.createElement("textarea", { rows: 3, placeholder: "\u041F\u0440\u043E\u0432\u0435\u0440\u0435\u043D\u044B \u0437\u0430\u0432\u0438\u0441\u0448\u0438\u0435 \u0437\u0430\u0445\u0432\u0430\u0442\u044B \u043F\u043E\u0441\u043B\u0435 \u043F\u0435\u0440\u0435\u0437\u0430\u043F\u0443\u0441\u043A\u0430 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u0447\u0438\u043A\u0430", value: s.inboundRepairReason, onChange: (e) => this.setState({ inboundRepairReason: e.target.value }) })),
                    React.createElement("label", { className: "wa-check" },
                        React.createElement("input", { type: "checkbox", checked: s.inboundRepairConfirmed, onChange: (e) => this.setState({ inboundRepairConfirmed: e.target.checked }) }),
                        " \u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044E \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435 \u0442\u043E\u043B\u044C\u043A\u043E \u043F\u0440\u043E\u0441\u0440\u043E\u0447\u0435\u043D\u043D\u044B\u0445 \u0437\u0430\u0434\u0430\u043D\u0438\u0439."),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || !s.inboundRepairConfirmed || s.inboundRepairReason.trim().length < 12, onClick: this.repairInboundExpired }, "\u0412\u044B\u043F\u043E\u043B\u043D\u0438\u0442\u044C \u0431\u0435\u0437\u043E\u043F\u0430\u0441\u043D\u043E\u0435 \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435")),
                s.modal === 'inbound-pause' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, s.inboundPauseAction === 'pause' ? 'После остановки новые webhook сохраняются в зашифрованную очередь, но не отображаются в Inbox до восстановления. Уже начатая обработка может завершиться.' : 'После возобновления накопленные события будут обрабатываться фоновыми обработчиками. Паузы отдельных каналов сохраняются.'),
                    React.createElement("label", null,
                        "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044F",
                        React.createElement("textarea", { "aria-label": "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0438 \u0432\u0445\u043E\u0434\u044F\u0449\u0438\u0445", rows: 3, minLength: 8, maxLength: 160, value: s.inboundPauseReason, onChange: (e) => this.setState({ inboundPauseReason: e.target.value }), placeholder: "\u041F\u0440\u043E\u0432\u0435\u0440\u0438\u043B \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u043A\u0430\u043D\u0430\u043B\u0430 \u0438 \u0440\u0430\u0437\u0440\u0435\u0448\u0430\u044E \u043E\u043F\u0435\u0440\u0430\u0446\u0438\u044E" })),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || s.inboundPauseReason.trim().length < 8, onClick: this.applyInboundPause }, s.inboundPauseAction === 'pause' ? 'Приостановить обработку' : 'Возобновить обработку')),
                s.modal === 'inbound-batch' && React.createElement("div", { className: "modal-form" },
                    React.createElement("p", { className: "modal-help" }, "\u041F\u0440\u0435\u0434\u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440 \u043E\u043F\u0440\u0435\u0434\u0435\u043B\u044F\u0435\u0442 \u0442\u043E\u0447\u043D\u044B\u0439 \u043D\u0430\u0431\u043E\u0440 \u043E\u0448\u0438\u0431\u043E\u043A \u0432\u044B\u0431\u0440\u0430\u043D\u043D\u043E\u0433\u043E \u0430\u043A\u043A\u0430\u0443\u043D\u0442\u0430. \u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043D\u0438\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0443\u0435\u0442 90 \u0441\u0435\u043A\u0443\u043D\u0434: \u0435\u0441\u043B\u0438 \u0434\u0440\u0443\u0433\u043E\u0439 \u0430\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440 \u0438\u0437\u043C\u0435\u043D\u0438\u0442 \u043E\u0447\u0435\u0440\u0435\u0434\u044C, \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044F \u043D\u043E\u0432\u0430\u044F \u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0430. \u0418\u0441\u0445\u043E\u0434\u044F\u0449\u0438\u0435 \u043A\u043B\u0438\u0435\u043D\u0442\u0430\u043C \u043D\u0435 \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u044E\u0442\u0441\u044F."),
                    React.createElement("div", { className: "ops-batch-preview", role: "status" },
                        React.createElement("span", null, "\u041F\u043E\u0434\u0433\u043E\u0442\u043E\u0432\u043B\u0435\u043D\u043E \u043A \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044E"),
                        React.createElement("strong", null,
                            s.inboundBatchPreview?.count || 0,
                            " \u0441\u043E\u0431\u044B\u0442\u0438\u0439"),
                        React.createElement("small", null, "\u0411\u0435\u0437 \u0440\u0430\u0441\u043A\u0440\u044B\u0442\u0438\u044F \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0439 \u0438 \u0434\u0430\u043D\u043D\u044B\u0445 \u043A\u043B\u0438\u0435\u043D\u0442\u043E\u0432. \u041F\u043B\u0430\u043D \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D 20 \u0441\u043E\u0431\u044B\u0442\u0438\u044F\u043C\u0438.")),
                    React.createElement("button", { className: "btn ghost ops-review-refresh", disabled: s.loading, onClick: this.refreshInboundBatchPreview }, "\u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C \u043F\u0440\u0435\u0434\u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440 \u043E\u0447\u0435\u0440\u0435\u0434\u0438"),
                    React.createElement("label", null,
                        "\u0427\u0442\u043E \u043F\u0440\u043E\u0432\u0435\u0440\u0435\u043D\u043E",
                        React.createElement("textarea", { "aria-label": "\u041F\u0440\u0438\u0447\u0438\u043D\u0430 \u043F\u0430\u043A\u0435\u0442\u043D\u043E\u0433\u043E \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u044F", rows: 3, minLength: 8, maxLength: 300, value: s.inboundBatchReason, onChange: (e) => this.setState({ inboundBatchReason: e.target.value }), placeholder: "\u041A\u043B\u044E\u0447 \u0440\u0430\u0441\u0448\u0438\u0444\u0440\u043E\u0432\u0430\u043D\u0438\u044F \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D, \u0441\u043E\u0435\u0434\u0438\u043D\u0435\u043D\u0438\u0435 \u043F\u0440\u043E\u0432\u0435\u0440\u0435\u043D\u043E" })),
                    React.createElement("button", { className: "btn primary wide", disabled: s.loading || !s.inboundBatchPreview?.count || s.inboundBatchReason.trim().length < 8, onClick: this.retryInboundBatch },
                        "\u041F\u043E\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044C \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u043B\u0435\u043D\u0438\u0435 ",
                        s.inboundBatchPreview?.count || 0,
                        " \u0441\u043E\u0431\u044B\u0442\u0438\u0439")),
                s.modal === 'invite' && React.createElement("div", { className: "modal-form" },
                    React.createElement("label", null,
                        "\u041F\u043E\u0447\u0442\u0430 \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u0430",
                        React.createElement("input", { type: "email", value: s.inviteEmail, onChange: (e) => this.setState({ inviteEmail: e.target.value }), placeholder: "employee@company.com" })),
                    React.createElement("label", null,
                        "\u0420\u043E\u043B\u044C",
                        React.createElement("select", { value: s.inviteRole, onChange: (e) => this.setState({ inviteRole: e.target.value }) },
                            React.createElement("option", { value: "operator" }, "\u041E\u043F\u0435\u0440\u0430\u0442\u043E\u0440"),
                            React.createElement("option", { value: "manager" }, "\u041C\u0435\u043D\u0435\u0434\u0436\u0435\u0440"),
                            React.createElement("option", { value: "lead" }, "\u0420\u0443\u043A\u043E\u0432\u043E\u0434\u0438\u0442\u0435\u043B\u044C"),
                            React.createElement("option", { value: "admin" }, "\u0410\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u043E\u0440"))),
                    s.inviteToken && React.createElement("div", { className: "invite-result" },
                        React.createElement("small", null, "\u0422\u041E\u041A\u0415\u041D \u041F\u0420\u0418\u0413\u041B\u0410\u0428\u0415\u041D\u0418\u042F"),
                        React.createElement("div", { className: "invite-copy" },
                            React.createElement("input", { readOnly: true, value: s.inviteToken }),
                            React.createElement("button", { className: "icon-btn", title: "\u0421\u043A\u043E\u043F\u0438\u0440\u043E\u0432\u0430\u0442\u044C", onClick: () => { navigator.clipboard?.writeText(s.inviteToken); this.notify('Токен скопирован'); } },
                                React.createElement(Icon, { name: "copy" }))),
                        React.createElement("p", null, "\u041F\u0435\u0440\u0435\u0434\u0430\u0439\u0442\u0435 \u0442\u043E\u043A\u0435\u043D \u0441\u043E\u0442\u0440\u0443\u0434\u043D\u0438\u043A\u0443. \u041E\u0442\u043F\u0440\u0430\u0432\u043A\u0430 \u043F\u043E\u0447\u0442\u044B \u043F\u043E\u043A\u0430 \u043D\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0435\u043D\u0430.")),
                    React.createElement("button", { className: "btn primary wide", onClick: this.invite, disabled: !s.inviteEmail || s.loading }, "\u0421\u043E\u0437\u0434\u0430\u0442\u044C \u043F\u0440\u0438\u0433\u043B\u0430\u0448\u0435\u043D\u0438\u0435"))));
    }
    render() { const s = this.state; if (s.boot)
        return React.createElement("div", { className: "loading-screen" },
            React.createElement("span", { className: "brand-mark" },
                "O",
                React.createElement("span", null, "X")),
            React.createElement("p", null, "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u0437\u0430\u0449\u0438\u0449\u0451\u043D\u043D\u043E\u0433\u043E \u043F\u0440\u043E\u0441\u0442\u0440\u0430\u043D\u0441\u0442\u0432\u0430...")); if (!s.me)
        return this.renderAuth(); return React.createElement("div", { className: 'app-shell ' + (s.view === 'inbox' ? 'quiet-inbox-app' : '') },
        this.renderSidebar(),
        React.createElement("main", { className: "main-shell" },
            s.view !== 'inbox' && React.createElement("div", { className: "top-strip" },
                React.createElement("button", { className: "icon-btn mobile-menu", onClick: () => this.setState({ sidebarOpen: true }) },
                    React.createElement(Icon, { name: "menu", size: 20 })),
                React.createElement("div", { className: "top-breadcrumb" },
                    React.createElement("span", null, "OSMANX OMNICHAT"),
                    React.createElement(Icon, { name: "chevron", size: 13 }),
                    React.createElement("strong", null, s.view === 'start' ? 'Быстрый старт' : NAV.find((n) => n[0] === s.view)?.[2] || 'Настройки')),
                React.createElement("div", { className: "top-actions" },
                    React.createElement("button", { className: "icon-btn", onClick: this.toggleNotifications, title: "\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044C \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u043E \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u044F\u0445" },
                        React.createElement(Icon, { name: "bell", size: 18 })),
                    s.alerts?.unanswered_over_sla > 0 && React.createElement("button", { className: "sla-pill", onClick: () => { this.changeView('inbox'); this.notify('Просроченных обращений: ' + s.alerts.unanswered_over_sla); } },
                        React.createElement(Icon, { name: "clock", size: 14 }),
                        s.alerts.unanswered_over_sla,
                        " SLA"),
                    s.me.organization.is_demo && React.createElement("span", { className: "demo-label" },
                        React.createElement("span", { className: "dot green" }),
                        " \u0414\u0415\u041C\u041E\u0420\u0415\u0416\u0418\u041C"),
                    React.createElement("span", { className: "top-date" }, new Date().toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric', month: 'short' })),
                    React.createElement("button", { className: "icon-btn", title: "\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438", onClick: () => this.changeView('settings') },
                        React.createElement(Icon, { name: "settings", size: 18 })))),
            React.createElement("div", { className: "main-body" }, s.view === 'start' ? this.renderStart() : s.view === 'command' ? this.renderCommand() : s.view === 'inbox' ? this.renderInbox() : s.view === 'websites' ? this.renderWebsites() : s.view === 'operations' ? this.renderOperations() : s.view === 'contacts' ? this.renderContacts() : s.view === 'deals' ? this.renderDeals() : s.view === 'analytics' ? this.renderAnalytics() : s.view === 'rules' ? this.renderRules() : s.view === 'integrations' ? this.renderIntegrations() : s.view === 'team' ? this.renderTeam() : this.renderSettings())),
        s.toast && React.createElement("div", { className: "toast" },
            React.createElement(Icon, { name: "info", size: 17 }),
            s.toast,
            React.createElement("button", { onClick: () => this.setState({ toast: '' }) },
                React.createElement(Icon, { name: "close", size: 14 }))),
        s.modal && this.renderModal()); }
}
ReactDOM.render(React.createElement(OmniApp, null), document.getElementById('root'));
