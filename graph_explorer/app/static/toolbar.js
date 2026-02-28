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
});
