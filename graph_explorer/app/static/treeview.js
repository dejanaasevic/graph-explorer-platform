(function () {

    /** Build adjacency list: nodeId → [nodeId, ...] from the global `edges` array. */
    function buildAdjacency(edgesArr) {
        var adj = {};
        Object.keys(nodes).forEach(function (id) { adj[id] = []; });
        edgesArr.forEach(function (edge) {
            var srcId = typeof edge.source === 'object' ? edge.source.id : edge.source;
            var tgtId = typeof edge.target === 'object' ? edge.target.id : edge.target;
            if (srcId && tgtId) {
                if (!adj[srcId]) adj[srcId] = [];
                adj[srcId].push(tgtId);
            }
        });
        return adj;
    }

    /** Pick root = node with no incoming edges (or first node as fallback). */
    function pickRoot(nodeIds, edgesArr) {
        var hasIncoming = {};
        edgesArr.forEach(function (edge) {
            var tgtId = typeof edge.target === 'object' ? edge.target.id : edge.target;
            if (tgtId) hasIncoming[tgtId] = true;
        });
        for (var i = 0; i < nodeIds.length; i++) {
            if (!hasIncoming[nodeIds[i]]) return nodeIds[i];
        }
        return nodeIds[0];
    }

    /** D3-force keys we don't want to display as attributes. */
    var D3_KEYS = new Set(['index', 'weight', 'x', 'y', 'px', 'py', 'id', 'label']);

    /** Render attribute rows for a node (non-D3 keys). */
    function renderAttributes(nodeData) {
        var html = '';
        Object.keys(nodeData).forEach(function (key) {
            if (D3_KEYS.has(key)) return;
            html += '<div class="tree-field">' + key + ': <span>' + nodeData[key] + '</span></div>';
        });
        return html;
    }

    /**
     * Recursively build HTML for a tree node.
     * visited  – Set of ids already on the current path (cycle detection).
     * expanded – Set of ids that are currently open.
     */
    function renderNode(nodeId, adj, visited, expanded) {
        var nodeData = nodes[nodeId];
        if (!nodeData) return '';

        var label = nodeData.label || nodeData.name || nodeData.id || nodeId;
        var children = adj[nodeId] || [];
        var hasChildren = children.length > 0;

        // Cycle: this node is already an ancestor on the path
        var isCycle = visited.has(nodeId);
        var isExpanded = expanded.has(nodeId);

        var toggleIcon = '';
        if (hasChildren && !isCycle) {
            toggleIcon = '<span class="tree-toggle">' + (isExpanded ? '−' : '+') + '</span>';
        } else {
            toggleIcon = '<span class="tree-toggle-placeholder"></span>';
        }

        var cycleLabel = isCycle ? ' <em style="color:var(--err);font-size:10px;">[cycle]</em>' : '';

        var html = '<div class="tree-node" data-node-id="' + nodeId + '">';
        html += '<div class="tree-node-header" data-node-id="' + nodeId + '">';
        html += toggleIcon;
        html += '<span class="tree-node-label">' + label + '</span>';
        html += cycleLabel;
        html += '</div>';

        // Attribute fields (always visible when parent is expanded)
        html += '<div class="tree-node-attrs" style="' + (isExpanded ? '' : 'display:none') + '">';
        html += renderAttributes(nodeData);
        html += '</div>';

        // Children container
        if (hasChildren && !isCycle && isExpanded) {
            html += '<div class="tree-node-children">';
            var newVisited = new Set(visited);
            newVisited.add(nodeId);
            children.forEach(function (childId) {
                html += renderNode(childId, adj, newVisited, expanded);
            });
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    function buildTree() {
        if (typeof nodes === 'undefined' || typeof edges === 'undefined') return;

        var nodeIds = Object.keys(nodes);
        if (nodeIds.length === 0) return;

        var adj = buildAdjacency(edges);
        var rootId = pickRoot(nodeIds, edges);

        // Start with root expanded
        var expanded = new Set([rootId]);

        var container = document.getElementById('tree-view-content');
        if (!container) return;

        container.innerHTML = renderNode(rootId, adj, new Set(), expanded);

        // Store state on container for use in later commits
        container._treeState = { adj: adj, rootId: rootId, expanded: expanded };
    }

    // Expose so later commits can call rebuild
    window._treeViewBuild = buildTree;


    var initDone = false;

    function maybeInit() {
        if (initDone) return;
        if (typeof nodes !== 'undefined' && Object.keys(nodes).length > 0) {
            initDone = true;
            buildTree();
        }
    }

    var observer = new MutationObserver(function () {
        maybeInit();
    });
    observer.observe(document.getElementById('graph'), {
        subtree: true,
        attributes: true,
        attributeFilter: ['transform']
    });

    // Also try immediately in case graph is already rendered
    document.addEventListener('DOMContentLoaded', maybeInit);

    // Re-build on graph reset
    GraphEvents.subscribe('graph:reset', function () {
        initDone = false;
        var container = document.getElementById('tree-view-content');
        if (container) container.innerHTML = '';
    });

})();