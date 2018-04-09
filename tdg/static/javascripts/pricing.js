app.controller("priceController", ["$scope", "$http", function ($scope, $http) {
//   var loader = document.getElementsByClassName("preloader-wrapper")[0];

  $scope.cabData = {'cab_category':null};
  $scope.cabCategory =[
       'hatchback',
       'sedan',
       'suv'
  ];
  $scope.capitalizeFirstLetter = function(string) {
    if(!string)return;
    return string.charAt(0).toUpperCase() + string.slice(1);
};

  $http({
        method: "GET",
        url: api_url.destination
  }).then((response) => {
        $scope.locationData = response.data.result;
        console.log(response.data);
        // loader.classList.remove("active");
        $scope.locationObject = createStructure($scope.locationData);
        setTimeout(() => {
          $('select').material_select();

        }, 1000);

  }, (response) => {
  });
$scope.fetchDestination = function(){
    console.log("clicked");
    $http({
        method: "GET",
        url: api_url.destination+"?source_id="+$scope.cabData.source_id
    }).then((response) => {
        $scope.destData = response.data.result;
        // loader.classList.remove("active");
        $scope.locationObject = createStructure($scope.locationData);
        setTimeout(() => {
          $('select').material_select();

        }, 1000);

  }, (response) => {
  });
},



  $scope.submitCabData = function () {
      console.log($scope.cabData);
    $http({
        method: "GET",
        url: api_url.route+"?source_id="+$scope.cabData.source_id+"&destination_id="+$scope.cabData.destination_id+"&cab_category="+$scope.cabData.cab_cat,
        // data: $scope.cabData
    }).then((response) => {
        Materialize.toast("Submitted", 800);
        $scope.Route = response.data.result;
        // loader.classList.remove("active");
    },(response) => {
                Materialize.toast("Error occurs!", 800);
        });

    };

    function createStructure(object){
        var returnObject = {};
        for(var i = 0; i < object.length ; i++){
            returnObject[object[i].id] = object[i];
        }

        return returnObject;

    }


}]);