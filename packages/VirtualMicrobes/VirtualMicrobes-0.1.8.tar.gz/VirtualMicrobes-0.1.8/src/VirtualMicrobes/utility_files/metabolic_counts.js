/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Metabolic Types
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_metabolic_counts"),
"population_dat/metabolic_types.csv", // path to CSV file
{
title: 'Metabolic counts',
xlabel: 'Simulation time',
ylabel: '',
//showRangeSelector: true,
//valueRange: [-0.01,1.01],

legend: 'always',
//labels: ['a0','a2','a3','a4','a5','a6','a7','a8','a9','a10','a11','a12','a13','a14','a15','a16', 'a17'],
labelsDiv: document.getElementById('legend_metabolic_counts'),

//labelDivWidth: 0,
visibility: [true,true,true,true,false,false,false,false,false,false,false,false,false,false,false,false,false],

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
