with open('/opt/hongloumeng/app/static/script.js') as f:
    js = f.read()

old = '''function toggleSidebar() {
    var sidebar = document.getElementById('index-sidebar');
    var main = document.querySelector('.main');
    if (!sidebar) return;
    var collapsed = sidebar.classList.toggle('collapsed');
    if (main) main.classList.toggle('sidebar-collapsed', collapsed);
    var btn = sidebar.querySelector('.sidebar-toggle-btn');
    if (btn) btn.textContent = collapsed ? '▶' : '◀';
    localStorage.setItem('hlm_sidebar_collapsed', collapsed ? '1' : '');
}'''

new = '''function toggleSidebar() {
    var sidebar = document.getElementById('index-sidebar');
    var main = document.querySelector('.main');
    if (!sidebar) return;
    var collapsed = sidebar.classList.toggle('collapsed');
    if (main) {
        main.classList.toggle('sidebar-collapsed', collapsed);
        if (!collapsed) {
            var w = localStorage.getItem('hlm_sidebar_width');
            if (w) {
                main.style.paddingLeft = (parseInt(w, 10) + 18) + 'px';
            }
        }
    }
    var btn = sidebar.querySelector('.sidebar-toggle-btn');
    if (btn) btn.textContent = collapsed ? '▶' : '◀';
    localStorage.setItem('hlm_sidebar_collapsed', collapsed ? '1' : '');
}'''

if old in js:
    js = js.replace(old, new)
    with open('/opt/hongloumeng/app/static/script.js', 'w') as f:
        f.write(js)
    print('DONE')
else:
    print('ERROR: old not found')
