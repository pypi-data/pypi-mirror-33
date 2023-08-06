/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Production rate
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_csize"),
"cell_size_time_course.csv", // path to CSV file
{
title: 'Cell size',
xlabel: 'Time (days)',
ylabel: '',
//valueRange: [-0.01,1.01],
//labels: ['Avgfit', 'Minfit', 'Maxfit', 'Maxfitmut'],
legend: 'always',
colors: ['#00AAAA', '#FF5555', '#000000', '#FF5555', '#5555FF', '#FF33FF', '#FFFF00', '#333333', '#FF00FF', '#FF0000', '#0000FF', '#00AA00', '#FFFF77', '#FF33FF', '#000000'],
labelsDiv: document.getElementById('legend_csize'),
//visibility: [true,true,true,true,true],


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
	   strokeWidth: 2,
	   strokeBorderWidth: 1,
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
