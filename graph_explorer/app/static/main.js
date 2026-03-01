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
    console.log(workspace_id)

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

    window.nodeClick = function(el) {
        const wasSelected = el.classList.contains('selected');
        document.querySelectorAll('#graph .node').forEach(n => n.classList.remove('selected'));
        if (!wasSelected) el.classList.add('selected');
        GraphEvents.publish('node:selected', { el: el, selected: !wasSelected });
    };
});