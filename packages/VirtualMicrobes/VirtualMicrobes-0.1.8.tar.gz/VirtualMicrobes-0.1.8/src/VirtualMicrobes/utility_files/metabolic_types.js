/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Metabolic Types
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_metabolic_types"),
"population_dat/metabolic_types.csv", // path to CSV file
{
title: 'Metabolic types (conversion/production)',
xlabel: 'Simulation time',
ylabel: '',
//showRangeSelector: true,
//valueRange: [-0.01,1.01],
//labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut'],
legend: 'always',
colors: ['#FF3333', '#FF3333', '#FF3333', '#55CC55', '#0000EE', '#0000EE', '#0000EE', '#FF3333', '#FF3333', '#FF3333'],
labelsDiv: document.getElementById('legend_metabolic_types'),
//labelDivWidth: 0,
visibility: [false,false,false,false,true,true,true,true,true,true,false,false,false,false,false,false,false,false,false,false,false,false],


//rangeSelectorHeight: 30,
// rangeSelectorPlotStrokeColor: 'black',
// rangeSelectorPlotFillColor: 'black',
series: {
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
	// highlightSeriesOpts: {
	//   strokeWidth: 2,
	//   strokeBorderWidth: 1,
	//   highlightCircleSize: 5
	// },
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
