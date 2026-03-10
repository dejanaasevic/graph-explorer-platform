from api.model import Graph, Node, Edge
from api.plugins import VisualizerPlugin
import json

class BlockVisualizer(VisualizerPlugin):
    def name(self) -> str:
        """Returns the display name of the visualizer."""
        return "Block Visualizer"

    def identifier(self) -> str:
        """Returns the unique string identifier of the visualizer."""
        return "block_visualizer"

    @staticmethod
    def serialize_node(node: Node):
        """
        Serializes a node to a JSON string.

        The resulting object contains the node's ID,
        and all of its attributes as string values.
        """
        dictionary = {"id": str(node.id)}
        for attribute in node.attributes:
            dictionary[attribute] = str(node.attributes[attribute])
        return json.dumps(dictionary)

    @staticmethod
    def serialize_edge(edge: Edge):
        """
        Serializes an edge to a JSON string.

        The resulting object contains the source and target node IDs as strings.
        """
        dictionary = {"source": str(edge.source.id), "target": str(edge.target.id)}
        return json.dumps(dictionary)

    def render(self, graph: Graph, **kwargs) -> str:
        """
        Renders the graph as an HTML script tag containing D3.js visualization code.

        Generates JavaScript that builds a force-directed graph using D3 v3.
        Supports both directed and undirected graphs — directed graphs include
        arrow markers on edges. Returns a <script> string ready to be embedded in HTML.
        """
        node_list_json = "nodes = {"
        for node in graph.get_nodes():
            node_list_json += "'" + str(node.id) + "':"
            node_list_json += BlockVisualizer.serialize_node(node) + ",\n"
        if node_list_json != "nodes = {":
            node_list_json = node_list_json[:-2]
        node_list_json += "}\n"
        edge_list_json = "edges = ["
        for edge in graph.get_edges():
            edge_list_json += BlockVisualizer.serialize_edge(edge) + ",\n"
        if edge_list_json != "edges = [":
            edge_list_json = edge_list_json[:-2]
        edge_list_json += "]\n"
        render_direction = "\t\t.attr('marker-end', 'url(#arrow)')\n" if graph.is_directed() else "\n"

        d3 = """
            function tick(e) {
                node.attr("transform", function(d) {
                    return "translate(" + d.x + "," + d.y + ")";
                }).call(drag);

                link.attr('x1', function(d) { return d.source.x; })
                    .attr('y1', function(d) { return d.source.y; })
                    .attr('x2', function(d) { return d.target.x; })
                    .attr('y2', function(d) { return d.target.y; });
            }
            
            var graph = d3.select("#graph")
                
            var gradient = graph
                .append("defs")
                .append("linearGradient")
                .attr("id", "grad")
                .attr("x1", "0%")
                .attr("x2", "100%")
                .attr("y1", "0%")
                .attr("y2", "100%");
                
            gradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "#ffcc99");
                
            gradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "#ffffcc");
                
            var arrow = graph
                .append("defs")
                .selectAll("marker")
                .data(["arrow"])
                .enter().append("marker")
                .attr("id", "arrow")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 15) 
                .attr("refY", 0.5)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5");
                
            
            edges.forEach(function(edge) {
                edge.source = nodes[edge.source];
                edge.target = nodes[edge.target];
            });
            
            var svgEl = document.getElementById('main-svg');
            var svgW = (svgEl && svgEl.clientWidth)  || 960;
            var svgH = (svgEl && svgEl.clientHeight) || 600;

            var force = d3.layout.force()
                .size([svgW, svgH])
                .nodes(d3.values(nodes))
                .links(edges)
                .on("tick", tick)
                .linkDistance(500)
                .linkStrength(0.01)
                .charge(-2000)
                .start();
                
            var link = graph.selectAll('.link')
                    .data(edges, d => d.source.id + d.target.id)
            var node = graph.selectAll('.node')
                    .data(force.nodes(), d => d.id)
                
            var drag = force.drag().on('dragstart', function() {
                    d3.event.sourceEvent.stopPropagation(); 
                });
                
            var d3ForceKeys = new Set(['index', 'weight', 'x', 'y', 'px', 'py'])
            
            function displayBlock(d){
                var width = 275;
                var textSize = 12;
                var height = (Object.keys(d).length + 1 - d3ForceKeys.size) * 10
                
                d3.select("g.id" + d.id)
                    .append('rect')
                    .attr('x',-5)
                    .attr('y',-5)
                    .attr('width', width)
                    .attr('height', height)
                    .attr('fill','url(#grad)')
                    .attr('stroke', '#99795c');
                
                let spacing = 10
                let mouseoverText = ""
                for (const key of Object.keys(d)){
                    if (d3ForceKeys.has(key)) continue
                    let line = `${key}: ${d[key]}`
                    d3.select("g.id" + d.id)
                        .append('text')
                        .attr('x',0)
                        .attr('y',spacing)
                        .attr('font-size',textSize)
                        .text(line);
                    mouseoverText += line + "\\n"
                    spacing += 10
                }
                
                d3.select("g.id" + d.id)
                    .append('title')
                    .text(mouseoverText)
            }
                
            function render(){
                force.nodes(d3.values(nodes));
                force.links(edges);
                force.start();
                
                link = graph.selectAll('.link')
                    .data(edges, d => d.source.id + d.target.id)
                node = graph.selectAll('.node')
                    .data(force.nodes(), d => d.id)
                    
                link.enter().append('line')
                    .attr('class', 'link')
                    .attr('stroke', '#000000')     
                    .attr('stroke-width', '1px')
            """ + render_direction + """
                
                node.enter().append('g')
                    .attr('class', function(d){ return 'node id' + d.id; })
                    .on('click', function(){ nodeClick(this); })
                    .call(drag)
                    .each(function(d){ displayBlock(d); });
                    
                node.each(function(d){
                    d3.select(this).selectAll("*").remove()
                    displayBlock(d)
                });
                
                graph.selectAll('.node')
                    .data(force.nodes(), d => d.id)
                    .exit()
                    .remove()
                
                graph.selectAll('.link')
                    .data(edges, d => d.source.id + d.target.id)
                    .exit()
                    .remove()
                
                node = graph.selectAll('.node');
                link = graph.selectAll('.link');
            }
            
            render()
        """

        script: str = "<script>\n" + node_list_json + edge_list_json + d3 + "</script>"
        return script