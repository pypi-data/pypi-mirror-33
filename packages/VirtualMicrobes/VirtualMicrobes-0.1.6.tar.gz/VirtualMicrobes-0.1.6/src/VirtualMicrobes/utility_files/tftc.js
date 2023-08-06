/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Metabolic Types
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_tftc"),
"best_dat/tfs_fecundant.csv", // path to CSV file
{
title: 'TF timecourse',
xlabel: 'Simulation time',
ylabel: '',
yRangePad: 50,
drawYGrid: false,
//showRangeSelector: true,
//valueRange: [-0.01,1.01],
//labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut'],
legend: 'onmouseover',
colors: ['#3333FF', '#FF3333', '#000000', '#55CC55', '#5555FF', '#FF33FF'],
labelsDiv: document.getElementById('legend_tftc'),
labelsDivWidth: 1400,
//visibility: [true,true,true,true,false,false,false,false,false,false,false,false,false,false,false,false],


//rangeSelectorHeight: 30,
// rangeSelectorPlotStrokeColor: 'black',
// rangeSelectorPlotFillColor: 'black',
series: {
		'avrg': {
		strokePattern: null,
		fillGraph: true,
		drawPoints: true,
			pointSize: 1,
		strokeWidth: 0.0,
		},
		'min': {
		strokePattern: null,
		drawPoints: true,
			pointSize: 1,
		strokeWidth: 0.0,
		},
		'max': {
		strokePattern: null,
		strokeWidth: .0,
			drawPoints:true,

		},
		'median': {
		strokePattern: Dygraph.DOTTED_LINE,
		strokeWidth: 3,
		visibility: false,
		},
		'Avg-std': {
		strokePattern: Dygraph.DOTTED_LINE,
		strokeWidth: 3,
		visibility: false,
		},
		'Maxfitmut': {
		//strokePattern: Dygraph.DOT_DASH_LINE,
		strokePattern: null,
		strokeWidth: 0,
		fillGraph: true,
		drawPoints:true,
		//highlightCircleSize: 3
		}
		},
	 highlightSeriesOpts: {
	   strokeWidth: 3,
	   strokeBorderWidth: 2,
	   highlightCircleSize: 5
	 },
drawCallback: function(me, initial) {
		if (blockRedraw || initial) return;
		blockRedraw = true;
		var range = me.xAxisRange();
	// var yrange = me.yAxisRange();
		for (var j = 0; j < gs.length; j++) {
		if (gs[j] == me) continue;
		gs[j].updateOptions( {
		dateWindow: range,
		//valueRange: yrange
		} );
		}
		blockRedraw = false;
	},
rollPeriod: 1,
showRoller: true,
animatedZooms: false,
	group: "all",
}          // options
)
)
