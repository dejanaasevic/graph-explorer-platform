from api.model import Graph, Node, Edge
from api.plugins import VisualizerPlugin
import json

class BlockVisualizer(VisualizerPlugin):
    def name(self) -> str:
        return "Block Visualizer"

    def identifier(self) -> str:
        return "block_visualizer"

    @staticmethod
    def serialize_node(node: Node):
        dictionary = {"id": str(node.id)}
        for attribute in node.attributes:
            dictionary[attribute] = str(node.attributes[attribute])
        return json.dumps(dictionary)

    @staticmethod
    def serialize_edge(edge: Edge):
        dictionary = {"source": str(edge.source.id), "target": str(edge.target.id)}
        return json.dumps(dictionary)

    def render(self, graph:Graph, **kwargs) -> str:
        node_list_json = "nodes = {"
        for node in graph.get_nodes():
            node_list_json += "'" + str(node.id) + "':"
            node_list_json += BlockVisualizer.serialize_node(node) + ",\n"
        node_list_json = node_list_json[:-2] + "}\n"

        edge_list_json = "edges = ["
        for edge in graph.get_edges():
            edge_list_json += BlockVisualizer.serialize_edge(edge) + ",\n"
        edge_list_json = edge_list_json[:-2] + "]\n"

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
                
            var gradient = d3.select("svg")
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
                
            var arrow = d3.select("svg")
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
                
            var graph = d3.select("#graph")
            
            edges.forEach(function(edge) {
                edge.source = nodes[edge.source];
                edge.target = nodes[edge.target];
            });
            
            var force = d3.layout.force()
                .size([480, 270])
                .nodes(d3.values(nodes))
                .links(edges)
                .on("tick", tick)
                .linkDistance(3000)
                .linkStrength(0)
                .charge(-2000)
                .start();
                
            var link = graph.selectAll('.link')
                .data(edges)
                .enter().append('line')
                .attr('class', 'link')
                .attr('stroke', '#000000')     
                .attr('stroke-width', '1px')
        """ + render_direction + """
            var drag = force.drag().on('dragstart', function() {
                d3.event.sourceEvent.stopPropagation(); 
            });
    
            var node = graph.selectAll('.node')
                .data(force.nodes()) 
                .enter().append('g')
                .attr('class', function(d){ return 'node id' + d.id; })
                .on('click', function(){ nodeClick(this); })
                .call(drag);
                
            const d3ForceKeys = new Set(['index', 'weight', 'x', 'y', 'px', 'py'])
                                
            node.each(function(d){ displayBlock(d); });
            
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
        """

        script: str = "<script>\n" + node_list_json + edge_list_json + d3 + "</script>"
        return script