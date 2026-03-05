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

    function updateView(args, response) {
        switch (args[0]){
            case 'create-node':
                appendLine("ok", "Created node!")
                let new_node = JSON.parse(response)
                nodes[new_node.id] = new_node
                render()
                break;
            case 'create-edge':
                appendLine("ok", "Created edge!")
                let new_edge = JSON.parse(response)
                edges.append(new_edge)
                render()
                break;
            case 'update-node':
                appendLine("ok", "Updated node!")
                let updated_node = JSON.parse(response)
                nodes[updated_node.id] = updated_node
                render()
                break;
            case 'update-edge':
                appendLine("ok", "Updated edge!")
                let updated_edge = JSON.parse(response)
                // edge updating
                break;
            case 'delete-node':
                appendLine("ok", "Deleted node!")
                delete nodes[args[1]]
                break;
            case 'delete-edge':
                appendLine("ok", "Deleted edge!")
                for (let i in edges){
                    if (edges[i].source === args[1] && edges[i].target === args[2]){
                        edges.splice(i, 1)
                        break;
                    }
                }
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
                cliInput.value = '' ? commandCounter === commandStack.length : commandStack[commandCounter]
        }
    });
});