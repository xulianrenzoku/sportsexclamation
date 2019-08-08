const svg = d3.select("#player_board_js")
              .append("svg")
              .attr("width", 600)
              .attr("height", 800)

const margin = { top: 170, right: 10, bottom: 260, left: 70 },
      margin2 = { top: 580, right: 10, bottom: 180, left: 70 },
      margin_density = { top: 170, right: 60, bottom: 260, left: 60 },
      width = +svg.attr("width") - margin.left - margin.right,
      width_density = 600, 
      height = +svg.attr("height") - margin.top - margin.bottom,
      height2 = +svg.attr("height") - margin2.top - margin2.bottom,
      height_density = 800;

// text label for the x axis
svg.append("text")             
    .attr("transform",
          "translate(" + ((width/2 + margin.left)) + " ," + 
                         (height + margin.top + 25) + ")")
    .style("text-anchor", "middle")
    .attr("font-size", "11px")
    .text("Available Players");

// text label for the y axis
svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", margin.left/3)
    .attr("x",0 - (height))
    .attr("dy", "1em")
    .attr("font-size", "11px")
    .style("text-anchor", "middle")
    .text("Projected Fantasy Points");

const x = d3.scaleBand().range([0, width]).padding(0.1),
      x2 = d3.scaleBand().range([0, width]).padding(0.1),
      y = d3.scaleLinear().range([height, 0]),
      y2 = d3.scaleLinear().range([height2, 0]),
      x_density = d3.scaleLinear().domain([0, 100]).range([margin_density.left, width_density - margin_density.right]),
      y_density = d3.scaleLinear().domain([0, .05]).range([height_density - margin_density.bottom, margin_density.top]);
const xAxis = d3.axisBottom(x),
      xAxis2 = d3.axisBottom(x2),
      yAxis = d3.axisLeft(y),
      xAxis_density = d3.axisBottom(x_density),
      yAxis_density = d3.axisLeft(y_density).ticks(null, "%");

var parseTime = d3.timeParse("%Y-%m-%d");

d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
    this.parentNode.appendChild(this);
  });
};

d3.selection.prototype.moveToBack = function() {
  return this.each(function() { 
      var firstChild = this.parentNode.firstChild; 
      if (firstChild) { 
          this.parentNode.insertBefore(this, firstChild); 
      } 
  });
};

var colorDict = {
  'atl' : {'main':'#E03A3E', 'alt':'#C1D32F'},
  'bos' : {'main':'#007A33', 'alt':'#BA9653'},
  'den' : {'main':'#0E2240', 'alt':'#FEC524'},
  'sac' : {'main':'#5A2D81', 'alt':'#63727A'},
  'por' : {'main':'#E03A3E', 'alt':'#63727A'},
  'phi' : {'main':'#006BB6', 'alt':'#ED174C'},
  'lac' : {'main':'#C8102E', 'alt':'#1D428A'},
  'nyk' : {'main':'#006BB6', 'alt':'#F58426'},
  'mil' : {'main':'#00471B', 'alt':'#EEE1C6'},
  'uta' : {'main':'#002B5C', 'alt':'#00471B'},
  'det' : {'main':'#C8102E', 'alt':'#006BB6'},
  'tor' : {'main':'#CE1141' , 'alt':'black'},
  'okc' : {'main':'#007AC1', 'alt':'#EF3B24'},
  'bkn' : {'main':'#000000', 'alt':'#FFFFFF'},
  'pho' : {'main':'#1D1160', 'alt':'#E56020'},
  'was' : {'main':'#002B5C', 'alt':'#E31837'},
  'lal' : {'main':'#552583', 'alt':'#FDB927'},
  'min' : {'main':'#0C2340', 'alt':'#236192'},
  'hou' : {'main':'#CE1141', 'alt':'#000000'},
  'gsw' : {'main': '#006BB6', 'alt':'#FDB927'},
  'dal' : {'main': '#00538C', 'alt':'#B8C4CA'},
  'nor' : {'main': '#0C2340', 'alt':'#85714D'},
  'mia' : {'main': '#98002E', 'alt':'#F9A01B'},
  'chi' : {'main': '#CE1141', 'alt':'#000000'},
  'mem' : {'main': '#5D76A9', 'alt':'#12173F'},
  'cle' : {'main':'#6F263D', 'alt':'#041E42'},
  'sas' : {'main': '#000000', 'alt':'#C4CED4'},
  'cha' : {'main': '#1D1160', 'alt':'#00788C'},
  'orl' : {'main':'#0077C0' , 'alt':'#C4CED4'},
  'ind' : {'main':'#002D62' , 'alt':'#FDBB30'}
}

d3.csv("../static/data/projections.csv", function(error, fantasy_data) {
  if (error) {throw error};
  data = []
  fantasy_data.forEach(function(d) {
    var player = {
      name: d.Name.replace("'", ""),
      playerid: d.Name.trim().split(' ')[1] + d.Name.trim().split(' ')[0],
      Date: parseTime(d.Date),
      fpts: +d.fpts_fanduel,
      clicked: false
    };
    data.push(player); 
  })
  data.sort((a, b) => b.fpts - a.fpts);

  // Set domains
  x.domain(data.map(function(d) { return d.name}));
  y.domain([0, 70]);
  x2.domain(x.domain());
  y2.domain(y.domain());

  // Brush & Zoom
  brush = d3.brushX()
      .extent([[0, 0], [width, height2]])
      .on("brush end", (brushed));
  zoom = d3.zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [width, height]])
    .extent([[0, 0], [width, height]]);

  // Create focus (larger bar chart)
  focus = svg.append("g")
      .attr("class", "focus")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  focus.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
  focus.append("g")
      .attr("class", "axis axis--y")
      .call(yAxis);

  // Create context (smaller bar chart)
  context = svg.append("g")
      .attr("class", "context")
      .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");
  context.append("g")
      .attr("class", "brush")
      .call(brush)
      .call(brush.move, x.range());

  updateMiniBars();
  barTooltips();
});

var parseDate = d3.timeParse("%Y-%m-%d");

d3.csv("../static/data/2018-2019_fd.csv", function(error, historical) {
  if (error) {throw error};

  players = {};
  historical.forEach(function(d) {
    if (!(d.player in players)) {
      players[d.player] = {}
      players[d.player]['name'] = d.player.replace("'", "")
      players[d.player]['playerid'] = d.player.replace(/[\W_]+/g, "")
      players[d.player]['fpts'] = []
      players[d.player]['team'] = ''
    }
    players[d.player]['fpts'].push(+d.fd_pt);
    players[d.player]['team'] = d.team;
  })
})

function barTooltips() {
  var tooltip = svg.append("g")
    .attr("class", "bar_tooltip")
    .style("display", "none");
  tooltip.append("rect")
    .attr("width", 130)
    .attr("height", 40)
    .attr("y", 120)
    .attr("x", -18)
    .attr("fill", "white")
    .style("opacity", 0.8);
  tooltip.append("text")
    .attr('class', 'line_1')
    .attr("x", 48)
    .attr("y", 120)
    .attr("dy", "1.2em")
    .style("text-anchor", "middle")
    .attr("font-size", "14px");
  tooltip.append("text")
    .attr('class', 'line_2')
    .attr("x", 48)
    .attr("y", 120)
    .attr("dy", "2.4em")
    .style("text-anchor", "middle")
    .attr("font-size", "14px");
}

function updateMiniBars(){
  let mini_bars = context.selectAll(".bar")
      .data(data);

  mini_bars
      .enter()
      .insert("rect")
      .attr("class", "bar")
      .attr("x", d => x2(d.name))
      .attr("width", x2.bandwidth())
      .attr("y", d => y2(d.fpts))
      .attr("height", d => height2 - y2(d.fpts))
      .style('fill', function(d) {
        if (d.clicked) {
          return '#FAFB97'
        } else {
          return '#464646'
        }
      });

  mini_bars.exit().remove();

  context.select('.axis--x').remove();

  context.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height2 + ")")
    .call(xAxis2)

  // remove names
  context.select('.axis--x')
      .selectAll("text")
      .remove();

}

function update() {
  displayed = 0;
  let bar = focus.selectAll(".bar")
    .data(data);

  bar
    .attr("x", d => x(d.name))
    .attr("width", x.bandwidth())
    .attr("y", d => y(d.fpts))
    .attr("height", d => height - y(d.fpts))
    .style('fill', function(d) {
      if (d.clicked) {
        return "#FAFB97"
      } else {
        return "#464646"
      }
    })
    .style("display", (d) => {
      let to_display = x(d.name) != null;
      if (to_display) {
        displayed += 1;
        return 'initial';
      }
      return 'none';
    })
    .on("mouseover", function(d){

      // activate tooltip
      svg.select('.bar_tooltip')
         .style('display', null); 

      // highlight bar
      d3.select(this)
        .style("fill", "#fbf9f3") // #C04C4B
        .style("cursor", "pointer");
    })
    .on("mouseout",function(d){ 

      // deactivate tooltip
      svg.select('.bar_tooltip').style('display', 'none'); 

      if (d.clicked) {
        d3.select(this)
          .style("fill", "#FAFB97")
          .style("cursor", "pointer");
      } else {
        d3.select(this)
          .style("fill", "#464646")
          .style("cursor", "pointer");
      }
    })
    .on("mousemove", function(d) {
      const tooltip = svg.select('.bar_tooltip');
      tooltip
        .select("text.line_1")
        .text(`${d.name}`);
      tooltip.select('text.line_2')
        .text(`${(d.fpts)}`);
      tooltip
        .attr('transform', `translate(${[d3.mouse(this)[0], d3.mouse(this)[1]]})`);
    })
    .on("click", function(d){
      d.clicked = !d.clicked
      if (d.clicked) {

        // Highlight bar 
        d3.select(this)
          .style("fill", "#FAFB97")
          .style("cursor", "pointer");
        drawDensity(d);

      } else {

        d3.selectAll("#" + d['playerid']).remove("*");

        // Revert bar color
        d3.select(this)
          .style("fill", "#464646")
          .style("cursor", "pointer");
      }
    });

  bar.enter()
    .insert("rect", '.mean')
    .attr("class", "bar")
    .attr("x", d => x(d.name))
    .attr("width", x.bandwidth())
    .attr("y", d => y(d.fpts))
    .attr("height", d => height - y(d.fpts));
}

function updateAxis() {
  let axis_x = focus.select(".axis--x").call(xAxis);

  axis_x.selectAll("text")
      .remove();
}

function updateContext(min, max) {
  context.selectAll(".bar")
      .style('fill-opacity', (_, i) => i >= min && i < max ? '1' : '0.3');
}

function brushed() {
  var s = d3.event.selection || x2.range();
  current_range = [Math.round(s[0] / (width/data.length)), Math.round(s[1] / (width/data.length))];
  x.domain(data.slice(current_range[0], current_range[1]).map(ft => ft.name));
  svg.select(".zoom").call(zoom.transform, d3.zoomIdentity
      .scale(width / (current_range[1] - current_range[0]))
      .translate(-current_range[0], 0));
  update();
  updateAxis();
  var min = current_range[0]
  var max = current_range[1]
  updateContext(min, max);
}

// ################## DENSITY PLOT ##################
const svg_density = d3.select("#player_board_js")
  .append("svg")
  .attr("width", 600)
  .attr("height", 800)

svg_density.append("g")
  .attr("class", "axis axis--x")
  .attr("transform", "translate(0," + (height_density - margin_density.bottom) + ")")
  .call(xAxis_density);
//svg_density.append("g")
//  .attr("class", "axis axis--y")
//  .attr("transform", "translate(" + margin_density.left + ",0)")
//  .call(yAxis_density);

function kernelDensityEstimator(kernel, X) {
  return function(V) {
    return X.map(function(x) {
      return [x, d3.mean(V, function(v) { return kernel(x - v); })];
    });
  };
}

function kernelEpanechnikov(k) {
  return function(v) {
    return Math.abs(v /= k) <= 1 ? 0.75 * (1 - v * v) / k : 0;
  };
}

function drawPlayer(player, density) { 

  // Find highest point
  var coords = [0, 0]
  density.forEach(function(d) {
    if (d[1] >= coords[1]) {
      coords = d; 
    }
  })

  var defs = svg_density.append("defs")
    .attr("id", "imgdefs")

  var playerid = player['name'].split(', ')[1] + player['name'].split(', ')[0]

  var playerpattern = defs.append("pattern")
                          .attr("id", playerid)
                          .attr("height", 1)
                          .attr("width", 1)
                          .attr("x", "1")
                          .attr("y", "1")

  playerpattern.append("image")
       .attr("x", -15)
       .attr("y", -10)
       .attr("height", 90)
       .attr("width", 90)
       .attr("xlink:href", '../static/images/' + player['name'] + '.png')

  svg_density.append("circle")
    .attr("cx", x_density(coords[0]))
    .attr("cy", y_density(coords[1])-35)
    .attr("id", player['playerid'])
    .attr("r", 30)
    .style("fill", "none")
    .style("stroke", colorDict[player['team']]['alt']);

  svg_density.append("circle")
      .attr("r", 30)
      .attr("cx", x_density(coords[0]))
      .attr("cy", y_density(coords[1])-35)
      .attr("id", player['playerid'])
      .attr("fill", "url(#" + playerid + ")")
      .on('mouseover', function(d) {
        d3.selectAll("#" + player['playerid'])
          .moveToFront()
          .style("cursor", "pointer");
      })
      .on('click', function(d) {
        player_name = player['name'].split(/[ ,]+/)[1] + '-' + player['name'].split(/[ ,]+/)[0]
        link = window.location.protocol + '/player_fanduel?Player=' + player_name
        window.open(link)
      })
}

function drawDensity(player_proj) {

  n1 = player_proj.name.trim().split(' ')
  player_name = n1[1] + ', ' + n1[0]

  var player = players[player_name];

  var n = player['fpts'].length,
      bins = d3.histogram().domain(x_density.domain()).thresholds(40)(player['fpts']),
      density = kernelDensityEstimator(kernelEpanechnikov(7), x_density.ticks(40))(player['fpts']);
  density[0][1] = 0
  density[density.length - 1][1] = 0

  drawPlayer(player, density)

  svg_density.append("path")
    .datum(density)
    .attr("fill", colorDict[player['team']]['main'])
    .attr("stroke", colorDict[player['team']]['alt'])
    .attr("stroke-width", "1.5")
    .attr("opacity", 0.8)
    .attr("id", player['playerid'])
    .attr("stroke-linejoin", "round")
    .attr("d",  d3.line()
        .curve(d3.curveCardinal)
        .x(function(d) { return x_density(d[0]); })
        .y(function(d) { return y_density(d[1]); }))
    .on('mouseover', function(d) {
      d3.selectAll("#" + player['playerid'])
        .moveToFront()
        .style("cursor", "pointer");
    });

    var idx1 = Math.floor(player_proj['fpts']/2)
    var idx2 = idx1 + 1
    var line_height = ((density[idx1][1] + density[idx2][1])) / 2

    svg_density.append("line")
      .attr("x1", x_density(player_proj['fpts']))
      .attr("y1", y_density(0))
      .attr("x2", x_density(player_proj['fpts']))
      .attr("y2", y_density(line_height))
      .attr("id", player['playerid'])
      .style("stroke-width", 2)
      .style("stroke", colorDict[player['team']]['alt'])
      .style("stroke-dasharray", ("3, 3"))
      .style("fill", "none");
}
