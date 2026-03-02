(function () {
    let state = { translate: [0, 0], scale: 1 };
    let initialized = false;
    let currentVB = { x: 0, y: 0, w: 480, h: 270 };

    function getNodeData() {
        const data = [];
        document.querySelectorAll('#graph .node').forEach(function (n) {
            const t = n.getAttribute('transform');
            const m = t && t.match(/translate\(([^,]+),([^)]+)\)/);
            if (!m) return;
            data.push({ x: parseFloat(m[1]), y: parseFloat(m[2]) });
        });
        return data;
    }

    function computeViewBox(nodes) {
        if (nodes.length === 0) return currentVB;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        nodes.forEach(function (n) {
            minX = Math.min(minX, n.x);
            minY = Math.min(minY, n.y);
            maxX = Math.max(maxX, n.x);
            maxY = Math.max(maxY, n.y);
        });
        const pad = 40;
        return { x: minX - pad, y: minY - pad, w: (maxX - minX) + 2 * pad, h: (maxY - minY) + 2 * pad };
    }

    // Undo zoom and pan to keep the graph unscaled and unshifted
    function updateWrapper() {
        const tx = state.translate[0];
        const ty = state.translate[1];
        const s = state.scale;
        d3.select('#bird-graph-wrapper')
            .attr('transform', 'scale(' + (1 / s) + ') translate(' + (-tx) + ',' + (-ty) + ')');
    }

    function updateViewport() {
        const mainSVG = document.getElementById('main-svg');
        const tx = state.translate[0];
        const ty = state.translate[1];
        const s = state.scale;
        d3.select('#bird-viewport')
            .attr('x', -tx / s)
            .attr('y', -ty / s)
            .attr('width', mainSVG.clientWidth / s)
            .attr('height', mainSVG.clientHeight / s);
    }

    function init() {
        initialized = true;
        const bird = d3.select('#bird-svg');
        bird.selectAll('*').remove();
        bird.attr('preserveAspectRatio', 'xMidYMid meet');

        // Mirror whatever is in #graph using <use>
        bird.append('g')
            .attr('id', 'bird-graph-wrapper')
            .attr('pointer-events', 'none') // so clicks pass through to bird-svg handler
            .append('use')
            .attr('xlink:href', '#graph');

        // Viewport rect
        bird.append('rect')
            .attr('class', 'viewport-rect')
            .attr('id', 'bird-viewport')
            .attr('stroke-width', 4)
            .attr('vector-effect', 'non-scaling-stroke');

        // Drag viewport to pan main view
        d3.select('#bird-viewport').call(
            d3.behavior.drag().on('drag', function () {
                state.translate[0] -= d3.event.dx * state.scale;
                state.translate[1] -= d3.event.dy * state.scale;
                window._mainZoom.translate(state.translate.slice());
                d3.select('#graph').attr('transform',
                    'translate(' + state.translate + ') scale(' + state.scale + ')');
                updateWrapper();
                updateViewport();
            })
        );

        // Click outside viewport to center main view on that point
        bird.on('click', function () {
            if (d3.event.target.id === 'bird-viewport') return;
            const pos = d3.mouse(this); // graph-space coords via viewBox
            const mainSVG = document.getElementById('main-svg');
            state.translate[0] = mainSVG.clientWidth / 2 - pos[0] * state.scale;
            state.translate[1] = mainSVG.clientHeight / 2 - pos[1] * state.scale;
            window._mainZoom.translate(state.translate.slice());
            d3.select('#graph').attr('transform',
                'translate(' + state.translate + ') scale(' + state.scale + ')');
            updateWrapper();
            updateViewport();
        });

        update();
    }

    function maybeInit() {
        if (!initialized && document.querySelectorAll('#graph .node').length > 0) {
            init();
        }
    }

    function update() {
        const nodes = getNodeData();
        currentVB = computeViewBox(nodes);
        d3.select('#bird-svg').attr('viewBox',
            currentVB.x + ' ' + currentVB.y + ' ' + currentVB.w + ' ' + currentVB.h);
        updateWrapper();
        updateViewport();
    }

    // Watch #graph for transform changes (node position updates from any visualizer)
    let updatePending = false;
    const observer = new MutationObserver(function () {
        if (updatePending) return;
        updatePending = true;
        requestAnimationFrame(function () {
            updatePending = false;
            maybeInit();
            update();
        });
    });
    observer.observe(document.getElementById('graph'), {
        subtree: true,
        attributes: true,
        attributeFilter: ['transform']
    });

    GraphEvents.subscribe('graph:zoom', function (data) {
        state.translate = data.translate;
        state.scale = data.scale;
        updateWrapper();
        updateViewport();
    });

    GraphEvents.subscribe('graph:reset', function () {
        initialized = false;
        d3.select('#bird-svg').selectAll('*').remove();
    });
})();