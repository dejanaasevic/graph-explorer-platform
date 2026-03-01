from api.model import Graph, Node, Edge
from api.plugins import VisualizerPlugin
import json


class SimpleVisualizer(VisualizerPlugin):
    def name(self) -> str:
        return "Simple Visualizer"

    def identifier(self) -> str:
        return "simple_visualizer"

    @staticmethod
    def node_label(node: Node) -> str:
        if node.attributes:
            return str(next(iter(node.attributes.values())))
        return str(node.id)[:8]

    @staticmethod
    def serialize_node(node: Node) -> str:
        dictionary = {"id": str(node.id), "label": SimpleVisualizer.node_label(node)}
        for attribute in node.attributes:
            dictionary[attribute] = str(node.attributes[attribute])
        return json.dumps(dictionary)

    @staticmethod
    def serialize_edge(edge: Edge) -> str:
        return json.dumps({"source": str(edge.source.id), "target": str(edge.target.id)})

    def render(self, graph: Graph, **kwargs) -> str:
        node_list_js = "var nodes = {\n"
        for node in graph.get_nodes():
            node_list_js += f"  '{node.id}': {self.serialize_node(node)},\n"
        node_list_js += "};\n"

        edge_list_js = "var edges = [\n"
        for edge in graph.get_edges():
            edge_list_js += f"  {self.serialize_edge(edge)},\n"
        edge_list_js += "];\n"

        arrow_marker = """
            d3.select("svg").append("defs").selectAll("marker")
                .data(["arrow"])
                .enter().append("marker")
                .attr("id", "arrow")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 28)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5");
        """ if graph.is_directed() else ""

        arrow_attr = ".attr('marker-end', 'url(#arrow)')" if graph.is_directed() else ""

        d3 = f"""
            var radius = 20;

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

            var link = graphEl.selectAll(".link")
                .data(edges)
                .enter().append("line")
                .attr("class", "link")
                .attr("stroke", "#999")
                .attr("stroke-width", "1.5px")
                {arrow_attr};

            var drag = force.drag().on("dragstart", function() {{
                d3.event.sourceEvent.stopPropagation();
            }});

            var node = graphEl.selectAll(".node")
                .data(force.nodes())
                .enter().append("g")
                .attr("class", function(d) {{ return "node id" + d.id; }})
                .on("click", function() {{ nodeClick(this); }})
                .call(drag);

            node.append("circle")
                .attr("r", radius)
                .attr("fill", "#6baed6")
                .attr("stroke", "#2171b5")
                .attr("stroke-width", "1.5px");

            node.append("text")
                .attr("text-anchor", "middle")
                .attr("dy", "0.35em")
                .attr("font-size", "11px")
                .attr("fill", "#fff")
                .attr("pointer-events", "none")
                .text(function(d) {{
                    var label = d.label || d.id;
                    return label.length > 10 ? label.substring(0, 10) + "..." : label;
                }});

            node.append("title")
                .text(function(d) {{
                    var d3Keys = new Set(["index", "weight", "x", "y", "px", "py"]);
                    var text = "";
                    for (var key in d) {{
                        if (!d3Keys.has(key)) text += key + ": " + d[key] + "\\n";
                    }}
                    return text;
                }});

            function tick() {{
                link
                    .attr("x1", function(d) {{ return d.source.x; }})
                    .attr("y1", function(d) {{ return d.source.y; }})
                    .attr("x2", function(d) {{ return d.target.x; }})
                    .attr("y2", function(d) {{ return d.target.y; }});

                node.attr("transform", function(d) {{
                    return "translate(" + d.x + "," + d.y + ")";
                }});
            }}
        """

        return "<script>\n" + node_list_js + edge_list_js + d3 + "\n</script>"