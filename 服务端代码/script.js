/* 红楼梦研究 · Search App JavaScript */

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('search-form');
    const input = document.getElementById('search-input');
    const resultsArea = document.getElementById('results-area');
    const placeholder = document.getElementById('placeholder');
    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const topKSelect = document.getElementById('top-k-select');
    const aiBtn = document.getElementById('ai-btn');
    const aiBalance = document.getElementById('ai-balance');
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    let aiModeActive = false;

    // --- Load AI balance ---
    fetch('/api/balance')
        .then(r => r.json())
        .then(data => {
            if (aiBalance) {
                if (data.authenticated) {
                    if (data.can_use_ai) {
                        if (data.is_lifetime || data.is_admin) {
                            aiBalance.textContent = '∞';
                        } else {
                            aiBalance.textContent = '余' + data.balance + '次';
                        }
                    } else {
                        aiBalance.innerHTML = '<a href="/recharge" style="color:var(--zhusha);">已用完</a>';
                    }
                } else {
                    aiBalance.innerHTML = '<a href="/login" style="color:var(--jin);">登录</a>';
                }
            }
        })
        .catch(() => {});

    // --- Chat session (promoted to global for sidebar access) ---
    window._chatSessionId = localStorage.getItem('hlm_chat_session') || '';
    window._chatMessages = [];
    var chatSessionId = window._chatSessionId; // backward compat
    // Populate sidebar with sessions on page load
    loadSessions(true);

    // --- AI toggle ---
    aiBtn.addEventListener('click', function () {
        aiModeActive = !aiModeActive;
        this.classList.toggle('active', aiModeActive);
        this.textContent = aiModeActive ? 'AI 问答（开）' : 'AI 问答';
        modeRadios.forEach(r => r.disabled = aiModeActive);
        if (aiModeActive) {
            initChatUI();
        } else {
            // Restore normal search results when toggling off
            resultsArea.innerHTML = '';
            if (placeholder) placeholder.style.display = '';
            const q = input.value.trim();
            if (q) doNormalSearch(q);
        }
    });

    // --- URL parameter parsing ---
    const params = new URLSearchParams(window.location.search);
    const urlQuery = params.get('q');
    const urlMode = params.get('mode');
    const urlAi = params.get('ai');

    if (urlAi === '1') {
        aiModeActive = true;
        aiBtn.classList.add('active');
        aiBtn.textContent = 'AI 问答（开）';
        modeRadios.forEach(r => r.disabled = true);
    }

    if (urlQuery) {
        input.value = urlQuery;
        if (urlMode && !aiModeActive) {
            const radio = document.querySelector(`input[name="mode"][value="${urlMode}"]`);
            if (radio) radio.checked = true;
        }
        // Don't re-submit AI query on page refresh
        if (aiModeActive) {
            initChatUI();
        } else {
            doSearch(urlQuery);
        }
    }

    // --- Form submit ---
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const q = input.value.trim();
        if (!q) return;
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const aiParam = aiModeActive ? '&ai=1' : '';
        const newUrl = `/?q=${encodeURIComponent(q)}&mode=${mode}${aiParam}`;
        window.history.pushState({ q, mode, ai: aiModeActive }, '', newUrl);
        if (aiModeActive) {
            // In AI mode: send directly as chat message without resetting UI
            if (!document.getElementById('chat-messages')) {
                initChatUI();
            }
            doAiChat(q);
        } else {
            doNormalSearch(q);
        }
    });

    // --- Search function ---
    function doSearch(query) {
        if (placeholder) placeholder.style.display = 'none';
        if (aiModeActive) {
            if (!document.getElementById('chat-messages')) {
                initChatUI();
            }
            doAiChat(query);
        } else {
            loading.style.display = 'flex';
            loadingText.textContent = '搜索中……';
            resultsArea.innerHTML = '';
            doNormalSearch(query);
        }
    }

    // --- AbortController with timeout ---
    function fetchWithTimeout(url, timeoutMs = 150000) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeoutMs);
        return fetch(url, { signal: controller.signal }).finally(() => clearTimeout(timer));
    }

    function doNormalSearch(query) {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const topK = topKSelect ? topKSelect.value : 12;
        loadingText.textContent = '搜索中……';
        resultsArea.innerHTML = '';

        fetchWithTimeout(`/api/search?q=${encodeURIComponent(query)}&mode=${mode}&top_k=${topK}`)
            .then(r => r.json())
            .then(data => {
                loading.style.display = 'none';
                if (data.error) {
                    resultsArea.innerHTML = `<div class="error-page"><p>${data.error}</p></div>`;
                    return;
                }
                if (data.results.length === 0) {
                    resultsArea.innerHTML = `
                        <div class="results-placeholder">
                            <p>未找到匹配结果</p>
                        </div>`;
                    return;
                }
                renderResults(data.results, query);
            })
            .catch(err => {
                loading.style.display = 'none';
                const msg = err.name === 'AbortError' ? '请求超时，请重试' : err.message;
                resultsArea.innerHTML = `<div class="error-page"><p>搜索失败：${msg}</p></div>`;
            });
    }

    // --- Chat UI ---
    // AbortController for AI chat
    let aiAbortController = null;

    window._initChatUI = function () {
        resultsArea.innerHTML = `
            <div class="chat-container">
                <div class="chat-messages" id="chat-messages"></div>
                <div class="chat-input-area">
                    <textarea class="chat-input" id="chat-input" rows="1"
                        placeholder="输入您的问题……"
                        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendChatMessage();}"></textarea>
                    <button class="chat-send-btn" id="chat-send-btn" onclick="sendChatMessage()">发送</button>
                    <button class="chat-send-btn" id="chat-cancel-btn" onclick="cancelAiChat()" style="display:none">停止</button>
                </div>
            </div>
        `;

        window._chatMessages = [];
        // If there's a saved session, load its messages (survives refresh)
        if (window._chatSessionId) {
            fetch('/api/chat/sessions/' + encodeURIComponent(window._chatSessionId) + '/messages')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var chatMessages = document.getElementById('chat-messages');
                    if (!chatMessages) return;
                    if (data.messages && data.messages.length > 0) {
                        chatMessages.innerHTML = '';
                        window._chatMessages = data.messages || [];
                        (data.messages || []).forEach(function(m) {
                            addChatBubble(m.role, m.content);
                        });
                    } else {
                        addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
                    }
                })
                .catch(function() {
                    addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
                });
        } else {
            addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
        }
    };
    function initChatUI() { window._initChatUI(); }

    window._addChatBubble = function (role, content) { addChatBubble(role, content); };
    // Create chat container HTML without welcome bubble (for restoring sessions)
    function ensureChatContainer() {
        if (document.getElementById('chat-messages')) return;
        resultsArea.innerHTML = `
            <div class="chat-container">
                <div class="chat-messages" id="chat-messages"></div>
                <div class="chat-input-area">
                    <textarea class="chat-input" id="chat-input" rows="1"
                        placeholder="输入您的问题……"
                        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendChatMessage();}"></textarea>
                    <button class="chat-send-btn" id="chat-send-btn" onclick="sendChatMessage()">发送</button>
                    <button class="chat-send-btn" id="chat-cancel-btn" onclick="cancelAiChat()" style="display:none">停止</button>
                </div>
            </div>
        `;
        window._chatMessages = [];
    }

    window.ensureChatContainer = ensureChatContainer;

    window._escapeHtml = function (text) { return escapeHtml(text); };
    window._sendChatMessage = function () { sendChatMessage(); };

    function sendChatMessage() {
        var inp = document.getElementById('chat-input');
        var q = inp ? inp.value.trim() : '';
        if (!q) return;
        if (inp) inp.value = '';
        doAiChat(q);
    }

    function cancelAiChat() {
        if (aiAbortController) {
            aiAbortController.abort();
            aiAbortController = null;
        }
        removeChatThinking();
        var cb = document.getElementById('chat-cancel-btn');
        var sb = document.getElementById('chat-send-btn');
        if (cb) cb.style.display = 'none';
        if (sb) sb.style.display = '';
    }

    function addChatBubble(role, content) {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = `chat-bubble chat-bubble-${role}`;

        if (role === 'user') {
            div.textContent = content;
        } else {
            // Render AI answer with markdown-like formatting
            div.innerHTML = formatAiAnswer(content);
        }

        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function addChatError(message, retryQuery, actionUrl, actionLabel) {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = 'chat-bubble chat-bubble-error';
        let html = `<p>${escapeHtml(message)}</p>`;
        if (actionUrl && actionLabel) {
            html += `<a href="${actionUrl}" class="chat-action-btn">${escapeHtml(actionLabel)}</a>`;
        }
        if (retryQuery) {
            html += `<button class="retry-btn" onclick="doAiChat('${escapeHtml(retryQuery)}')">重试</button>`;
        }
        div.innerHTML = html;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function addChatSources(sources) {
        if (!sources || sources.length === 0) return;
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = 'chat-bubble chat-bubble-sources';
        div.innerHTML = `<strong>参考来源：</strong> ${sources.map(s =>
            `<a href="/source/${s.source}" target="_blank">${s.source_pretty}</a>`
        ).join(' · ')}`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function addChatThinking() {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = 'chat-bubble chat-bubble-thinking';
        div.id = 'chat-thinking';
        div.innerHTML = '<span class="thinking-dots">思考中……</span><span class="thinking-timer" id="thinking-timer">（0秒）</span>';
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;

        // Start timer
        if (window.thinkingTimerInterval) clearInterval(window.thinkingTimerInterval);
        var sec = 0;
        window.thinkingTimerInterval = setInterval(function() {
            sec++;
            var el = document.getElementById('thinking-timer');
            if (el) el.textContent = '（' + sec + '秒）';
        }, 1000);
    }

    function removeChatThinking() {
        const el = document.getElementById('chat-thinking');
        if (el) el.remove();
        if (window.thinkingTimerInterval) {
            clearInterval(window.thinkingTimerInterval);
            window.thinkingTimerInterval = null;
        }
    }

    function doAiChat(query) {
        addChatBubble('user', query);
        addChatThinking();

        // Show cancel button
        var cancelBtn = document.getElementById('chat-cancel-btn');
        var sendBtn = document.getElementById('chat-send-btn');
        if (cancelBtn) cancelBtn.style.display = '';
        if (sendBtn) sendBtn.style.display = 'none';

        aiAbortController = new AbortController();
        var timeoutId = setTimeout(function() { if (aiAbortController) aiAbortController.abort(); }, 300000);

        fetch('/api/ai-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: query,
                session_id: window._chatSessionId,
            }),
            signal: aiAbortController.signal,
        })
            .then(r => {
                if (!r.ok) throw new Error('服务器错误 (' + r.status + ')');
                return r.json();
            })
            .then(data => {
                removeChatThinking();
                if (data.error) {
                    if (data.needs_login) {
                        addChatError('请先登录后再使用 AI 问答', query, '/login', '去登录');
                    } else if (data.needs_recharge) {
                        addChatError('AI 问答次数已用尽', query, '/recharge', '去充值');
                    } else {
                        addChatError(data.error, query);
                    }
                    return;
                }
                // Save session (only add to sidebar when it's a new session)
                if (data.session_id) {
                    window._chatSessionId = data.session_id;
                    localStorage.setItem('hlm_chat_session', data.session_id);
                    if (data.is_new) {
                        _addSessionToSidebar(query.substring(0, 30));
                    }
                }
                addChatBubble('ai', data.answer);
                addChatSources(data.sources);
                window._chatMessages.push({ role: 'user', content: query });
                window._chatMessages.push({ role: 'assistant', content: data.answer });
                if (cancelBtn) cancelBtn.style.display = 'none';
                if (sendBtn) sendBtn.style.display = '';
                aiAbortController = null;
                clearTimeout(timeoutId);
            })
            .catch(err => {
                removeChatThinking();
                if (cancelBtn) cancelBtn.style.display = 'none';
                if (sendBtn) sendBtn.style.display = '';
                aiAbortController = null;
                clearTimeout(timeoutId);
                if (err.name === 'AbortError') {
                    addChatBubble('ai', '已取消，请继续提问。');
                    return;
                }
                let msg = err.name === 'TimeoutError'
                    ? '请求超时。AI 问答耗时较长，请重试。'
                    : err.message;
                addChatError('AI 问答失败：' + msg, query);
            });
    }

    function formatAiAnswer(text) {
        if (!text) return '';
        let html = escapeHtml(text);

        // Split into body and footnotes section
        let body = html;
        let footnotes = '';
        const fnMatch = html.match(/(注释[：:]\s*)/);
        if (fnMatch) {
            body = html.substring(0, fnMatch.index);
            footnotes = html.substring(fnMatch.index + fnMatch[1].length);
        }

        // Strip page number references from footnotes (keep chapter/section only)
        if (footnotes) {
            footnotes = footnotes.replace(/[,，\s]*第\d+(?:[-—–]\d+)?页[,，\s]*/g, '');
            footnotes = footnotes.replace(/[,，\s]*页\d+(?:[-—–]\d+)?[,，\s]*/g, '');
        }

        // Collect footnote numbers that exist in the footnotes section
        var footnoteIds = {};
        if (footnotes) {
            footnotes = footnotes.replace(/^\[(\d+)\]/gm, function(match, num) {
                footnoteIds[num] = true;
                return '<a id="fn-' + num + '"></a>[' + num + ']';
            });
        }

        // Process body: [N] → clickable superscript link only if footnote exists
        body = body.replace(/\[(\d+)\]/g, function(match, num) {
            if (footnoteIds[num]) {
                return '<sup class="fn-marker"><a href="#fn-' + num + '">[' + num + ']</a></sup>';
            }
            return '<sup class="fn-marker fn-missing">[' + num + ']</sup>';
        });
        body = body
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        // Process footnotes: remaining formatting
        if (footnotes) {
            footnotes = footnotes
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
            html = body + '<div class="footnotes-section"><br>注释：<br>' + footnotes + '</div>';
        } else {
            html = body;
        }

        // Add disclaimer
        html += '<div class="ai-answer-disclaimer">AI 回答基于知识库内容生成，仅供参考</div>';
        return html;
    }

    // --- Render results ---
    function renderResults(results, query) {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const modeNames = { hybrid: '混合', semantic_only: '语义', keyword_only: '关键词' };

        const html = `
            <div class="results-list">
                <div class="results-header">
                    ${results.length} 条结果 · ${modeNames[mode] || mode}
                </div>
                ${results.map(r => renderCard(r, query)).join('')}
            </div>`;

        resultsArea.innerHTML = html;
    }

    // --- Render a single result card ---
    function renderCard(r, query) {
        const text = r.text || r.line_text || '';
        const highlighted = highlightText(text, query);
        const source = r.source || '';
        const sourcePretty = r.source_pretty || source.split('/').pop().replace(/\.(md|txt)$/, '');
        const score = r.score_hybrid !== undefined ? r.score_hybrid.toFixed(3) : '';
        const chunkId = r.chunk_id || '';

        const expandHtml = chunkId ? `
            <div class="expand-section">
                <button class="expand-btn" data-chunk="${chunkId}">展开</button>
                <div class="expand-content" id="expand-${chunkId.replace(/[.#\/]/g, '-')}"></div>
            </div>
        ` : '';

        return `
            <div class="result-item">
                <div class="result-header">
                    <span class="result-source">
                        <a href="/source/${source}" target="_blank">${sourcePretty}</a>
                    </span>
                    ${score ? `<span class="result-score">${score}</span>` : ''}
                </div>
                <div class="result-text">${highlighted}</div>
                ${expandHtml}
            </div>
        `;
    }

    // --- Highlight matching terms ---
    function highlightText(text, query) {
        if (!query) return escapeHtml(text);
        const terms = query.split(/\s+/).filter(t => t.length > 0);
        let result = escapeHtml(text);
        terms.forEach(term => {
            const escaped = escapeHtml(term);
            const regex = new RegExp(`(${escapeRegex(escaped)})`, 'gi');
            result = result.replace(regex, '<span class="highlight">$1</span>');
        });
        return result;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    window.escapeHtml = escapeHtml;

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // --- Expand context (delegated) ---
    resultsArea.addEventListener('click', function (e) {
        const btn = e.target.closest('.expand-btn');
        if (!btn) return;
        const chunkId = btn.dataset.chunk;
        const contentDiv = document.getElementById(`expand-${chunkId.replace(/[.#\/]/g, '-')}`);

        if (contentDiv.classList.contains('visible')) {
            contentDiv.classList.remove('visible');
            btn.textContent = '展开';
            return;
        }
        if (contentDiv.dataset.loaded) {
            contentDiv.classList.add('visible');
            btn.textContent = '收起';
            return;
        }

        contentDiv.innerHTML = '<p style="padding:0.5rem">加载中……</p>';
        contentDiv.classList.add('visible');
        btn.textContent = '加载中';

        fetch(`/api/expand?chunk_id=${encodeURIComponent(chunkId)}`)
            .then(r => r.json())
            .then(data => {
                contentDiv.innerHTML = `<pre style="white-space:pre-wrap;font-family:inherit">${escapeHtml(data.text || '')}</pre>`;
                contentDiv.dataset.loaded = '1';
                btn.textContent = '收起';
            })
            .catch(() => {
                contentDiv.innerHTML = '<p style="padding:0.5rem">加载失败</p>';
                btn.textContent = '展开';
            });
    });

    // --- Browser back/forward ---
    window.addEventListener('popstate', function (e) {
        if (e.state && e.state.q) {
            input.value = e.state.q;
            const radio = document.querySelector(`input[name="mode"][value="${e.state.mode}"]`);
            if (radio) radio.checked = true;
            doSearch(e.state.q);
        }
    });


    // =======================================================================
    // 红楼梦名言滚动 100+
    // =======================================================================

    const QUOTES = [
        // ——— 开卷诗 ———
        '满纸荒唐言，一把辛酸泪。都云作者痴，谁解其中味。',
        '无材可去补苍天，枉入红尘若许年。此系身前身后事，倩谁记去作奇传。',
        '悲喜千般同幻渺，古今一梦尽荒唐。',

        // ——— 太虚幻境 ———
        '假作真时真亦假，无为有处有还无。',
        '春恨秋悲皆自惹，花容月貌为谁妍。',
        '厚地高天，堪叹古今情不尽；痴男怨女，可怜风月债难酬。',
        '幽微灵秀地，无可奈何天。',
        '空对着，山中高士晶莹雪；终不忘，世外仙姝寂寞林。',

        // ——— 红楼梦曲 ———
        '开辟鸿蒙，谁为情种？都只为风月情浓。',
        '一个是阆苑仙葩，一个是美玉无瑕。若说没奇缘，今生偏又遇着他；若说有奇缘，如何心事终虚化？',
        '枉凝眉，想眼中能有多少泪珠儿，怎经得秋流到冬尽，春流到夏！',
        '趁着这奈何天，伤怀日，寂寥时，试遣愚衷。',
        '都道是金玉良姻，俺只念木石前盟。',
        '叹人间，美中不足今方信。纵然是齐眉举案，到底意难平。',
        '机关算尽太聪明，反算了卿卿性命。',
        '好一似食尽鸟投林，落了片白茫茫大地真干净！',
        '一个是水中月，一个是镜中花。',
        '一帆风雨路三千，把骨肉家园齐来抛闪。',
        '自古穷通皆有定，离合岂无缘？',
        '这是尘寰中消长数应当，何必枉悲伤！',
        '为官的，家业凋零；富贵的，金银散尽。',
        '有恩的，死里逃生；无情的，分明报应。',
        '看破的，遁入空门；痴迷的，枉送了性命。',

        // ——— 金陵判词 ———
        '可叹停机德，堪怜咏絮才。玉带林中挂，金簪雪里埋。',
        '二十年来辨是非，榴花开处照宫闱。三春争及初春景，虎兕相逢大梦归。',
        '才自精明志自高，生于末世运偏消。清明涕送江边望，千里东风一梦遥。',
        '富贵又何为，襁褓之间父母违。展眼吊斜晖，湘江水逝楚云飞。',
        '欲洁何曾洁，云空未必空。可怜金玉质，终陷淖泥中。',
        '子系中山狼，得志便猖狂。金闺花柳质，一载赴黄粱。',
        '勘破三春景不长，缁衣顿改昔年妆。可怜绣户侯门女，独卧青灯古佛旁。',
        '凡鸟偏从末世来，都知爱慕此生才。一从二令三人木，哭向金陵事更哀。',
        '势败休云贵，家亡莫论亲。偶因济刘氏，巧得遇恩人。',
        '桃李春风结子完，到头谁似一盆兰。如冰水好空相妒，枉与他人作笑谈。',
        '情天情海幻情身，情既相逢必主淫。漫言不肖皆荣出，造衅开端实在宁。',
        '霁月难逢，彩云易散。心比天高，身为下贱。风流灵巧招人怨。',
        '寿夭多因毁谤生，多情公子空牵念。',
        '枉自温柔和顺，空云似桂如兰。堪羡优伶有福，谁知公子无缘。',
        '根并荷花一茎香，平生遭际实堪伤。自从两地生孤木，致使香魂返故乡。',

        // ——— 经典对白与名句 ———
        '女儿是水做的骨肉，男子是泥做的骨肉。我见了女儿，我便清爽；见了男子，便觉浊臭逼人。',
        '世事洞明皆学问，人情练达即文章。',
        '纵有千年铁门槛，终须一个土馒头。',
        '黄金万两容易得，知心一个也难求。',
        '心病终须心药治，解铃还是系铃人。',
        '千里搭长棚，没有不散的筵席。',
        '浮生着甚苦奔忙，盛席华筵终散场。',
        '大旨谈情，实录其事。',
        '编新不如述旧，刻古终胜雕今。',

        // ——— 黛玉诗词 ———
        '花谢花飞花满天，红消香断有谁怜。',
        '一年三百六十日，风刀霜剑严相逼。',
        '质本洁来还洁去，强于污淖陷渠沟。',
        '侬今葬花人笑痴，他年葬侬知是谁。',
        '试看春残花渐落，便是红颜老死时。',
        '一朝春尽红颜老，花落人亡两不知。',
        '半卷湘帘半掩门，碾冰为土玉为盆。',
        '偷来梨蕊三分白，借得梅花一缕魂。',
        '月窟仙人缝缟袂，秋闺怨女拭啼痕。',
        '娇羞默默同谁诉，倦倚西风夜已昏。',
        '孤标傲世偕谁隐，一样花开为底迟。',
        '怅望西风抱闷思，蓼红苇白断肠时。',
        '焦首朝朝还暮暮，煎心日日复年年。',
        '寒塘渡鹤影，冷月葬花魂。',
        '草木也知愁，韶华竟白头。',
        '叹今生谁舍谁收。',
        '嫁与东风春不管，凭尔去，忍淹留。',
        '粉堕百花洲，香残燕子楼。',
        '空挂纤纤缕，徒垂络络丝。',
        '池上凭栏愁无碍，鸾镜菱花仔细看。',

        // ——— 宝钗诗词 ———
        '淡极始知花更艳。',
        '好风凭借力，送我上青云。',
        '万缕千丝终不改，任他随聚随分。',
        '白玉堂前春解舞，东风卷得均匀。',
        '蜂团蝶阵乱纷纷，几曾随逝水，岂必委芳尘。',
        '珍重芳姿昼掩门，自携手瓮灌苔盆。',
        '胭脂洗出秋阶影，冰雪招来露砌魂。',

        // ——— 湘云及他人诗词 ———
        '莫道缟仙能羽化，多情伴我咏黄昏。',
        '神仙昨日降都门，种得蓝田玉一盆。',
        '秋光荏苒休辜负，相对原宜惜寸阴。',
        '萧疏篱畔科头坐，清冷香中抱膝吟。',
        '数去更无君傲世，看来惟有我知音。',
        '醉眠芳草，飞觞醉月。',

        // ——— 大观园题咏 ———
        '绕堤柳借三篙翠，隔岸花分一脉香。',
        '宝鼎茶闲烟尚绿，幽窗棋罢指犹凉。',
        '新涨绿添浣葛处，好云香护采芹人。',
        '麝兰芳霭斜阳院，杜若香飘明月洲。',
        '三径香风飘玉蕙，一庭明月照金兰。',
        '金门玉户神仙府，桂殿兰宫妃子家。',
        '菱荇鹅儿水，桑榆燕子梁。',
        '杏帘招客饮，在望有山庄。',
        '一畦春韭绿，十里稻花香。',
        '盛世无饥馁，何须耕织忙。',
        '吟成豆蔻才犹艳，睡足荼蘼梦亦香。',

        // ——— 人物外貌 ———
        '天然一段风骚，全在眉梢；平生万种情思，悉堆眼角。',
        '面若中秋之月，色如春晓之花。',
        '闲静时如姣花照水，行动处似弱柳扶风。',
        '心较比干多一窍，病如西子胜三分。',
        '虽怒时而若笑，即嗔视而有情。',
        '唇不点而红，眉不画而翠。',
        '任是无情也动人。',
        '黛眉颦蹙，风流袅娜。',

        // ——— 好了歌 ———
        '世人都晓神仙好，惟有功名忘不了。古今将相在何方？荒冢一堆草没了。',
        '世人都晓神仙好，只有金银忘不了。终朝只恨聚无多，及到多时眼闭了。',
        '世人都晓神仙好，只有姣妻忘不了。君生日日说恩情，君死又随人去了。',
        '世人都晓神仙好，只有儿孙忘不了。痴心父母古来多，孝顺儿孙谁见了。',

        // ——— 对联与警句 ———
        '眼前道路无经纬，皮里春秋空黑黄。',
        '酒未敌腥还用菊，性防积冷定须姜。',
        '于今落釜成何益，月浦空余禾黍香。',
        '白杨村里人呜咽，青枫林下鬼吟哦。',
        '闻说道，西方宝树唤婆娑，上结着长生果。',
        '渐闻语笑寂，空剩雪霜痕。',
        '芳情只自遣，雅趣向谁言。',
        '彻旦休云倦，烹茶更细论。',
        '失意人逢失意事，新啼痕间旧啼痕。',
        '瘦影正临春水照，卿须怜我我怜卿。',
        '赤条条来去无牵挂。',

        // ——— 经典对话 ———
        '黛玉：我为的是我的心。',
        '宝玉：你死了，我做和尚去。',
        '紫鹃：万两黄金容易得，知心一个也难求。',
        '探春：百足之虫，死而不僵。',
        '凤姐：大有大的难处。',
        '刘姥姥：大火烧了毛毛虫。',
        '晴雯：我宁可一头碰死了，也不出这门。',
        '袭人：好歹留着麝月。',
        '龄官：划蔷痴及局外。',
        '妙玉：纵有千年铁门槛，终须一个土馒头。',

        // ——— 其他 ———
        '不在梅边在柳边。',
        '玉在匮中求善价，钗于奁内待时飞。',
        '天不拘兮地不羁，心头无喜亦无悲。',
        '你方唱罢我登场，反认他乡是故乡。',
        '甚荒唐，到头来都是为他人作嫁衣裳。',
        '乱哄哄，你方唱罢我登场。',
        '因嫌纱帽小，致使锁枷扛。',
        '昨怜破袄寒，今嫌紫蟒长。',
        '训有方，保不定日后作强梁。',
        '择膏粱，谁承望流落在烟花巷。',
        '正叹他人命不长，那知自己归来丧。',
    ];

    const quoteEl = document.getElementById('quote-text');
    let quoteIdx = 0;
    let quoteTimer = null;

    // 手机端只选短名言（≤20字）
    var _mobileQuotes = window.innerWidth <= 768
        ? QUOTES.filter(function(q) { return q.length <= 20; })
        : QUOTES;

    function showNextQuote() {
        if (!quoteEl) return;
        const next = _mobileQuotes[quoteIdx % _mobileQuotes.length];
        quoteIdx++;
        quoteEl.textContent = next;
        quoteEl.style.opacity = 1;
    }

    function fadeOutQuote() {
        if (!quoteEl) return;
        quoteEl.style.opacity = 0;
        setTimeout(showNextQuote, 600);
    }

    if (quoteEl && _mobileQuotes.length > 0) {
        showNextQuote();
        quoteTimer = setInterval(fadeOutQuote, 5000);
    }

    // Expose chat functions globally for onclick handlers in dynamic UI
    window.sendChatMessage = sendChatMessage;
    window.cancelAiChat = cancelAiChat;
    window.doAiChat = doAiChat;
    window.addChatBubble = addChatBubble;
    // Sidebar: collapsed in HTML, attach ☰ toggle
    (function() {
        var sidebar = document.getElementById('index-sidebar');
        var main = document.querySelector('.main');
        var navToggle = document.getElementById('sidebar-toggle-btn');
        if (!sidebar) return;

        if (navToggle) {
            navToggle.addEventListener('click', function(e) {
                e.preventDefault();
                toggleSidebar();
            });
        }
    })();

    // Right-click on sidebar session to rename
    var sidebarSessions = document.getElementById('sidebar-sessions');
    if (sidebarSessions) {
        sidebarSessions.addEventListener('contextmenu', function(e) {
            var item = e.target.closest('.sidebar-session-item');
            if (!item || _batchMode) return;
            e.preventDefault();
            var sid = item.getAttribute('data-sid');
            var titleEl = item.querySelector('.sidebar-session-title');
            var currentTitle = titleEl ? titleEl.textContent.trim() : '';
            startRename(sid, currentTitle);
        });

        // Enter key on selected session to rename
        sidebarSessions.addEventListener('keydown', function(e) {
            if (e.key !== 'Enter') return;
            var item = e.target.closest('.sidebar-session-item');
            if (!item || _batchMode) return;
            // Don't trigger if already renaming or if an input is focused
            if (item.classList.contains('renaming')) return;
            if (e.target.tagName === 'INPUT') return;
            var sid = item.getAttribute('data-sid');
            var titleEl = item.querySelector('.sidebar-session-title');
            var currentTitle = titleEl ? titleEl.textContent.trim() : '';
            startRename(sid, currentTitle);
        });
    }
});

// =======================================================================
// Sidebar: Chat Session Management (global functions for onclick)
// =======================================================================

// Track fetch requests to prevent stale responses from overwriting newer DOM updates
var _sidebarFetchId = 0;
var _batchMode = false;

function loadSessions(skipInitial) {
    var list = document.getElementById('sidebar-sessions');
    if (!list) return;
    var isLoggedIn = document.querySelector('.nav-auth-user') !== null;
    if (!isLoggedIn) {
        list.innerHTML = '<div class="sidebar-empty">请先<a href="/login" style="color:var(--zhusha)">登录</a></div>';
        return;
    }
    var fetchId = ++_sidebarFetchId;
    if (!skipInitial) {
        list.innerHTML = '<div class="sidebar-empty">暂无对话</div>';
    }
    fetch('/api/chat/sessions')
        .then(function(r) {
            if (r.redirected || !r.ok) {
                if (fetchId === _sidebarFetchId) {
                    list.innerHTML = '<div class="sidebar-empty">请先<a href="/login" style="color:var(--zhusha)">登录</a></div>';
                }
                return null;
            }
            return r.json();
        })
        .then(function(data) {
            if (!data || fetchId !== _sidebarFetchId) return;
            if (!data.sessions || data.sessions.length === 0) {
                if (!skipInitial) {
                    list.innerHTML = '<div class="sidebar-empty">暂无对话</div>';
                }
                return;
            }
            var html = '';
            data.sessions.forEach(function(s) {
                var active = (s.id === window._chatSessionId) ? ' active' : '';
                var cbHtml = _batchMode ? '<input type="checkbox" class="sidebar-session-cb" data-sid="' + s.id + '" onchange="updateBatchBar()">' : '';
                var delHtml = _batchMode ? '' : '<button class="sidebar-session-del" onclick="event.stopPropagation();deleteSession(\'' + s.id + '\')" title="删除">✕</button>';
                var titleClick = _batchMode ? '' : 'switchSession(\'' + s.id + '\')';
                html += '<div class="sidebar-session-item' + active + '" data-sid="' + s.id + '" tabindex="0">'
                    + cbHtml
                    + '<span class="sidebar-session-title"' + (titleClick ? ' onclick="' + titleClick + '"' : '') + '>' + escapeHtml(s.title) + '</span>'
                    + '<span class="sidebar-session-rename"><input type="text" value="' + escapeHtml(s.title) + '" onblur="var v=this.value.trim();if(v)fetch(\'/api/chat/sessions/' + s.id + '\',{method:\'PATCH\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({title:v})}).then(function(){loadSessions()});else loadSessions();" onkeydown="if(event.key===\'Enter\')this.blur();"></span>'
                    + delHtml
                    + '</div>';
            });
            if (fetchId === _sidebarFetchId) {
                list.innerHTML = html;
            }
        })
        .catch(function() {});
}

function newChatSession() {
    var defaultName = '新对话 ' + new Date().toLocaleString('zh-CN', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'});
    // Bump fetchId to invalidate any in-flight loadSessions from toggleSidebar
    _sidebarFetchId++;
    fetch('/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: defaultName }),
    })
    .then(function(r) {
        if (r.redirected || !r.ok) { window.location.href = '/login'; return null; }
        return r.json();
    })
    .then(function(data) {
        if (!data || !data.session_id) return;
        window._chatSessionId = data.session_id;
        localStorage.setItem('hlm_chat_session', data.session_id);
        window._chatMessages = [];
        // Clear chat area and show welcome
        var chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
            addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
        }
        // Load all sessions from server (this includes the new one we just created)
        loadSessions(true);
        // Focus rename input by polling for the session element via data-sid (more robust than .active class)
        var sid = String(data.session_id);
        var focusTimer = setInterval(function() {
            var items = document.querySelectorAll('.sidebar-session-item');
            for (var i = 0; i < items.length; i++) {
                if (items[i].getAttribute('data-sid') === sid) {
                    clearInterval(focusTimer);
                    items[i].classList.add('renaming');
                    var inp = items[i].querySelector('.sidebar-session-rename input');
                    if (inp) { inp.focus(); inp.select(); }
                    break;
                }
            }
        }, 100);
        // Safety: stop polling after 15 seconds
        setTimeout(function() { clearInterval(focusTimer); }, 15000);
    })
    .catch(function(){
        window.location.href = '/login';
    });
}

function switchSession(sid) {
    if (sid === window._chatSessionId && document.getElementById('chat-messages')) return;
    window._chatSessionId = sid;
    localStorage.setItem('hlm_chat_session', sid);
    // Ensure the chat UI container exists (in case page was refreshed outside AI mode)
    ensureChatContainer();
    var chatMessages = document.getElementById('chat-messages');
    // Show loading indicator while fetching
    if (chatMessages) chatMessages.innerHTML = '<div class="chat-bubble chat-bubble-ai" style="text-align:center;color:var(--mo-muted);">加载中……</div>';
    fetch('/api/chat/sessions/' + encodeURIComponent(sid) + '/messages')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            window._chatMessages = data.messages || [];
            if (chatMessages) {
                chatMessages.innerHTML = '';
                (data.messages || []).forEach(function(m) {
                    addChatBubble(m.role, m.content);
                });
                if (!data.messages || data.messages.length === 0) {
                    addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
                }
            }
            loadSessions();
        })
        .catch(function(){
            if (chatMessages) chatMessages.innerHTML = '';
        });
}

function startRename(sid, currentTitle) {
    var items = document.querySelectorAll('.sidebar-session-item');
    items.forEach(function(item) {
        if (item.dataset.sid === sid) {
            item.classList.add('renaming');
            var inp = item.querySelector('.sidebar-session-rename input');
            if (inp) {
                inp.value = currentTitle;
                inp.focus();
                inp.select();
            }
        } else {
            item.classList.remove('renaming');
        }
    });
}

function deleteSession(sid) {
    if (!confirm('确定删除此对话？')) return;
    fetch('/api/chat/sessions/' + encodeURIComponent(sid), { method: 'DELETE' })
        .then(function() {
            if (window._chatSessionId === sid) {
                window._chatSessionId = '';
                localStorage.removeItem('hlm_chat_session');
                window._chatMessages = [];
                var chatMessages = document.getElementById('chat-messages');
                if (chatMessages) {
                    chatMessages.innerHTML = '';
                    addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
                }
            }
            loadSessions();
        })
        .catch(function(){});
}

// -- Batch delete mode --
function toggleBatchMode() {
    _batchMode = !_batchMode;
    // Update header UI
    var header = document.querySelector('.sidebar-header-top');
    if (header) {
        if (_batchMode) {
            header.innerHTML = '<span class="sidebar-title" style="flex:1;font-family:var(--font-heading);font-size:0.95rem;color:inherit;">选择对话</span>'
                + '<button class="sidebar-manage-btn" onclick="toggleBatchMode()" style="background:var(--zhusha);color:white;border:none;border-radius:3px;padding:2px 8px;cursor:pointer;font-size:0.8rem;">完成</button>'
                + '<button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="收起边栏">◀</button>';
        } else {
            header.innerHTML = '<span class="sidebar-title" style="flex:1;font-family:var(--font-heading);font-size:0.95rem;color:var(--mo);font-weight:600;">对话历史</span>'
                + '<button class="sidebar-new-btn" onclick="newChatSession()" title="新对话" id="sidebar-new-btn" style="background:var(--zhusha);color:white;border:none;border-radius:3px;width:24px;height:24px;font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;">+</button>'
                + '<button class="sidebar-manage-btn" onclick="toggleBatchMode()" title="批量管理" style="background:none;border:1px solid var(--border);border-radius:3px;cursor:pointer;padding:2px 6px;font-size:0.8rem;color:var(--mo-muted);">管理</button>'
                + '<button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="收起边栏">◀</button>';
        }
    }
    // Show/hide batch bar
    var bar = document.getElementById('sidebar-batch-bar');
    if (bar) bar.style.display = _batchMode ? 'flex' : 'none';
    loadSessions();
    if (!_batchMode) {
        // Reset batch bar count
        var label = document.getElementById('batch-count-label');
        if (label) label.textContent = '0';
    }
}

function updateBatchBar() {
    var checked = document.querySelectorAll('.sidebar-session-cb:checked');
    var label = document.getElementById('batch-count-label');
    if (label) label.textContent = checked.length;
    var btn = document.getElementById('batch-delete-btn');
    if (btn) btn.disabled = checked.length === 0;
}

function toggleSelectAll() {
    var checked = document.getElementById('batch-select-all') && document.getElementById('batch-select-all').checked;
    document.querySelectorAll('.sidebar-session-cb').forEach(function(cb) {
        cb.checked = checked;
    });
    updateBatchBar();
}

function deleteSelected() {
    var checked = document.querySelectorAll('.sidebar-session-cb:checked');
    if (checked.length === 0) return;
    if (!confirm('确定删除选中的 ' + checked.length + ' 个对话？此操作不可恢复。')) return;
    var ids = [];
    checked.forEach(function(cb) { ids.push(cb.dataset.sid); });
    _sidebarFetchId++;
    fetch('/api/chat/sessions', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: ids }),
    })
    .then(function(r) { return r.json(); })
    .then(function() {
        // If current session was deleted, clear it
        var currentDeleted = ids.indexOf(window._chatSessionId) !== -1;
        if (currentDeleted) {
            window._chatSessionId = '';
            localStorage.removeItem('hlm_chat_session');
            window._chatMessages = [];
            var chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                chatMessages.innerHTML = '';
                addChatBubble('ai', '您好！我是红楼梦研究助手。您可以问我任何关于《红楼梦》的问题——原著情节、人物分析、版本源流、红学史论争等。我会以学术论文风格回答，并提供详细的文献出处。');
            }
        }
        // Exit batch mode and refresh
        _batchMode = false;
        // Reset header
        var header = document.querySelector('.sidebar-header-top');
        if (header) {
            header.innerHTML = '<span class="sidebar-title" style="flex:1;font-family:var(--font-heading);font-size:0.95rem;color:var(--mo);font-weight:600;">对话历史</span>'
                + '<button class="sidebar-new-btn" onclick="newChatSession()" title="新对话" id="sidebar-new-btn" style="background:var(--zhusha);color:white;border:none;border-radius:3px;width:24px;height:24px;font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;">+</button>'
                + '<button class="sidebar-manage-btn" onclick="toggleBatchMode()" title="批量管理" style="background:none;border:1px solid var(--border);border-radius:3px;cursor:pointer;padding:2px 6px;font-size:0.8rem;color:var(--mo-muted);">管理</button>'
                + '<button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="收起边栏">◀</button>';
        }
        var bar = document.getElementById('sidebar-batch-bar');
        if (bar) bar.style.display = 'none';
        loadSessions();
    })
    .catch(function(){});
}

function toggleSidebar() {
    var sidebar = document.getElementById('index-sidebar');
    var main = document.querySelector('.main');
    if (!sidebar) return;
    var collapsed = sidebar.classList.toggle('collapsed');
    if (main && window.innerWidth > 768) {
        if (collapsed) {
            main.style.paddingLeft = '0';
        } else {
            var w = localStorage.getItem('hlm_sidebar_width');
            main.style.paddingLeft = (w ? parseInt(w, 10) : 300) + 18 + 'px';
        }
    }
    var btn = sidebar.querySelector('.sidebar-toggle-btn');
    if (btn) btn.textContent = collapsed ? '▶' : '◀';
    localStorage.setItem('hlm_sidebar_collapsed', collapsed ? '1' : '');
    // Reset batch mode when closing sidebar
    if (collapsed && _batchMode) {
        _batchMode = false;
        var header = document.querySelector('.sidebar-header-top');
        if (header) {
            header.innerHTML = '<span class="sidebar-title" style="flex:1;font-family:var(--font-heading);font-size:0.95rem;color:var(--mo);font-weight:600;">对话历史</span>'
                + '<button class="sidebar-new-btn" onclick="newChatSession()" title="新对话" id="sidebar-new-btn" style="background:var(--zhusha);color:white;border:none;border-radius:3px;width:24px;height:24px;font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;">+</button>'
                + '<button class="sidebar-manage-btn" onclick="toggleBatchMode()" title="批量管理" style="background:none;border:1px solid var(--border);border-radius:3px;cursor:pointer;padding:2px 6px;font-size:0.8rem;color:var(--mo-muted);">管理</button>'
                + '<button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="收起边栏">◀</button>';
        }
        var bar = document.getElementById('sidebar-batch-bar');
        if (bar) bar.style.display = 'none';
    }
    // Load sessions on first open
    if (!collapsed) {
        var list = document.getElementById('sidebar-sessions');
        if (list && list.children.length === 0) {
            loadSessions();
        }
    }
}

function _addSessionToSidebar(title) {
    var list = document.getElementById('sidebar-sessions');
    if (!list || !window._chatSessionId) {
        loadSessions();
        return;
    }
    // Bump fetchId to prevent stale loadSessions from overwriting
    _sidebarFetchId++;
    // Prepend new session to sidebar directly
    var html = '<div class="sidebar-session-item active" data-sid="' + window._chatSessionId + '" tabindex="0">'
        + '<span class="sidebar-session-title" onclick="switchSession(\'' + window._chatSessionId + '\')">' + escapeHtml(title) + '</span>'
        + '<span class="sidebar-session-rename"><input type="text" value="' + escapeHtml(title) + '" onblur="var v=this.value.trim();if(v)fetch(\'/api/chat/sessions/' + window._chatSessionId + '\',{method:\'PATCH\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({title:v})}).then(function(){loadSessions()});else loadSessions();" onkeydown="if(event.key===\'Enter\')this.blur();"></span>'
        + '<button class="sidebar-session-del" onclick="event.stopPropagation();deleteSession(\'' + window._chatSessionId + '\')" title="删除">✕</button>'
        + '</div>';
    // If the list currently shows empty state, replace it
    var emptyEl = list.querySelector('.sidebar-empty');
    if (emptyEl) {
        list.innerHTML = html;
    } else {
        list.insertAdjacentHTML('afterbegin', html);
    }
}

// --- Sidebar drag-to-resize ---
(function() {
    var handle = document.getElementById('sidebar-handle');
    var sidebar = document.getElementById('index-sidebar');
    var main = document.querySelector('.main');
    if (!handle || !sidebar) return;

    var savedWidth = localStorage.getItem('hlm_sidebar_width');
    if (savedWidth) {
        sidebar.style.width = savedWidth + 'px';
        handle.style.left = savedWidth + 'px';
    }

    var isDragging = false;

    handle.addEventListener('mousedown', function(e) {
        e.preventDefault();
        isDragging = false; // reset; set to true only after a small move
        handle._dragStartX = e.clientX;
        handle.classList.add('active');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function(e) {
        if (!handle._dragStartX) return;
        // Only set isDragging after moving at least 3px (distinguish click from drag)
        if (Math.abs(e.clientX - handle._dragStartX) > 3) {
            isDragging = true;
        }
        if (!isDragging) return;
        var w = Math.max(180, Math.min(500, e.clientX));
        sidebar.style.width = w + 'px';
        handle.style.left = w + 'px';
        if (main) main.style.paddingLeft = (w + 18) + 'px';
    });

    document.addEventListener('mouseup', function() {
        handle._dragStartX = null;
        if (!isDragging) return;
        isDragging = false;
        handle.classList.remove('active');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        var w = parseInt(sidebar.style.width, 10);
        if (w > 0) localStorage.setItem('hlm_sidebar_width', w);
    });

    // Click on handle when sidebar is collapsed → toggle open
    handle.addEventListener('click', function() {
        if (sidebar.classList.contains('collapsed')) {
            toggleSidebar();
        }
    });
})();
