document.addEventListener("DOMContentLoaded", function(event) {

  // Create the input graph
  var g = new dagreD3.graphlib.Graph({compound:true})
    .setGraph({rankdir: 'LR'})
    .setDefaultEdgeLabel(function() { return {}; });

  // Create the renderer
  var render = new dagreD3.render();

  // Set up an SVG group so that we can translate the final graph.
  var svg = d3.select(".graph1");

    data_string = svg.attr("data")
      .substr(1).slice(0, -1)
      .replace(/\\\"/g, '"')
      .replace(/\\n/g,' ')
      .replace(/ /g,'');
    var data = JSON.parse(data_string);

    data.nodes.forEach(function(e) {
      g.setNode(e.id, {label: e.label||e.id, class:e.status});
      // add the groups
      g.setNode(e.group, {label: e.group, clusterLabelPos: 'top', style: 'fill: #d3d7e8'});
    });
    data.nodes.forEach(function(e) {
      g.setParent(e.id, e.group);
    });
    data.links.forEach(function(e) {
      g.setEdge(e.source, e.target)
    });
    g.nodes().forEach(function(v) {
      var node = g.node(v);
      // Round the corners of the nodes
      node.rx = node.ry = 5;
    });

  var svgGroup = svg.append("g");
  // Run the renderer. This is what draws the final graph.
  render(d3.select(".graph1 > g"), g);

  // Center the graph
  var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
  svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
  svg.attr("height", g.graph().height + 40);


  /////// SECOND GRAPH


  // Create the input graph
  var g2 = new dagreD3.graphlib.Graph({compound:true})
    .setGraph({rankdir: 'LR'})
    .setDefaultEdgeLabel(function() { return {}; });

  // Create the renderer
  var render2 = new dagreD3.render();

  var svg2 = d3.select(".graph2");

  data_string_2 = svg2.attr("data")
    .substr(1).slice(0, -1)
    .replace(/\\\"/g, '"')
    .replace(/\\n/g,' ')
    .replace(/ /g,'');
  var data2 = JSON.parse(data_string_2);

  data2.nodes.forEach(function(e) {
    g2.setNode(e.id, {label: e.label||e.id, class:e.status});
    // add the groups
    g2.setNode(e.group, {label: e.group, clusterLabelPos: 'top', style: 'fill: #d3d7e8'});
  });
  data2.nodes.forEach(function(e) {
    g2.setParent(e.id, e.group);
  });
  data2.links.forEach(function(e) {
    g2.setEdge(e.source, e.target, {curve: d3.curveBasis})
  });
  g2.nodes().forEach(function(v) {
    var node = g2.node(v);
    // Round the corners of the nodes
    node.rx = node.ry = 5;
  });

  var svgGroup2 = svg2.append("g");
  // Run the renderer. This is what draws the final graph.
  render2(d3.select(".graph2 > g"), g2);

  // Center the graph
  var xCenterOffset = (svg2.attr("width") - g2.graph().width) / 2;
  svgGroup2.attr("transform", "translate(" + xCenterOffset + ", 20)");
  svg2.attr("height", g2.graph().height + 40);

});
