  google.load('visualization', '1', {'packages': ['geochart']});
  google.setOnLoadCallback(cb);
  
  var geochart;
  
  function cb()
  {
	geochart = new google.visualization.GeoChart(document.getElementById('chart_div'));
	  
  }
  function drawMap(country) {
	var data = google.visualization.arrayToDataTable([
	  ['State', 'Population'],

	]);

//	geochart = new google.visualization.GeoChart(document.getElementById('chart_div'));
	geochart.draw(data, {width: 500, height: 300, region: country, resolution: "provinces"});
	
	
	 google.visualization.events.addListener(geochart, 'select', function() {
		   alert("f**k");
  var selection = chart.getSelection();
  if (selection.length == 1) {
  var selectedRow = selection[0].row;
  var selectedRegion = data.getValue(selectedRow, 0);
  if(ivalue[selectedRegion] != '') { document.location = ivalue[selectedRegion];  }
  }
  }); 
	
  };
  
  
  
