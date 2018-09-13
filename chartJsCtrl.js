var app = angular.module('trafficModule', ['chart.js']);
app.controller("TrafficCtrl", ["$scope", "$http", function($scope, $http) {
	//$scope.labels = ['6a', '7a', '8a'];
	//$scope.data = [65,59,80];

	//chart not loading till window resizing! reload... add a watch?

	var ctx = document.getElementById('SundayChart').getContext("2d");
	var label = [];
	var dataset = [];
	var newLabel = [];
	var newDataSet = [];
	var res = {};
	$scope.jsondata = {};
	$scope.user = {};


	$http.get('output_Starbucks 247 King St N, Waterloo, ON N2J 2Y8, Canada1.txt').then(success, error);
	function success(response){
		res = response;
		console.log(response.data.schedule.Sundays);
		$scope.jsondata = response.data.schedule.Sundays;
		//console.log(typeof($scope.jsondata));
		additional_info = "Name: " + response.data.name + "\n" + "Address: " + response.data.address + "\n" + "ID: " + response.data.id + "\n" + 
		"Typical duration of visit: " + response.data.duration_of_visit;
		$scope.additional_info = additional_info;

		pushToArray($scope.jsondata);

	}
	function error(error){
		console.log(error);
	}

	function pushToArray(data){
		label = []; //need to empty them each time, otherwise it appends
		dataset = [];
		for (var key in data) {
			console.log(key + ' is ' + data[key]);
			label.push(key);
			dataset.push(data[key]);
		}
		console.log(label);
		console.log(dataset);
		addExtraDataPoints(data);
	}

	// this function allows the user to use the datepicker in order to select a day of the week to 
	// see busy data for. 
	// It will then create the bar chart showing busy times for that date.
	function callAnyDay(day){
		// toCall = res.data.schedule. + day;
		dayToCall = day + "s";
		listOfTimes = res.data.schedule[dayToCall];
		console.log(listOfTimes);
		pushToArray(listOfTimes);
		createBarChart(ctx);
	}

	function convertToArray(obj) {
		return Object.keys(obj).map(function(key) {
			return obj[key];
		});
	}

	// this function interpolates between hours, adding half-hour blocks.
	function addExtraDataPoints(array) {
		console.log(array);
		var started = false;
		var newkey;
		var newval;
		newLabel = []; //again need to empty each time.
		newDataSet = [];
		var i = 1;
		for (var key in array) {
			newLabel.push(key);
			if (i < Object.keys(array).length) { //not the last one
				//i = i + 1;
				newkey = key + ":30";
				newLabel.push(newkey);
			}
			//console.log(array[key-1]);
			if (started && i <= Object.keys(array).length) { //not the first one
				newDataSet.push(array[key-1]);
				newval = (array[key] + array[key - 1])/2;
				newDataSet.push(newval);
			} 
			//oldval = array[key];
			
			i = i + 1;
			//newDataSet.push(array[key]);
			//newDataSet.push(newval);
			started = true;
			} 
			newDataSet.push(array[key]); //need this last one
			console.log(newLabel);
			console.log(newDataSet);
	}

	//addExtraDataPoints($scope.jsondata);

	//label = convertToArray(label);
	//console.log(typeof(label));
	//dataset = convertToArray(dataset);

	//console.log($scope.day);

	function createBarChart(ctx) {
		var barChart = new Chart(ctx, {
			type: 'bar',
			data: {
				labels: newLabel, //extra data points stored in the newLabel array! 
				datasets: [{
					label: '2017',
					data: newDataSet //the filled in :30 one

				}]
			},
			options: {
				scales: {
					yAxes: [{
						scaleLabel: {
							display: true,
							labelString: 'Percentage busy'
						}
					}],
					xAxes: [{
						scaleLabel: {
							display: true,
							labelString: 'Hour of the day'
						}
					}]
				},
				title: {
					display: true,
					text: $scope.day
				}
			}
		});
	}

	$scope.searching = function(){

		console.log($scope.user.input1);
		console.log($scope.day);
		//call the python script here! 
	}

	$scope.save_to_file = function() {
		//add code here to save the data to the staging.lumotune.com server
		//after user verifies it is the location they want
		//(text search is just that, a text search, so verification is needed)
	}	

	$(document).ready(function(){
		$("#datepicker").datepicker({
			onSelect: function(dateText, inst) {
				var date = $(this).datepicker('getDate');
				$scope.day = $.datepicker.formatDate('DD', date);
				var dayOfWeek = date.getUTCDay();
				console.log($scope.day);
				//console.log(typeof($scope.day));
				callAnyDay($scope.day);
			}
		});
	});

}]);
