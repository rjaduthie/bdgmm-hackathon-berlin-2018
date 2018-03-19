function processCharts( ) {
/*******************************************************************************
 * INITIALIZATION
 ******************************************************************************/
/* RESET FUNCTIONALITY */
d3.selectAll('a#all').on('click', function () {
    dc.filterAll();
    dc.renderAll();
});


/* Read Config */
var config;
loadJSON(function(response){
    config = JSON.parse(response);
}, 'config.json');


(function() {
    var compositeChart = dc.compositeChart;
    dc.compositeChart = function(parent, chartGroup) {
        var _chart = compositeChart(parent, chartGroup);
        
        _chart._brushing = function () {
            var extent = _chart.extendBrush();
            var rangedFilter = null;
            if(!_chart.brushIsEmpty(extent)) {
                rangedFilter = dc.filters.RangedFilter(extent[0], extent[1]);
            }

            dc.events.trigger(function () {
                if (!rangedFilter) {
                    _chart.filter(null);
                } else {
                    _chart.replaceFilter(rangedFilter);
                }
                _chart.redrawGroup();
            }, dc.constants.EVENT_DELAY);
        };
        
        return _chart;
    };
})();
/* please note that all keys in df correspond to the %-strings in git's
 * log format */

/*******************************************************************************
 * DATA PROCESSING => CREATE SOME CHARTS
 ******************************************************************************/
d3.csv('data.csv', function (error, data) {
    //Explicitely cast integers
    //data.forEach(function(datum) //{
        //datum[df.at] //= //+datum[df.at];
        //datum[df.ct] //= //+datum[df.ct];
    //});
    var ndx = crossfilter(data);
    dc.dataCount('#data-count').dimension(ndx).group(ndx.groupAll());

    /* Adapt the view dependant on the config */
    var navList = document.getElementById('navList');
    for (var chart in config.charts) {
        if (config.charts[chart] === "true") {
            var li = document.createElement("li");
            var a = document.createElement("a");
            a.setAttribute("href", "javascript:void(0)");
            a.setAttribute("onClick", "document.getElementById('" + chart + "_header').scrollIntoView(); window.scrollBy(0,-50);");
            a.appendChild(document.createTextNode(chart));
            li.appendChild(a);
            navList.appendChild(li);
            /* add headers - only to charts*/
            if(chart.indexOf("dataTable") === -1) {
                var h2 = document.createElement("h2");
                h2.setAttribute("class", "sub-header");
                h2.setAttribute("id", chart + "_header");
                h2.innerHTML = chart;
                console.log(chart)
                document.getElementById(chart).appendChild(h2);
            }
        }
    }
    document.title = "IEE BDGMM workshop showcase";
    document.getElementById("h1").innerHTML
        = document.title

    /**************************************************************************
     * SELECT MENUS
     *************************************************************************/
    if (config.charts.Sensors === "true") {
        var sensorDimension = ndx.dimension(function (d) {
            return d["Sensor"];
        });
        var sensors = sensorDimension.group().reduceCount();
        dc.selectMenu('#Sensors')
            .multiple(true)
            .numberVisible(13)
            .dimension(sensorDimension)
            .group(sensors)
            .order(function(a,b) {
                return a.value < b.value ? 1 : b.value < a.value ? -1 : 0;
            })
            .on('renderlet', function(chart) {
                chart.selectAll("select.dc-select-menu").classed("center-block", true);
            });
    }

    /**************************************************************************
     * BARCHART OF COMMITS PER WEEKDAY (BOTTUM UP)
     *************************************************************************/

    /**************************************************************************
     * TIMELINE CHART (COMMITS PER DAY)
     *************************************************************************/
    if (config.charts.Datetime === "true") {
        var measurementByDatetime = ndx.dimension(function (d) {
            var exactDate = Date.parse(d["dateTime"])
            return exactDate;
        });


        var internalTimeGroup = measurementByDatetime
            .group()
            .reduceCount(function(d) {
                return Date.parse(d["dateTime"]);
        });

//        var patchesByCommittime = ndx.dimension(function (d) {
//            var exactDate = new Date(d[df.ct] * 1000);
//            return d3.time.day(exactDate);
//        });
//
//        var committerTimeGroup = patchesByCommittime
//            .group()
//            .reduceCount(function(d) {
//                return d3.time.hour(new Date(d[df.ct] * 1000))
//            });

        var compositeTimeLineChart = dc.compositeChart('#timeLine'); 

        var measurementLineChart = dc.lineChart(compositeTimeLineChart)
            .dimension(measurementLineChart)
            .colors('red')
            .group(internalTimeGroup);



//        var commitLineChart = dc.lineChart(compositeTimeLineChart)
//            .colors('green')
//            .dimension(patchesByCommittime)
//            .group(committerTimeGroup);
//

        compositeTimeLineChart
            .width(600)
            .height(250)
            .margins({top: 30, right: 50, bottom: 25, left: 40})
            .x(d3.time.scale()
                .domain(d3.extent(data, function(d) {
                            return Date.parse(d["dateTime"])
            })))
            .compose([measurementLineChart])
            .elasticY(true);
/*            .round(d3.time.hour.round)
            .xUnits(d3.time.hour)
            .elasticY(true)
            .brushOn(true)
            .on('renderlet', function(chart) {
                chart.selectAll("svg").classed("center-block", true)
            });**/
    }

    /**************************************************************************
     * DETAILS TABLE
     *************************************************************************/
    if (config.charts.dataTable === "true") {
        var dtFormat = d3.time.format("%d.%m.%Y (%H:%M)");
        dc.dataTable('#dataTable')
            .dimension(ndx.dimension(function(d) {return d;}))
            .group(function(d) {return 'DUMMY';})
            .size(10)
            .columns([
                function (d) {return d["Sensor"];},
                function (d) {return d["Observation"];},
                function (d) {return d["dateTime"];},
                function (d) {return d["dataValue"];},
                function (d) {return d["internal"];},

            ])
            .sortBy(function (d) {return d["dataValue"];})
            .on('renderlet', function (table) {
                table.select('tr.dc-table-group').remove();
            });
    } else {
        var tableDiv = document.getElementById('dataTableMail');
        tableDiv.parentNode.removeChild(tableDiv);
    }

    /* FINISH */
    dc.renderAll();
});
}

function loadJSON(callback, path) {

    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', path, false);
    xobj.onreadystatechange = function() {
       if (xobj.readyState == 4 && xobj.status == "200") {
           callback(xobj.responseText);
       }
    };

    xobj.send(null);
}
