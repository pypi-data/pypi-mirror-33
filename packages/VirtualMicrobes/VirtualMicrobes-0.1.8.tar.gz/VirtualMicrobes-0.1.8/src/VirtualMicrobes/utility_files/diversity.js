/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Metabolic Types
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/

gs = []; 			// Empty vector of graphs (used to store them for synchronization)
var blockRedraw = false;	// Used for synchronization of zooming
var initialized = false;	// "	"	"	"	"

gs.push(new Dygraph(
document.getElementById("graph_genotype_diversity"), "ecology_dat/genotype.csv", // path to CSV file
{
    title: 'Genotype diversity',
    xlabel: 'Simulation time',
    ylabel: '',
    //showRangeSelector: true,
    //valueRange: [-0.01,1.01],
    //labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut'],
    legend: 'always',
    //colors: ['#FF3333', '#FF3333', '#FF3333', '#0000EE', '#0000EE', '#0000EE', '#0000EE', '#FF3333', '#FF3333', '#FF3333'],
    labelsDiv: document.getElementById('legend_genotype_diversity'),
    //labelDivWidth: 0,
    //visibility: [false,false,false,false,false,false,false,false,false,false,true,true,true,true,true,true,true,true,true,true,true,true],


    //rangeSelectorHeight: 30,
    // rangeSelectorPlotStrokeColor: 'black',
    // rangeSelectorPlotFillColor: 'black',
    /*series: {
		'producer_max_diff': {
		strokePattern: Dygraph.DASHED_LINE,
		pointSize: 1,
		strokeWidth: 1.0,
		},
		'producer_min_diff': {
		strokePattern: Dygraph.DASHED_LINE,
		pointSize: 1,
		strokeWidth: 1.0,
		},
		'consumer_max_diff': {
		strokePattern: Dygraph.DASHED_LINE,
		pointSize: 1,
		strokeWidth: 1.0,
		},
		'consumer_min_diff': {
		strokePattern: Dygraph.DASHED_LINE,
		pointSize: 1,
		strokeWidth: 1.0,
		},
		
	}, 
	*/

    // highlightSeriesOpts: {
    //   strokeWidth: 2,
    //   strokeBorderWidth: 1,
    //   highlightCircleSize: 5
    // },
    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

gs.push(new Dygraph(
document.getElementById("graph_reaction_genotype_diversity"), "ecology_dat/reaction_genotype.csv", // path to CSV file
{
    title: 'Reaction Genotype Diversity',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_reaction_genotype_diversity'),

    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

gs.push(new Dygraph(
document.getElementById("graph_metabolic_type_diversity"), "ecology_dat/metabolic_type.csv", // path to CSV file
{
    title: 'Metabolic Type Diversity',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_metabolic_type_diversity'),

    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

gs.push(new Dygraph(
document.getElementById("graph_producer_diversity"), "ecology_dat/producer_type.csv", // path to CSV file
{
    title: 'Producer Diversity',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_producer_diversity'),

    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

gs.push(new Dygraph(
document.getElementById("graph_consumer_diversity"), "ecology_dat/consumer_type.csv", // path to CSV file
{
    title: 'Consumer Diversity',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_consumer_diversity'),

    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

gs.push(new Dygraph(
document.getElementById("graph_import_diversity"), "ecology_dat/import_type.csv", // path to CSV file
{
    title: 'Import Genotype Diversity',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_import_diversity'),

    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

gs.push(new Dygraph(
document.getElementById("graph_export_diversity"), "ecology_dat/export_type.csv", // path to CSV file
{
    title: 'Export Genotype Diversity',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_export_diversity'),

    drawCallback: function(me, initial) {
        if (blockRedraw || initial) return;
        blockRedraw = true;
        var range = me.xAxisRange();
        var yrange = me.yAxisRange();
        for (var j = 0; j < gs.length; j++) {
            if (gs[j] == me) continue;
            gs[j].updateOptions({
                dateWindow: range,
                valueRange: yrange
            });
        }
        blockRedraw = false;
    },
    rollPeriod: 10,
    showRoller: true,
    animatedZooms: false,
    includeZero: true,
    group: "all",
} // options
))

Dygraph.synchronize(gs);
