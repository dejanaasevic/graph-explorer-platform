document.addEventListener('DOMContentLoaded', () => {

    function getWorkspaceId() {
        const parts = window.location.pathname.split('/').filter(Boolean);
        const id = parseInt(parts[0], 10);
        return isNaN(id) ? 0 : id;
    }

    // After a redirect the tags HTML is restored from sessionStorage but the
    // remove-btn click listeners are lost (innerHTML doesn't restore handlers).
    // Re-bind them here before anything else runs.
    function bindRemoveButtons() {
        document.querySelectorAll('#query-tags .remove-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.query-tag').remove();
                syncWithBackend();
            });
        });
    }

    const savedTags = sessionStorage.getItem('queryTagsHTML');
    if (savedTags) {
        const qt = document.getElementById('query-tags');
        if (qt) qt.innerHTML = savedTags;
        sessionStorage.removeItem('queryTagsHTML');
        bindRemoveButtons();
    }

    // Workspace switching
    function bindWorkspaceChips(){
        document.querySelectorAll('.workspace-chip').forEach(chip =>{
            chip.addEventListener('click', () => {
                document.querySelectorAll('.workspace-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active')
                window.location.href = window.location.origin + '/workspace/' + chip.getAttribute('data-ws')
            });
        });
    }
    bindWorkspaceChips();

    // Add workspaces
    document.getElementById("add-ws-btn").addEventListener('click', function() {
        var url = new URL(window.location.origin + '/create_workspace')
        fetch(url)
            .then(response => response.json())
            .then(response => {
                var workspaceSpan = document.getElementById("workspace-span")
                var newWorkspaceButton = document.createElement('div')
                newWorkspaceButton.setAttribute('class', 'workspace-chip')
                newWorkspaceButton.setAttribute('data-ws', response.workspace_count - 1)
                newWorkspaceButton.innerText = `WS ${response.workspace_count}`
                newWorkspaceButton.addEventListener('click', function() {
                    document.querySelectorAll('.workspace-chip').forEach(c => c.classList.remove('active'));
                    newWorkspaceButton.classList.add('active')
                    window.location.href = window.location.origin + '/workspace/' + newWorkspaceButton.getAttribute('data-ws')
                })
                workspaceSpan.appendChild(newWorkspaceButton)
            })
    })

    // Filter query tags
    document.getElementById('filter-btn').addEventListener('click', addFilterQueryTag);
    document.getElementById('value-input').addEventListener('keydown', e => {
        if(e.key === 'Enter') addFilterQueryTag();
    });

    function addFilterQueryTag() {
        const attribute = document.getElementById('attribute-input').value.trim();
        const operator = document.getElementById('operator-select').value;
        const value = document.getElementById('value-input').value.trim();
        if(!attribute || !value) return;

        const tag = document.createElement('span');
        tag.className = 'query-tag';
        tag.dataset.type = 'filter';
        tag.dataset.attribute = attribute;
        tag.dataset.operator = operator;
        tag.dataset.value = value;
        tag.innerHTML = `${attribute} ${operator} ${value} <button class="remove-btn">×</button>`;
        tag.querySelector('.remove-btn').addEventListener('click', () => { tag.remove(); syncWithBackend(); });
        document.getElementById('query-tags').appendChild(tag);

        document.getElementById('attribute-input').value = '';
        document.getElementById('value-input').value = '';
        syncWithBackend();
    }

    document.getElementById('clear-btn').addEventListener('click', () => {
        document.getElementById('query-tags').innerHTML = '';
        syncWithBackend();
    });

    // Search query tags
    document.getElementById('search-btn').addEventListener('click', addSearchQueryTag);
    document.getElementById('search-input').addEventListener('keydown', e => {
        if(e.key === 'Enter') addSearchQueryTag();
    });

    function addSearchQueryTag() {
        const value = document.getElementById('search-input').value.trim();
        if(!value) return;

        const tag = document.createElement('span');
        tag.className = 'query-tag';
        tag.dataset.type = 'search';
        tag.dataset.value = value;
        tag.innerHTML = `${value} <button class="remove-btn">×</button>`;
        tag.querySelector('.remove-btn').addEventListener('click', () => { tag.remove(); syncWithBackend(); });

        document.getElementById('query-tags').appendChild(tag);
        document.getElementById('search-input').value = '';
        syncWithBackend();
    }

    function collectQueries() {
        const queries = [];
        document.querySelectorAll('#query-tags .query-tag').forEach(tag => {
            const type = tag.dataset.type;
            if (type === 'search') {
                queries.push({ type: 'search', text: tag.dataset.value });
            } else if (type === 'filter') {
                queries.push({
                    type:      'filter',
                    attribute: tag.dataset.attribute,
                    operator:  tag.dataset.operator,
                    value:     tag.dataset.value,
                });
            }
        });
        return queries;
    }

    async function syncWithBackend() {
        const workspaceId = getWorkspaceId();
        const queries = collectQueries();

        sessionStorage.setItem('queryTagsHTML', document.getElementById('query-tags').innerHTML);

        const res = await fetch(`/${workspaceId}/apply_queries`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ queries }),
        });

        if (!res.ok) {
            sessionStorage.removeItem('queryTagsHTML');
            return;
        }

        window.location.href = `/${workspaceId}/render`;
    }
});