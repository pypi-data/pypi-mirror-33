/***************************
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#1 = GENOME SIZE 
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	***************************/  

	gs.push( new Dygraph(
	document.getElementById("graph_gsize"),
	"population_dat/genome_sizes.csv",		 // path to CSV file
	{
	title: 'Genome length dynamics',
	xlabel: 'Simulation time',
	ylabel: '',
	//valueRange: [0.0,1.01],
	//labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut', 'Hoi', 'Test'],
	legend: 'always',
	colors: ['#5555FF', '#5555FF', '#5555FF', '#5555FF', '#5555FF', '#FF33FF'],
	visibility: [true,true,true,true,false,false,false,false,false,false,false,false,false,false,false],
	labelsDiv: document.getElementById('legend_gsize'),
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
				drawPoints:true, pointsize: 0.5,
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
			//var yrange = me.yAxisRange();
			for (var j = 0; j < gs.length; j++) {
			if (gs[j] == me) continue;
				gs[j].updateOptions( 
				{
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
	}          // options
	)
	)
