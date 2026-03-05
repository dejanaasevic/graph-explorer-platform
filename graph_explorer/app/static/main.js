document.addEventListener('DOMContentLoaded', () => {

    // zoom and pan functionality
    const svg = d3.select('#main-svg');
    const graph = d3.select('#graph');

    const zoom = d3.behavior.zoom().scaleExtent([0.1, 10]).on('zoom', function () {
            graph.attr('transform', 'translate(' + d3.event.translate + ') scale(' + d3.event.scale + ')');
            GraphEvents.publish('graph:zoom', {
                translate: d3.event.translate.slice(),
                scale: d3.event.scale
            });
    });
    svg.call(zoom);
    window._mainZoom = zoom;

    // prevent zoom and pan while dragging and dropping node
    svg.selectAll('.node').on('mousedown.zoom', null);

    // data source and visualizer selection logic
    const selectDS = document.getElementById('data-format-select');
    const selectVis = document.getElementById('visualizer-select');
    const currentURL = new URL(window.location.href)
    const workspace_id = currentURL.pathname.split('/').at(1)

    if(currentURL.searchParams.get("datasource")){
        selectDS.value = currentURL.searchParams.get("datasource")
    }

    selectDS.addEventListener('change', function() {
        var source = this.value;
        var url = new URL(currentURL.origin + '/' + workspace_id)
        console.log(url.toString())
        url.searchParams.set("datasource", this.value)
        if (source) {
            window.location.href = url.href;
        }
    });

    selectVis.addEventListener('change', function() {
        var visualizer = this.value;
        var url = new URL(currentURL.origin + '/' + workspace_id + '/select_vis')
        console.log(URL)
        url.searchParams.set("visualizer", visualizer)
        fetch(url).then(response => console.log(response));
        GraphEvents.publish('graph:reset', {});
    });

    // Node selection with mouseup and position check to bypass D3 drag click suppression.
    let mouseDownInfo = null;
    const graphEl = document.getElementById('graph');

    graphEl.addEventListener('mousedown', function (e) {
        const nodeEl = e.target.closest('.node');
        mouseDownInfo = nodeEl ? { node: nodeEl, x: e.clientX, y: e.clientY } : null;
    }, true); // capture phase — fires before D3 drag stops propagation

    document.addEventListener('mouseup', function (e) {
        if (!mouseDownInfo) return;
        const { node, x, y } = mouseDownInfo;
        mouseDownInfo = null;

        const dx = Math.abs(e.clientX - x);
        const dy = Math.abs(e.clientY - y);
        if (dx > 5 || dy > 5) return; // drag, not a click

        const wasSelected = node.classList.contains('selected');
        document.querySelectorAll('#graph .node').forEach(n => n.classList.remove('selected'));
        if (!wasSelected) node.classList.add('selected');

        var nodeId = null;
        node.classList.forEach(function (c) {
            if (c !== 'node' && c !== 'selected') {
                nodeId = c.replace(/^id/, '');
            }
        });

        GraphEvents.publish('node:selected', {el: node, id: nodeId, selected: !wasSelected});
    });

    // Tree View → Main View
    // When a node is selected in Tree View, highlight it and pan Main View to centre on it.
    GraphEvents.subscribe('node:selected', function(data) {
        if (data.source !== 'tree') return;

        var nodeId = data.id;
        if (!nodeId) return;

        document.querySelectorAll('#graph .node').forEach(function(n) {
            n.classList.remove('selected');
        });

        var nodeEl = document.querySelector('#graph .node[class*="' + nodeId + '"]');
        if (!nodeEl && nodes[nodeId] && nodes[nodeId].id) {
            var xmlId = String(nodes[nodeId].id);
            nodeEl = document.querySelector('#graph .node[class*="' + xmlId + '"]');
        }

        if (!nodeEl) return;
        nodeEl.classList.add('selected');

        // Pan Main View to centre on the selected node.
        var transform = nodeEl.getAttribute('transform');
        var match = transform && transform.match(/translate\(([^,]+),([^)]+)\)/);
        if (!match) return;

        var nodeX = parseFloat(match[1]);
        var nodeY = parseFloat(match[2]);

        var mainSVG = document.getElementById('main-svg');
        var scale = window._mainZoom.scale();
        var newTx = mainSVG.clientWidth  / 2 - nodeX * scale;
        var newTy = mainSVG.clientHeight / 2 - nodeY * scale;

        window._mainZoom.translate([newTx, newTy]);
        d3.select('#graph').attr('transform',
            'translate(' + newTx + ',' + newTy + ') scale(' + scale + ')');

        // Notify Bird View and any other listeners of the new pan position
        GraphEvents.publish('graph:zoom', {
            translate: [newTx, newTy],
            scale: scale
        });

    });
    // Handled on mouseup, keep empty to prevent double toggle
    window.nodeClick = function (el) {};
});