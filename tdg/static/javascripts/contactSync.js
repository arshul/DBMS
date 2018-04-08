app.controller("contactController" , ["$scope" , "$http" , function($scope , $http){

  $http({
    method : 'GET',
    url:api_url.channel+"?per_page=100"
  }).then(function (response) {
    $scope.channelData = response.data.result;
    console.log($scope.channelData);
    
  },function (response) {
    console.log(response);
  })




}])