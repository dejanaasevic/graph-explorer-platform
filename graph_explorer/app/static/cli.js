document.addEventListener('DOMContentLoaded', () => {
    const cliInput = document.getElementById('cli-input');
    const cliOutput = document.getElementById('cli-output');

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

     function handleCommand(command) {
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
                appendLine('err', `Unknown command: ${parts[0]}`);
        }
    }
    document.getElementById('cli-run-btn').addEventListener('click', cliRun);
    cliInput.addEventListener('keydown', e => { if (e.key === 'Enter') cliRun(); });
});