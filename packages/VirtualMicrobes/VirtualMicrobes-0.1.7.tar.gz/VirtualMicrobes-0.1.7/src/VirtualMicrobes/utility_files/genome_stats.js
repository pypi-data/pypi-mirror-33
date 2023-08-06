/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Genome Stats
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/

gs = []; // Empty vector of graphs (used to store them for synchronization)
var blockRedraw = false; // Used for synchronization of zooming
var initialized = false; // "	"	"	"	"

/***************************
	TF Promoter Strength
***************************/

gs.push(new Dygraph(
document.getElementById("graph_tf_promoter_strengths"), "population_dat/tf_promoter_strengths.csv", // path to CSV file
{
    title: 'TF Promoter Strength',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_tf_promoter_strengths'),

    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },

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

/***************************
	Enzyme Promoter Strength
***************************/

gs.push(new Dygraph(
document.getElementById("graph_enz_promoter_strengths"), "population_dat/enzyme_promoter_strengths.csv", // path to CSV file
{
    title: 'Enzyme Promoter Strength',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_enz_promoter_strengths'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	Pump Promoter Strength
***************************/

gs.push(new Dygraph(
document.getElementById("graph_pump_promoter_strengths"), "population_dat/pump_promoter_strengths.csv", // path to CSV file
{
    title: 'Pump Promoter Strength',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_pump_promoter_strengths'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	TF Differential Regulation
***************************/

gs.push(new Dygraph(
document.getElementById("graph_differential_regulation"), "population_dat/differential_regulation.csv", // path to CSV file
{
    title: 'Differential TF Regulation',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_differential_regulation'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	Pump Vmax
***************************/

gs.push(new Dygraph(
document.getElementById("graph_pump_vmaxs"), "population_dat/pump_vmaxs.csv", // path to CSV file
{
    title: 'Transport Vmax',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_pump_vmaxs'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	Enzyme Vmax
***************************/

gs.push(new Dygraph(
document.getElementById("graph_enzyme_vmaxs"), "population_dat/enzyme_vmaxs.csv", // path to CSV file
{
    title: 'Enzyme Vmax',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_enzyme_vmaxs'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	TF Operator binding Ks
***************************/

gs.push(new Dygraph(
document.getElementById("graph_tf_k_bind_ops"), "population_dat/tf_k_bind_ops.csv", // path to CSV file
{
    title: 'TF Operator binding Ks',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_tf_k_bind_ops'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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


/***************************
	TF Ligand Ks
***************************/

gs.push(new Dygraph(
document.getElementById("graph_tf_ligand_ks"), "population_dat/tf_ligand_ks.csv", // path to CSV file
{
    title: 'TF Ligand Ks',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_tf_ligand_ks'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	Enzyme Substrate Ks
***************************/

gs.push(new Dygraph(
document.getElementById("graph_enz_subs_ks"), "population_dat/enz_subs_ks.csv", // path to CSV file
{
    title: 'Enzyme Substrate Ks',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_enz_subs_ks'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	Pump Substrate Ks
***************************/

gs.push(new Dygraph(
document.getElementById("graph_pump_subs_ks"), "population_dat/pump_subs_ks.csv", // path to CSV file
{
    title: 'Pump Substrate Ks',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_pump_subs_ks'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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

/***************************
	Pump Energye Ks
***************************/

gs.push(new Dygraph(
document.getElementById("graph_pump_ene_ks"), "population_dat/pump_ene_ks.csv", // path to CSV file
{
    title: 'Pump Energy Ks',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_pump_ene_ks'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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


/***************************
	TF counts
***************************/

dg = new Dygraph(
document.getElementById("graph_tf_counts"), "population_dat/tf_counts.csv", // path to CSV file
{
    title: 'TF Counts',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_tf_counts'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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
)
//gs.push(dg)

/***************************
	Enzyme counts
***************************/

dg = new Dygraph(
document.getElementById("graph_enzyme_counts"), "population_dat/enzyme_counts.csv", // path to CSV file
{
    title: 'Enzyme Counts',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_enzyme_counts'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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
)

//gs.push(dg)

/***************************
	Importer counts
***************************/

dg = new Dygraph(
document.getElementById("graph_importer_counts"), "population_dat/importer_counts.csv", // path to CSV file
{
    title: 'Importer Counts',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_importer_counts'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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
)

//gs.push(dg)

/***************************
	Exporter counts
***************************/

dg = new Dygraph(
document.getElementById("graph_exporter_counts"), "population_dat/exporter_counts.csv", // path to CSV file
{
    title: 'Exporter Counts',
    xlabel: 'Simulation time',
    ylabel: '',

    legend: 'always',
    labelsDiv: document.getElementById('legend_exporter_counts'),
    colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
    visibility: [true, true, true, true, false, false, false, false, false, false, false, false, false, false, false],
    series: {
        'avrg': {
            strokePattern: null,
            fillGraph: true,
            strokeWidth: 1.0,
        },
        'min': {
            strokeWidth: 1.0,
        },
        'max': {
            strokePattern: null,
            drawPoints: true,
            pointsize: 0.5,
            strokeWidth: 0.0,

        },
        'median': {
            strokePattern: Dygraph.DOTTED_LINE,
            strokeWidth: 1,
        },

    },
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
)
//gs.push(dg)

Dygraph.synchronize(gs);
