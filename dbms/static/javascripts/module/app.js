var app = angular.module('whatsappDashboard', ['checklist-model','ui.materialize']);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

//, 'ui.bootstrap', 'ui.bootstrap.datetimepicker'