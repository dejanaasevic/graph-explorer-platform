document.addEventListener('DOMContentLoaded', () => {
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
        if(e.key === 'Enter'){
            addFilterQueryTag();
        }
    });

    function addFilterQueryTag() {
        const attribute = document.getElementById('attribute-input').value.trim();
        const operator = document.getElementById('operator-select').value;
        const value = document.getElementById('value-input').value.trim();
        if(!attribute || !value){
            return;
        }
        const tag = document.createElement('span');
        tag.className = 'query-tag';
        tag.innerHTML = `${attribute} ${operator} ${value} <button class="remove-btn">×</button>`;
        tag.querySelector('.remove-btn').addEventListener('click', () => tag.remove());
        document.getElementById('query-tags').appendChild(tag);

        document.getElementById('attribute-input').value = '';
        document.getElementById('value-input').value = '';
    }

    document.getElementById('clear-btn').addEventListener('click', () => {
        document.getElementById('query-tags').innerHTML = '';
    });

     // Search query tags
    document.getElementById('search-btn').addEventListener('click', addSearchQueryTag);
    document.getElementById('search-input').addEventListener('keydown', e => {
        if(e.key === 'Enter'){
            addSearchQueryTag();
        }
    });

   function addSearchQueryTag() {
        const value = document.getElementById('search-input').value.trim();
        if(!value) return;

        const tag = document.createElement('span');
        tag.className = 'query-tag';
        tag.innerHTML = `${value} <button class="remove-btn">×</button>`;
        tag.querySelector('.remove-btn').addEventListener('click', () => tag.remove());

        const queryTags = document.getElementById('query-tags');
        queryTags.appendChild(tag);
        document.getElementById('search-input').value = '';
    }
});