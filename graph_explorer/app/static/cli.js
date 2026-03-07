import {addSearchQueryTag, addFilterQueryTag} from "./toolbar.js";

document.addEventListener('DOMContentLoaded', () => {
    const cliInput = document.getElementById('cli-input');
    const cliOutput = document.getElementById('cli-output');
    let commandStack = []
    let commandCounter = 0

    function cliRun() {
        const command = cliInput.value.trim();
        if(!command){
            return;
        }
        appendLine('cmd', '> ' + command);
        cliInput.value = '';
        handleCommand(command);
    }

     function appendLine(type, text) {
        const line = document.createElement('div');
        line.className = 'cli-line ' + type;
        line.textContent = text;
        cliOutput.appendChild(line);
        cliOutput.scrollTop = cliOutput.scrollHeight;
     }

     function fetchCommand(command) {
        const currentURL = new URL(window.location.href);
        const workspace_id = currentURL.pathname.split('/').at(1);
        const cliEndpoint = new URL(currentURL.origin + '/' + workspace_id + '/cli');
        cliEndpoint.searchParams.append('command', command);
        return fetch(cliEndpoint)
     }

     function handleCommand(command) {
        commandStack.push(command);
        commandCounter = commandStack.length
        const parts = command.trim().split(/\s+/);
        switch (parts[0]) {
            case 'clear':
                cliOutput.innerHTML = '';
                break;
            case 'help':
                // TODO: add other command patterns
                appendLine('ok', 'Commands: clear, help');
                break;
            default:
                fetchCommand(command).then(response => {
                    if(response.ok){
                        response.text().then(response => updateView(parts, response))
                    } else {
                        response.text().then(response => appendLine("err", response))
                    }
            })
        }
    }

    function renderUpdate(){
        render()
        GraphEvents.publish('graph:updated')
    }

    function updateView(args, response) {
        switch (args[0]){
            case 'create-node':
                appendLine("ok", "Created node!")
                let new_node = JSON.parse(response)
                nodes[new_node.id] = new_node
                renderUpdate()
                break;
            case 'create-edge':
                appendLine("ok", "Created edge!")
                let new_edge = JSON.parse(response)
                new_edge.source = nodes[new_edge.source]
                new_edge.target = nodes[new_edge.target]
                edges.push(new_edge)
                renderUpdate()
                break;
            case 'update-node':
                appendLine("ok", "Updated node!")
                let updated_node = JSON.parse(response)
                Object.assign(nodes[updated_node.id], updated_node)
                renderUpdate()
                break;
            case 'update-edge':
                appendLine("ok", "Updated edge!")
                let updated_edge = JSON.parse(response)
                for (let i in edges) {
                    if (edges[i].source.id === updated_edge.source && edges[i].target.id === updated_edge.target) {
                        edges[i].source = nodes[updated_edge.source]
                        edges[i].target = nodes[updated_edge.target]
                        Object.assign(edges[i], updated_edge)
                        break;
                    }
                }
                renderUpdate()
                break;
            case 'delete-node':
                appendLine("ok", "Deleted node!")
                let id = args[1]
                for (let i = edges.length - 1; i >= 0; i--) {
                    if (edges[i].source.id === id || edges[i].target.id === id) {
                        edges.splice(i, 1)
                    }
                }
                delete nodes[id]
                renderUpdate()
                break;
            case 'delete-edge':
                appendLine("ok", "Deleted edge!")
                for (let i in edges){
                    if (edges[i].source === nodes[args[1]] && edges[i].target === nodes[args[2]]){
                        edges.splice(i, 1)
                        break;
                    }
                }
                renderUpdate()
                break;
            case 'search':
                appendLine("ok", "Search query applied!")
                addSearchQueryTag(args[1])
            case 'filter':
                appendLine("ok", "Filter query applied!")
                addFilterQueryTag(args[1], args[2], args[3])
                break;
        }
    }

    document.getElementById('cli-run-btn').addEventListener('click', cliRun);
    cliInput.addEventListener('keydown', e => {
        switch(e.key) {
            case 'Enter':
                cliRun()
                break;
            case 'ArrowUp':
                commandCounter = Math.max(0, commandCounter - 1);
                cliInput.value = commandStack[commandCounter];
                break;
            case 'ArrowDown':
                commandCounter = Math.min(commandStack.length, commandCounter + 1)
                cliInput.value = commandStack[commandCounter] ? commandStack[commandCounter] : ''
        }
    });
});