from api.model import Graph, Node, Edge
from api.plugins import VisualizerPlugin
import json


class SimpleVisualizer(VisualizerPlugin):
    def name(self) -> str:
        """Returns the display name of the visualizer."""
        return "Simple Visualizer"

    def identifier(self) -> str:
        """Returns the unique string identifier of the visualizer."""
        return "simple_visualizer"

    @staticmethod
    def node_label(node: Node) -> str:
        """
        Returns the display label for a node.

        Uses the first attribute value if any attributes exist,
        otherwise falls back to the first 8 characters of the node's ID.
        """
        if node.attributes:
            return str(next(iter(node.attributes.values())))
        return str(node.id)[:8]

    @staticmethod
    def serialize_node(node: Node) -> str:
        """
        Serializes a node to a JSON string.

        The resulting object contains the node's ID, its display label,
        and all of its attributes as string values.
        """
        dictionary = {"id": str(node.id), "label": SimpleVisualizer.node_label(node)}
        for attribute in node.attributes:
            dictionary[attribute] = str(node.attributes[attribute])
        return json.dumps(dictionary)

    @staticmethod
    def serialize_edge(edge: Edge) -> str:
        """
        Serializes an edge to a JSON string.

        The resulting object contains the source and target node IDs as strings.
        """
        return json.dumps({"source": str(edge.source.id), "target": str(edge.target.id)})

    def render(self, graph: Graph, **kwargs) -> str:
        """
        Renders the graph as an HTML script tag containing D3.js visualization code.

        Generates JavaScript that builds a force-directed graph using D3 v3.
        Supports both directed and undirected graphs — directed graphs include
        arrow markers on edges. Returns a <script> string ready to be embedded in HTML.
        """
        node_list_js = "var nodes = {\n"
        for node in graph.get_nodes():
            node_list_js += f"  '{node.id}': {self.serialize_node(node)},\n"
        node_list_js += "};\n"

        edge_list_js = "var edges = [\n"
        for edge in graph.get_edges():
            edge_list_js += f"  {self.serialize_edge(edge)},\n"
        edge_list_js += "];\n"

        arrow_marker = """
            d3.select("#main-svg").append("defs").selectAll("marker")
                .data(["arrow"])
                .enter().append("marker")
                .attr("id", "arrow")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 10)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
        """ if graph.is_directed() else ""

        arrow_attr = ".attr('marker-end', 'url(#arrow)')" if graph.is_directed() else ""

        d3 = f"""
            var radius = 32;

            {arrow_marker}

            edges.forEach(function(edge) {{
                edge.source = nodes[edge.source];
                edge.target = nodes[edge.target];
            }});

            var force = d3.layout.force()
                .size([480, 270])
                .nodes(d3.values(nodes))
                .links(edges)
                .linkDistance(120)
                .charge(-400)
                .on("tick", tick)
                .start();

            var graphEl = d3.select("#graph");

            var drag = force.drag().on("dragstart", function() {{
                d3.event.sourceEvent.stopPropagation();
            }});

            var link = graphEl.selectAll(".link").data(edges);
            var node = graphEl.selectAll(".node").data(force.nodes());

            function displayNode(selection) {{
                selection.append("circle")
                    .attr("r", radius)
                    .attr("fill", "#6baed6")
                    .attr("stroke", "#2171b5")
                    .attr("stroke-width", "1.5px");

                selection.append("text")
                    .attr("text-anchor", "middle")
                    .attr("font-size", "10px")
                    .attr("fill", "#fff")
                    .attr("pointer-events", "none")
                    .each(function(d) {{
                        var label = String(d.label || d.id);
                        var charsPerLine = 10;
                        var sel = d3.select(this);
                        if (label.length <= charsPerLine) {{
                            sel.append("tspan").attr("x", 0).attr("dy", "0.35em").text(label);
                        }} else {{
                            var line1 = label.substring(0, charsPerLine);
                            var rest = label.substring(charsPerLine);
                            var line2 = rest.length > charsPerLine ? rest.substring(0, charsPerLine - 1) + "..." : rest;
                            sel.append("tspan").attr("x", 0).attr("dy", "-0.25em").text(line1);
                            sel.append("tspan").attr("x", 0).attr("dy", "1.2em").text(line2);
                        }}
                    }});

                selection.append("title")
                    .text(function(d) {{
                        var d3Keys = new Set(["index", "weight", "x", "y", "px", "py"]);
                        var text = "";
                        for (var key in d) {{
                            if (!d3Keys.has(key)) text += key + ": " + d[key] + "\\n";
                        }}
                        return text;
                    }});
            }}

            function render() {{
                force.nodes(d3.values(nodes));
                force.links(edges);
                force.start();

                link = graphEl.selectAll(".link")
                    .data(edges, function(d) {{ return d.source.id + d.target.id; }});

                link.enter().append("line")
                    .attr("class", "link")
                    .attr("stroke", "#999")
                    .attr("stroke-width", "1.5px")
                    {arrow_attr};

                graphEl.selectAll(".link")
                    .data(edges, function(d) {{ return d.source.id + d.target.id; }})
                    .exit()
                    .remove();

                node = graphEl.selectAll(".node")
                    .data(force.nodes(), function(d) {{ return d.id; }});

                node.enter().append("g")
                    .attr("class", function(d) {{ return "node id" + d.id; }})
                    .on("click", function() {{ nodeClick(this); }})
                    .call(drag)
                    .call(displayNode);

                node.each(function(d) {{
                    d3.select(this).selectAll("*").remove();
                    displayNode(d3.select(this));
                }});

                graphEl.selectAll(".node")
                    .data(force.nodes(), function(d) {{ return d.id; }})
                    .exit()
                    .remove();

                node = graphEl.selectAll(".node");
                link = graphEl.selectAll(".link");
            }}

            function tick() {{
                link.each(function(d) {{
                    var dx = d.target.x - d.source.x, dy = d.target.y - d.source.y;
                    var dist = Math.sqrt(dx*dx + dy*dy) || 1;
                    d3.select(this)
                        .attr("x1", d.source.x + dx/dist*radius)
                        .attr("y1", d.source.y + dy/dist*radius)
                        .attr("x2", d.target.x - dx/dist*radius)
                        .attr("y2", d.target.y - dy/dist*radius);
                }});

                node.attr("transform", function(d) {{
                    return "translate(" + d.x + "," + d.y + ")";
                }});
            }}

            render();
        """

        return "<script>\n" + node_list_js + edge_list_js + d3 + "\n</script>"