/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Species
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_trop"),
"population_dat/trophic_type_counts.csv", // path to CSV file
{
title: 'Trophic type counts',
xlabel: 'Simulation time',
ylabel: '',
//showRangeSelector: true,
//valueRange: [-0.01,1.01],
//labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut'],
legend: 'yes',
fillAlpha: 0.65,
stackedGraph: true,
colors: ['#3333FF', '#33FF33', '#FF3333', '#222222', '#5555FF', '#FF33FF'],
labelsDiv: document.getElementById('legend_trop'),
//labelDivWidth: 0,
//visibility: [true,true,true,true,true],


//rangeSelectorHeight: 30,
// rangeSelectorPlotStrokeColor: 'black',
// rangeSelectorPlotFillColor: 'black',
series: {
		'fac-mixotroph': {
		fillGraph: true,
		strokeWidth: 1.0,
		},
		'autotroph': {
		fillGraph: true,
		strokeWidth: 1.0,
		},
		'heterotroph': {
		fillGraph: true,
		strokeWidth: 1.0,
		},
		'obl-mixotroph': {
		fillGraph: true,
		strokeWidth: 1.0,
		}
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
