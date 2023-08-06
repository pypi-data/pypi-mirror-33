/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	coalescence 
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_generations"),
"population_dat/iterages.csv", // path to CSV file
{
title: 'Number of generations',
xlabel: 'Simulation time',
ylabel: '',
//showRangeSelector: true,
//valueRange: [-0.01,1.01],

legend: 'always',
labelsDiv: document.getElementById('legend_generations'),

//labelDivWidth: 0,
visibility: [true,true,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false],

colors: ['#3333FF', '#FF3333', '#000000', '#55CC55', '#5555FF', '#FF33FF'],

//rangeSelectorHeight: 30,
// rangeSelectorPlotStrokeColor: 'black',
// rangeSelectorPlotFillColor: 'black',

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
