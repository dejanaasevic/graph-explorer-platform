document.addEventListener('DOMContentLoaded', () => {

    // zoom and pan functionality
    const svg = d3.select('#main-svg');
    const graph = d3.select('#graph');

    const zoom = d3.behavior.zoom().scaleExtent([0.1, 10]).on('zoom', function () {
            graph.attr('transform', 'translate(' + d3.event.translate + ') scale(' + d3.event.scale + ')');
    });
    svg.call(zoom);

    // prevent zoom and pan while dragging and dropping node
    svg.selectAll('.node').on('mousedown.zoom', null);
});