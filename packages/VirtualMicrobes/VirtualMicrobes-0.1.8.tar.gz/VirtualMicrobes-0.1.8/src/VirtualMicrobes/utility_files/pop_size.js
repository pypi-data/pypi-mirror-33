/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#3 =  Popsize
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/  

gs.push( new Dygraph(
	document.getElementById("graph_popsize"),
	"population_dat/population_size.csv", // path to CSV file
	{
	title: 'Population size',
	xlabel: 'Simulation time',
	ylabel: '',
	//showRangeSelector: true,
	valueRange: [0.0,],
	legend: 'always',
	colors: ['#555555', '#FF5555', '#FF5555', '#FF5555', '#5555FF', '#FF33FF'],
	visibility: [true,true,true,true,false,false,false,false,false,false,false,false,false,false,false],
	labelsDiv: document.getElementById('legend_popsize'),


	series: {'value': {strokePattern: null,strokeWidth: 1.0,fillGraph:true},},
	drawCallback: function(me, initial) {
			if (blockRedraw || initial) return;
			blockRedraw = true;
			var range = me.xAxisRange();

			for (var j = 0; j < gs.length; j++) {
			if (gs[j] == me) continue;
			gs[j].updateOptions( {
			dateWindow: range,
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
