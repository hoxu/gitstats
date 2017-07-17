// menu transition
$("#leftside-navigation .sub-menu > a").click(function(e) {
  $("#leftside-navigation ul ul").slideUp(), $(this).next().is(":visible") || $(this).next().slideDown(),
  e.stopPropagation()
});


// heatmap SVG
const margin = { top: 50, right: 0, bottom: 100, left: 30 },
  width =520 - margin.left - margin.right,
  height = 320 - margin.top - margin.bottom,
  gridSize = Math.floor(width / 24),
  legendElementWidth = gridSize*2,
  buckets = 9,

  // blue colors
  // colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
  
  // orange colors
  // colors = ['#fff5eb','#fee6ce','#fdd0a2','#fdae6b','#fd8d3c','#f16913','#d94801','#a63603','#7f2704'],

  // yellow colors
  colors =["#ECE622","#D5CF22","#BEB922","#A7A222","#908C22","#797522","#625F22","#625F22","#4B4822","#343222"],

  days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
  times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
  datasets = ["../static/data/data.tsv", "../static/data/data2.tsv"];

const svg = d3.select("#chart").append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


const dayLabels = svg.selectAll(".dayLabel")
  .data(days)
  .enter().append("text")
    .text(function (d) { return d; })
    .attr("x", 0)
    .attr("y", (d, i) => i * gridSize)
    .style("text-anchor", "end")
    .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
    .attr("class", (d, i) => ((i >= 0 && i <= 4) ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis"));

const timeLabels = svg.selectAll(".timeLabel")
  .data(times)
  .enter().append("text") 
    .text((d) => d)
    .attr("x", (d, i) => i * gridSize)
    .attr("y", 0)
    .style("text-anchor", "middle")
    .attr("transform", "translate(" + gridSize / 2 + ", -6)")
    .attr("class", (d, i) => ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"));

const type = (d) => {
  return {
    day: +d.day,
    hour: +d.hour,
    value: +d.value
  };
};

const heatmapChart = function(tsvFile) {
d3.tsv(tsvFile, type, (error, data) => {

  var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  const colorScale = d3.scaleQuantile()
    .domain([0, buckets - 1, d3.max(data, (d) => d.value)])
    .range(colors);

  const cards = svg.selectAll(".hour")
    .data(data, (d) => d.day+':'+d.hour);

  cards.append("title");

  cards.enter().append("rect")
  .attr("x", (d) => (d.hour - 1) * gridSize)
  .attr("y", (d) => (d.day - 1) * gridSize)
  .attr("rx", 4)
  .attr("ry", 4)  
  .attr("class", "hour bordered")
  .attr("width", gridSize)
  .attr("height", gridSize)
  .style("fill", colors[0])
  .on("mouseover", function(d) {
    div.transition()
      .duration(200)
      .style("opacity", .9);
    div.html("Day: " +days[d.day-1]+ "<br>Hour: " +times[d.hour-1]+ "<br>Commits: " +d.value+ "")
      .style("left", (d3.event.pageX + 20) + "px")
      .style("top", (d3.event.pageY - 20) + "px");
    })
  .on("mouseout", function(d) {
    div.transition()
      .duration(500)
      .style("opacity", 0);
    })
  .merge(cards)
    .transition()
    .duration(1000)
    .style("fill", (d) => colorScale(d.value));

  // cards.select("title").text((d) => d.value);  

  cards.exit().remove();

  const legend = svg.selectAll(".legend")
    .data([0].concat(colorScale.quantiles()), (d) => d);

  const legend_g = legend.enter().append("g")
    .attr("class", "legend");

  legend_g.append("rect")
    .attr("x", (d, i) => legendElementWidth * i)
    .attr("y", height)
    .attr("width", legendElementWidth)
    .attr("height", gridSize / 2)
    .style("fill", (d, i) => colors[i]);

  legend_g.append("text")
    .attr("class", "mono")
    .text((d) => "≥ " + Math.round(d))
    .attr("x", (d, i) => legendElementWidth * i)
    .attr("y", height + gridSize);

  legend.exit().remove();
});
};

// use first dataset by default
heatmapChart(datasets[0]);

// dataset buttons
const datasetpicker = d3.select("#dataset-picker")
  .selectAll(".btn btn-primary")
  .data(datasets);

// dataset picking button
datasetpicker.enter()
  .append("input")
  .attr("value", (d) => "Dataset " + d)
  .attr("type", "button")
  .attr("class", "btn-sm btn-primary")
  .on("click", (d) => heatmapChart(d));







generateBarChart("../static/data/day_of_week_copy.tsv", "#day_of_week");

function generateBarChart (pathToTSV,divID){
  // Bar chart, see function 'main' for main execution wheel

   function toNum(d){
    //cleaner function
        d.commits= +d.commits
        return d
  };

  d3.tsv(pathToTSV, toNum, function (error,data){
      "use strict"
      // declare outside for reference later
      var width=520
      var height=380
      var chartWidth, chartHeight
      var margin
      var svg = d3.select(divID).append("svg")
      var axisLayer = svg.append("g").classed("axisLayer", true)
      var chartLayer = svg.append("g").classed("chartLayer", true)
      
      var xScale = d3.scaleBand()
      var yScale = d3.scaleLinear()

      var div = d3.select("body").append("div")
      .attr("class", "rect_tooltip")
      .style("opacity", 0);
      
      function main(data) {
          setSize(data)
          drawAxis()
          drawChart(data)    
      }
      
      function setSize(data) {

          margin = {top:50, right:0, bottom:100,  left:30}
          chartWidth = width - margin.left - margin.right,
          chartHeight = height - margin.top - margin.bottom,        
          
          svg
            .attr("width", 520)
            .attr("height", 320)
          
          axisLayer
            .attr("width", chartWidth)
            .attr("height", chartHeight)
          
          chartLayer
              .attr("width", chartWidth)
              .attr("height", chartHeight)
              .attr("transform", "translate("+[margin.left, margin.top]+")")
              
          xScale.domain(data.map(function(d){ return d.day_name })).range([0, chartWidth])
              .paddingInner(0.1) 
              .paddingOuter(0.5)

          yScale.domain([0, d3.max(data, function(d){ return d.commits})]).range([chartHeight, 0])
              
      }
      
      function drawChart(data) {
         // monitor the transition
          var t = d3.transition()
              .duration(1000)
              .ease(d3.easeLinear)
              .on("start", function(d){ console.log("Transiton start") })
              .on("end", function(d){ console.log("Transiton end") })
          
          var bar = chartLayer
            .selectAll(".bar")
            .data(data)
          
          bar.exit().remove() 


          var labels = chartLayer
            .selectAll("labels")
            .data(data)

          bar
            .enter()
            .append("rect")
            .classed("bar", true)
            .merge(bar) 
            .attr("fill", "rgb(236, 230, 34)")
            .attr("width", xScale.bandwidth())
            .attr("stroke", "#323232")
            //setup for cool transition
            .attr("height", 0)
            .attr("transform", function(d){ return "translate("+[xScale(d.day_name), chartHeight]+")"})
              

          var totalCommits=0
          data.forEach(function(d){
            totalCommits+=d.commits
          })   
          labels
            .enter()
            .append("text")
            .text(function(d){
              var percentage= (d.commits/totalCommits *100).toFixed(2)

              return ""+percentage+"%";
            })
            .attr("transform", function(d){
               return "translate("+[xScale(d.day_name)+5, chartHeight-5]+")"
            })

          chartLayer.selectAll(".bar").transition(t)
              // grows to appropriate amount
              .attr("height", function(d){ return chartHeight - yScale(d.commits) })
              .attr("transform", function(d){ return "translate("+[xScale(d.day_name), yScale(d.commits)]+")"})
      }
      
      function drawAxis(){
          var yAxis = d3.axisLeft(yScale)
              .tickSizeInner(-chartWidth)
          
          axisLayer.append("g")
              .attr("transform", "translate("+[margin.left, margin.top]+")")
              .attr("class", "axis y")
              .call(yAxis);
              
          var xAxis = d3.axisBottom(xScale)
      
          axisLayer.append("g")
              .attr("class", "axis x")
              .attr("transform", "translate("+[margin.left, (height-margin.bottom)]+")")
              .call(xAxis);
          
      }  
      
      //kicks of execution of the bar chart
      main(data);
  }); 

} //end of generateBarChart

generateLineChart("../static/data/commits_by_author.tsv", "#lineChart");
generateLineChart("../static/data/lines_of_code_by_author.tsv", "#lineChart2");

function generateLineChart(pathToTSV, divID){

  function allToNumber(d){
    //converts everything to Number type
    for (var key in d){
      d[key] = +d[key]
    }
    //fix for Unix timestamps
    d.date = new Date(d.date * 1000)
    return d;
  }

  d3.tsv(pathToTSV, allToNumber, function (error,data){
    if (error) throw error;

    var authors = data.columns.slice(1).map(function(id) {
      return {
        id: id,
        values: data.map(function(d) {
          return {date: d.date, commits: d[id]};
        })
      };
    });

    var svgWidth=1200,
    svgHeight=400,
    chartWidth= 1000;

    var svg = d3.select(divID).append("svg").attr("height", svgHeight).attr("width", svgWidth),
      margin = {top: 20, right: 80, bottom: 30, left: 50},
      //this is smaller than svgWidth to accomodate Legend
      width = chartWidth - margin.left - margin.right,
      height = svgHeight - margin.top - margin.bottom,
      //dynamically builds grid
      numberGridLines=30
      //main chart container
      g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var xScale = d3.scaleTime().range([0, width]),
        yScale = d3.scaleLinear().range([height, 0]),
        // 10 nice colors
        z = d3.scaleOrdinal(d3.schemeCategory10);

    var line = d3.line()
      .curve(d3.curveBasis)
      .x(function(d) { return xScale(d.date); })
      .y(function(d) { return yScale(d.commits);});

    xScale.domain(d3.extent(data, function(d) { return d.date; }));

    yScale.domain([
      d3.min(authors, function(c) { return d3.min(c.values, function(d) { return d.commits; }); }),
      d3.max(authors, function(c) { return d3.max(c.values, function(d) { return d.commits; }); })
    ]);

    z.domain(authors.map(function(c) { return c.id; }));

    function main(){
      drawAxisLineChart();
      drawChartLineChart();
      drawLegend();
    }

    // gridlines in x axis 
    function make_x_gridlines() {   
      return d3.axisBottom(xScale)
          .ticks(numberGridLines)
    }

    // gridlines in y axis
    function make_y_gridlines() {   
      return d3.axisLeft(yScale)
          .ticks(numberGridLines)
    }

    function drawAxisLineChart(){
      g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale));

      g.append("g")
          .attr("class", "axis axis--y")
          .call(d3.axisLeft(yScale))
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", "0.71em")
          .attr("fill", "#000")

      // add the X gridlines
      g.append("g")     
          .attr("class", "grid")
          .attr("transform", "translate(0," + height + ")")
          .call(make_x_gridlines()
              .tickSize(-height)
              .tickFormat("")
          );

      // add the Y gridlines
      g.append("g")     
          .attr("class", "grid")
          .call(make_y_gridlines()
              .tickSize(-width)
              .tickFormat("")
          );

    }

    function drawChartLineChart() {
      var author = g.selectAll(".author")
        .data(authors)
        .enter().append("g")
          .attr("class", "author");

      author.append("path")
          .attr("class", "line")
          .attr("d", function(d) { return line(d.values); })
          .style("stroke", function(d) { return z(d.id); });

      // Enable to show author at the end of the line
      // author.append("text")
      //     .datum(function(d) { return {id: d.id, value: d.values[d.values.length - 1]}; })
      //     .attr("transform", function(d) { return "translate(" + xScale(d.value.date) + "," + yScale(d.value.commits) + ")"; })
      //     .attr("x", 3)
      //     .attr("dy", "0.35em")
      //     .style("font", "10px sans-serif")
      //     .text(function(d) { return d.id; });

      }

      function drawLegend(){
        var legend= svg.selectAll(".legend-item")
        .data(authors)
        .enter().append("g")
          .attr("class","legend");

        legend.append("rect")
            .attr('x', chartWidth - 20)
            .attr('y', function(d, i) {
              return (i * 35) + 20;
            })
            .attr('width', 10)
            .attr('height', 10)
            .style('fill', function(d) {
              return z(d.id);
            });
        legend.append('text')
            .attr('x', chartWidth - 8)
            .attr('y', function(d, i) {
              return (i * 35) + 29;
            })
            .text(function(d) {
              return d.id;
            });
      }

      main(); //kicks off main execution wheel

  }); //end tsv read in

}; //end generate line chart


