(function () {

    // Builds an adjacency list from edges
    function buildAdjacency(edgesArr) {
        var adj = {};
        Object.keys(nodes).forEach(function (id) { adj[id] = []; });

        var xmlIdToUuid = {};
        Object.keys(nodes).forEach(function (uuidKey) {
            var n = nodes[uuidKey];
            if (n.id) {
                xmlIdToUuid[String(n.id)] = uuidKey;
            }
        });

        // Resolves a raw edge endpoint (UUID string or node object) to an internal UUID key
        function resolveId(raw) {
            var s = String(raw);
            if (nodes[s] !== undefined) return s;
            if (xmlIdToUuid[s] !== undefined) return xmlIdToUuid[s];
            return null;
        }

        edgesArr.forEach(function (edge) {
            var srcRaw = typeof edge.source === 'object' ? edge.source.id : edge.source;
            var tgtRaw = typeof edge.target === 'object' ? edge.target.id : edge.target;

            var srcId = resolveId(srcRaw);
            var tgtId = resolveId(tgtRaw);

            if (srcId && tgtId) {
                if (!adj[srcId]) adj[srcId] = [];
                adj[srcId].push(tgtId);
            }
        });
        return adj;
    }

    // Picks the root node: prefers a node with no incoming edges (true root).
    // Falls back to the first node if the graph is fully cyclic.
    function pickRoot(nodeIds, edgesArr) {
        var hasIncoming = {};
        edgesArr.forEach(function (edge) {
            var tgtRaw = typeof edge.target === 'object' ? edge.target.id : edge.target;
            if (tgtRaw) hasIncoming[String(tgtRaw)] = true;
        });
        for (var i = 0; i < nodeIds.length; i++) {
            var n = nodes[nodeIds[i]];
            var xmlId = n && n.id ? String(n.id) : nodeIds[i];
            if (!hasIncoming[nodeIds[i]] && !hasIncoming[xmlId]) return nodeIds[i];
        }
        return nodeIds[0];
    }

    // Keys added by D3 force layout — excluded from attribute display
    var D3_KEYS = new Set(['index', 'weight', 'x', 'y', 'px', 'py', 'id', 'label', 'tag']);

    // Renders key-value attribute rows for a node, skipping internal D3 keys
    function renderAttributes(nodeData) {
        var html = '';
        Object.keys(nodeData).forEach(function (key) {
            if (D3_KEYS.has(key)) return;
            html += '<div class="tree-field">' + key + ': <span>' + nodeData[key] + '</span></div>';
        });
        return html;
    }

    // Recursively renders a tree node as HTML.
    // Shows [cycle] and disables expansion when a cycle is detected via `visited`.
    // A node gets a "+" toggle if it has children OR displayable attributes.
    function renderNode(nodeId, adj, visited, expanded) {
        var nodeData = nodes[nodeId];
        if (!nodeData) return '';

        var label = nodeData.label
            || nodeData.full_name
            || nodeData.name
            || nodeData.model
            || nodeData.tag
            || nodeId.substring(0, 8);

        var children = adj[nodeId] || [];
        var isCycle = visited.has(nodeId);
        var isExpanded = expanded.has(nodeId);

        var displayAttrs = Object.keys(nodeData).filter(function(k) {
            return !D3_KEYS.has(k);
        });

        var hasChildren = children.length > 0;
        var hasAttrs = displayAttrs.length > 0;
        // Node is expandable if it has children or attributes, and is not a cycle back-edge
        var canExpand = (hasChildren || hasAttrs) && !isCycle;

        var toggleIcon = '';
        if (canExpand) {
            toggleIcon = '<span class="tree-toggle" data-toggle="' + nodeId + '">' + (isExpanded ? '−' : '+') + '</span>';
        } else {
            toggleIcon = '<span class="tree-toggle-placeholder"></span>';
        }

        var cycleLabel = isCycle ? ' <em style="color:var(--err);font-size:10px;">[↩ cycle]</em>' : '';

        var html = '<div class="tree-node" data-node-id="' + nodeId + '">';
        html += '<div class="tree-node-header" data-node-id="' + nodeId + '">';
        html += toggleIcon;
        html += '<span class="tree-node-label">' + label + '</span>';
        html += cycleLabel;
        html += '</div>';

        html += '<div class="tree-node-attrs" data-attrs-for="' + nodeId + '" style="' + (isExpanded ? '' : 'display:none') + '">';
        html += renderAttributes(nodeData);
        html += '</div>';

        if (hasChildren && !isCycle && isExpanded) {
            html += '<div class="tree-node-children" data-children-for="' + nodeId + '">';
            var newVisited = new Set(visited);
            newVisited.add(nodeId);
            children.forEach(function (childId) {
                html += renderNode(childId, adj, newVisited, expanded);
            });
            html += '</div>';
        } else if (hasChildren && !isCycle && !isExpanded) {
            html += '<div class="tree-node-children" data-children-for="' + nodeId + '" style="display:none"></div>';
        }

        html += '</div>';
        return html;
    }

    // Handles expand/collapse toggle for a node.
    function handleToggle(nodeId, state, nodeElement) {
        var adj = state.adj;
        var expanded = state.expanded;

        var children = adj[nodeId] || [];
        var nodeData = nodes[nodeId];
        var displayAttrs = nodeData ? Object.keys(nodeData).filter(function(k) {
            return !D3_KEYS.has(k);
        }) : [];

        if (children.length === 0 && displayAttrs.length === 0) return;

        var childrenDiv = nodeElement.querySelector('[data-children-for="' + nodeId + '"]');
        var attrsDiv = nodeElement.querySelector('[data-attrs-for="' + nodeId + '"]');
        var toggleBtn = nodeElement.querySelector('[data-toggle="' + nodeId + '"]');

        if (expanded.has(nodeId)) {
            expanded.delete(nodeId);
            if (childrenDiv) childrenDiv.style.display = 'none';
            if (attrsDiv) attrsDiv.style.display = 'none';
            if (toggleBtn) toggleBtn.textContent = '+';
        } else {
            expanded.add(nodeId);
            if (attrsDiv) attrsDiv.style.display = '';
            if (toggleBtn) toggleBtn.textContent = '−';

            if (childrenDiv) {
                childrenDiv.style.display = '';

                if (childrenDiv.children.length === 0) {
                    var visited = new Set();
                    var el = nodeElement;
                    while (el) {
                        var pid = el.getAttribute('data-node-id');
                        if (pid) visited.add(pid);
                        el = el.parentElement.closest('.tree-node');
                    }

                    var html = '';
                    children.forEach(function (childId) {
                        html += renderNode(childId, adj, visited, expanded);
                    });
                    childrenDiv.innerHTML = html;
                }
            }
        }
    }

    // Attaches a single delegated click listener to the tree container.
    function attachClickHandlers(state) {
        var container = document.getElementById('tree-view-content');
        container.addEventListener('click', function (e) {
            var header = e.target.closest('.tree-node-header');
            if (!header) return;
            var nodeId = header.getAttribute('data-node-id');
            if (!nodeId) return;
            var nodeElement = header.closest('.tree-node');
            handleToggle(nodeId, state, nodeElement);
            GraphEvents.publish('node:selected', { id: nodeId, source: 'tree' });
        });
    }

    function buildTree() {
        if (typeof nodes === 'undefined' || typeof edges === 'undefined') return;
        var nodeIds = Object.keys(nodes);
        if (nodeIds.length === 0) return;

        var adj = buildAdjacency(edges);
        var rootId = pickRoot(nodeIds, edges);
        var expanded = new Set([rootId]);
        var state = { adj: adj, rootId: rootId, expanded: expanded };

        var container = document.getElementById('tree-view-content');
        if (!container) return;

        container.innerHTML = renderNode(rootId, adj, new Set(), expanded);
        // Store state on the DOM element so subscribers can access it
        container._treeState = state;
        attachClickHandlers(state);
    }

    window._treeViewBuild = buildTree;

    var initDone = false;

    function maybeInit() {
        if (initDone) return;
        if (typeof nodes !== 'undefined' && Object.keys(nodes).length > 0) {
            initDone = true;
            buildTree();
        }
    }

    var observer = new MutationObserver(function () { maybeInit(); });
    observer.observe(document.getElementById('graph'), {
        subtree: true, attributes: true, attributeFilter: ['transform']
    });

    document.addEventListener('DOMContentLoaded', maybeInit);

    GraphEvents.subscribe('graph:reset', function () {
        initDone = false;
        var container = document.getElementById('tree-view-content');
        if (container) container.innerHTML = '';
    });

    // BFS from root to find the path to a target node.
    // Used to open all ancestor nodes when navigating from Main View.
    function findPathToNode(targetUuid, adj, rootId) {
        var queue = [[rootId, [rootId]]];
        var visited = new Set();
        while (queue.length > 0) {
            var current = queue.shift();
            var nodeId = current[0];
            var path = current[1];
            if (nodeId === targetUuid) return path;
            if (visited.has(nodeId)) continue;
            visited.add(nodeId);
            var children = adj[nodeId] || [];
            children.forEach(function(childId) {
                if (!visited.has(childId)) {
                    queue.push([childId, path.concat(childId)]);
                }
            });
        }
        return null;
    }

    // Main View → Tree View
    // When a node is selected in Main View, open all ancestors and scroll to it.
    GraphEvents.subscribe('node:selected', function(data) {
        if (data.source === 'tree') return;

        var nodeId = data.id;
        if (!nodeId) return;

        document.querySelectorAll('#tree-view-content .tree-node-header')
            .forEach(function(h) { h.classList.remove('tree-selected'); });

        var targetUuid = null;
        if (nodes[nodeId]) {
            targetUuid = nodeId;
        } else {
            Object.keys(nodes).forEach(function(uuid) {
                if (String(nodes[uuid].id) === String(nodeId)) targetUuid = uuid;
            });
        }
        if (!targetUuid) return;

        var container = document.getElementById('tree-view-content');
        var state = container._treeState;
        if (!state) return;

        var path = findPathToNode(targetUuid, state.adj, state.rootId);
        if (!path) return;

        // Open each ancestor along the path (excluding the target itself)
        path.slice(0, -1).forEach(function(ancestorId) {
            if (!state.expanded.has(ancestorId)) {
                state.expanded.add(ancestorId);
                var ancestorEl = container.querySelector('.tree-node[data-node-id="' + ancestorId + '"]');
                if (ancestorEl) {
                    var childrenDiv = ancestorEl.querySelector('[data-children-for="' + ancestorId + '"]');
                    var attrsDiv = ancestorEl.querySelector('[data-attrs-for="' + ancestorId + '"]');
                    var toggleBtn = ancestorEl.querySelector('[data-toggle="' + ancestorId + '"]');
                    if (attrsDiv) attrsDiv.style.display = '';
                    if (toggleBtn) toggleBtn.textContent = '−';
                    if (childrenDiv) {
                        childrenDiv.style.display = '';
                        if (childrenDiv.children.length === 0) {
                            var visited = new Set();
                            var el = ancestorEl;
                            while (el) {
                                var pid = el.getAttribute('data-node-id');
                                if (pid) visited.add(pid);
                                el = el.parentElement ? el.parentElement.closest('.tree-node') : null;
                            }
                            var html = '';
                            (state.adj[ancestorId] || []).forEach(function(childId) {
                                html += renderNode(childId, state.adj, visited, state.expanded);
                            });
                            childrenDiv.innerHTML = html;
                        }
                    }
                }
            }
        });

        state.expanded.add(targetUuid);

        setTimeout(function() {
            var header = container.querySelector('.tree-node-header[data-node-id="' + targetUuid + '"]');
            if (header) {
                header.classList.add('tree-selected');
                header.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                var nodeEl = header.closest('.tree-node');
                if (nodeEl) {
                    var attrsDiv = nodeEl.querySelector('[data-attrs-for="' + targetUuid + '"]');
                    var toggleBtn = nodeEl.querySelector('[data-toggle="' + targetUuid + '"]');
                    if (attrsDiv) attrsDiv.style.display = '';
                    if (toggleBtn) toggleBtn.textContent = '−';
                }
            }
        }, 50);
    });
})();