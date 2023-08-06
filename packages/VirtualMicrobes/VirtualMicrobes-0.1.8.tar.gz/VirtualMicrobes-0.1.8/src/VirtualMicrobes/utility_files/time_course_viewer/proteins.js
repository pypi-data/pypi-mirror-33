/***************************
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	Production rate
!!!!!!!!!!!!!!!!!!!!!!!!!!!!
***************************/ 

gs.push( new Dygraph(
document.getElementById("graph_prots"),
"prot_time_courses.csv", // path to CSV file
{
title: 'Proteins',
xlabel: 'Time (days)',
ylabel: '',
gridLineColor: '#DDDDDD',
//fillGraph: true,
//labels: ['a.0','a.1','a.2','b.0','b.1','b.2','c.0','c.1','c.2','d.0','d.1','d.2','e.0','e.1','e.2','f.0','[f.1]','f.2','[g.0]','g.1','g.2','h.0','h.1','h.2','i.0*','i.1*]'],
legend: 'always',
colors: ['#00AAAA', '#FF5555', '#000000', '#FF5555', '#5555FF', '#FF33FF', '#FF1133', '#333333', '#FF00FF', '#FF0000', '#0000FF', '#00AA00', '#FF0077', '#333333', '#FF00FF', '#FF0000', '#FF33FF', '#000000'],
labelsDiv: document.getElementById('legend_prots'),
//visibility: [true,true,true,false,false],


rangeSelectorHeight: 30,
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
