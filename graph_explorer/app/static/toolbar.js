document.addEventListener('DOMContentLoaded', () => {
    // Workspace switching
    function bindWorkspaceChips(){
        document.querySelectorAll('.workspace-chip').forEach(chip =>{
            chip.addEventListener('click', () => {
                document.querySelectorAll('.workspace-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active')
            });
        });
    }
    bindWorkspaceChips();

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