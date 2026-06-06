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
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    let aiModeActive = false;

    // --- AI toggle ---
    aiBtn.addEventListener('click', function () {
        aiModeActive = !aiModeActive;
        this.classList.toggle('active', aiModeActive);
        this.textContent = aiModeActive ? '🤖 AI 问答 (开)' : '🤖 AI 问答';
        // Disable mode radios when AI is on
        modeRadios.forEach(r => r.disabled = aiModeActive);

        const q = input.value.trim();
        if (q) doSearch(q);
    });

    // --- URL parameter parsing ---
    const params = new URLSearchParams(window.location.search);
    const urlQuery = params.get('q');
    const urlMode = params.get('mode');
    const urlAi = params.get('ai');

    if (urlAi === '1') {
        aiModeActive = true;
        aiBtn.classList.add('active');
        aiBtn.textContent = '🤖 AI 问答 (开)';
        modeRadios.forEach(r => r.disabled = true);
    }

    if (urlQuery) {
        input.value = urlQuery;
        if (urlMode && !aiModeActive) {
            const radio = document.querySelector(`input[name="mode"][value="${urlMode}"]`);
            if (radio) radio.checked = true;
        }
        doSearch(urlQuery);
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

        doSearch(q);
    });

    // --- Search function ---
    function doSearch(query) {
        if (placeholder) placeholder.style.display = 'none';
        loading.style.display = 'flex';

        if (aiModeActive) {
            doAiSearch(query);
        } else {
            doNormalSearch(query);
        }
    }

    function doNormalSearch(query) {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const topK = topKSelect ? topKSelect.value : 12;
        loadingText.textContent = '搜索中……';
        resultsArea.innerHTML = '';

        fetch(`/api/search?q=${encodeURIComponent(query)}&mode=${mode}&top_k=${topK}`)
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
                            <p class="placeholder-hint">试试其他搜索词或切换搜索模式</p>
                        </div>`;
                    return;
                }

                renderResults(data.results, query);
            })
            .catch(err => {
                loading.style.display = 'none';
                resultsArea.innerHTML = `<div class="error-page"><p>搜索失败: ${err.message}</p></div>`;
            });
    }

    function doAiSearch(query) {
        loadingText.textContent = '正在搜索知识库并生成 AI 回答……';
        resultsArea.innerHTML = '';

        fetch(`/api/ai-search?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                loading.style.display = 'none';

                if (data.error) {
                    resultsArea.innerHTML = `
                        <div class="error-page">
                            <p>${data.error}</p>
                            <p style="margin-top:1rem;font-size:0.85rem;color:var(--text-muted)">
                                请前往 <a href="/settings" style="color:var(--crimson)">AI 设置页面</a> 配置 API
                            </p>
                        </div>`;
                    return;
                }

                renderAiAnswer(data, query);
            })
            .catch(err => {
                loading.style.display = 'none';
                resultsArea.innerHTML = `<div class="error-page"><p>AI 问答失败: ${err.message}</p></div>`;
            });
    }

    function renderAiAnswer(data, query) {
        const sourcesHtml = data.sources && data.sources.length > 0 ? `
            <div class="ai-answer-sources">
                <strong>参考来源：</strong>
                ${data.sources.map(s =>
                    `<a href="/source/${s.source}" target="_blank">${s.source_pretty}</a>`
                ).join(' · ')}
            </div>
        ` : '';

        resultsArea.innerHTML = `
            <div class="results-list" style="max-width:800px">
                <div class="ai-answer-card">
                    <div class="ai-answer-header">🤖 AI 回答 · ${escapeHtml(query)}</div>
                    <div class="ai-answer-body">${escapeHtml(data.answer)}</div>
                    ${sourcesHtml}
                </div>
                <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:1rem">
                    AI 回答基于知识库内容生成，仅供参考。关闭 AI 模式查看原始搜索结果。
                </div>
            </div>
        `;
    }

    // --- Render results ---
    function renderResults(results, query) {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const modeNames = {
            'hybrid': '混合搜索',
            'semantic_only': '语义搜索',
            'keyword_only': '关键词搜索',
        };

        const html = `
            <div class="results-list">
                <div class="results-header">
                    找到 ${results.length} 条结果 · ${modeNames[mode] || mode}
                </div>
                ${results.map(r => renderCard(r, query)).join('')}
            </div>
            <div id="source-sidebar-placeholder"></div>
        `;

        resultsArea.innerHTML = html;
    }

    // --- Render a single result card ---
    function renderCard(r, query) {
        const text = r.text || r.line_text || '';
        const highlighted = highlightText(text, query);
        const source = r.source || '';
        const sourcePretty = r.source_pretty || source.split('/').pop();
        const score = r.score_hybrid !== undefined ? r.score_hybrid.toFixed(3) : '';
        const type = r.type === 'rag' ? '语义' : '关键词';
        const chunkId = r.chunk_id || '';

        const scoresHtml = score ? `
            <span class="result-score">
                相关度 ${score}
                <span class="result-type-badge">${type}</span>
            </span>
        ` : '';

        const expandHtml = chunkId ? `
            <div class="expand-section">
                <button class="expand-btn" data-chunk="${chunkId}">展开上下文</button>
                <div class="expand-content" id="expand-${chunkId.replace(/[.#\/]/g, '-')}"></div>
            </div>
        ` : '';

        return `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-source">
                        <a href="/source/${source}" target="_blank">${sourcePretty}</a>
                    </div>
                    ${scoresHtml}
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
            btn.textContent = '展开上下文';
            return;
        }

        if (contentDiv.dataset.loaded) {
            contentDiv.classList.add('visible');
            btn.textContent = '收起';
            return;
        }

        contentDiv.innerHTML = '<p>加载中……</p>';
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
                contentDiv.innerHTML = '<p>加载失败</p>';
                btn.textContent = '展开上下文';
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
});
