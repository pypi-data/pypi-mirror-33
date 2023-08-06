/**************************
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#2 = # Chromosomes
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	***************************/  

	gs.push(new Dygraph(
	document.getElementById("graph_ccounts"),
	"population_dat/chromosome_counts.csv", // path to CSV file
	{
	title: 'Chromosome numbers',
	//showRangeSelector: true,
	xlabel: 'Simulation time',
	ylabel: '',
	//valueRange: [0.0,1.01],
	//labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut'],
	legend: 'always',
	colors: ['#FF5555', '#FF5555', '#FF5555', '#FF5555', '#5555FF', '#FF33FF'],
	visibility: [true,true,true,true,false,false,false,false,false,false,false,false,false,false,false],
	labelsDiv: document.getElementById('legend_ccounts'),

	

	//rangeSelectorHeight: 30,
	// rangeSelectorPlotStrokeColor: 'black',
	// rangeSelectorPlotFillColor: 'black',
	series: {
			'avrg': {
			strokePattern: null,
			fillGraph: true,
			strokeWidth: 1.0,
			},
			'min': {
			strokePattern: null,
			strokeWidth: 1.0,
	//                  drawPoints: true,
			pointSize: 1,
	//                    highlightCircleSize: 2
			},
			'max': {
			strokePattern: null,
			strokeWidth: 0.0,
				drawPoints: true, pointSize: 2,

			},
			'median': {
			strokePattern: Dygraph.DOTTED_LINE,
			strokeWidth: 1,

			}
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
	group: "all"
	}         // options
	)
	)
