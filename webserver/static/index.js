Vue.use(VueResource);

app = new Vue({
  el: '#app',
  data: {
  	namespace: '__test__',
  	name: 'counter1',
  },
  created: function() {
  	google.charts.load('current', {packages: ['corechart', 'line']});
  },
  methods: {
  	show: function() {
  		this.$http.get(`/counter/${this.namespace}/${this.name}`).then(response => {
  			this.draw(response.body.counters);
  		});
  	},
  	draw: function(counters) {
			var data = new google.visualization.DataTable();
      data.addColumn('datetime', 'Time');
      data.addColumn('number', 'Value');
      counters.forEach(counter => {
	      data.addRow([new Date(counter.timestamp), counter.lastMinCount]);
      });

      var options = {
	      hAxis: {
	        title: 'Time',
	        format: 'MM/dd HH:mm',
	        slantedText: true, 
          slantedTextAngle: 45,
	      },
	      vAxis: {
		      title: 'Value'
	      }
      };

      var chart = new google.visualization.LineChart(document.getElementById('Chart'));
      chart.draw(data, options);  		
  	},
  },
});