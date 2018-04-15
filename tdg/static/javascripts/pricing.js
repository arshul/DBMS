app.controller("priceController", ["$scope", "$http", function ($scope, $http) {
    $scope.routePostData={'price':{}};
    $scope.cabData = {'cab_category':null};
    $scope.cabCategory =[
        'hatchback',
        'sedan',
        'suv'
   ];
   $http({
        method: "GET",
        url: api_url.route,
    }).then((response) => {
        $scope.allRoutes = response.data.result;
        console.log($scope.allRoutes);
    }, (response) => {
        Materialize.toast("Something Went Wrong!!", 800);
    });
   $http({
       method: "GET",
       url: api_url.destination
    }).then((response) => {
        $scope.locationData = response.data.result;
        setTimeout(() => {
            $('select').material_select();
        }, 1000);
    }, (response) => {
    });
    $scope.fetchDestination = function(){
        $http({
            method: "GET",
            url: api_url.destination+"?source_id="+$scope.cabData.source_id
        }).then((response) => {
            $scope.destData = response.data.result;
            setTimeout(() => {
                $('select').material_select();
            }, 1000);
        }, (response) => {
        });
    },
    $scope.submitCabData = function () {
        $http({
            method: "GET",
            url: api_url.route+"?source_id="+$scope.cabData.source_id+"&destination_id="+$scope.cabData.destination_id+"&cab_category="+$scope.cabData.cab_cat,
        }).then((response) => {
            Materialize.toast("Submitted", 800);
            $scope.Route = response.data.result;
        }, (response) => {
            Materialize.toast("Something Went Wrong!!", 800);
        });
    },
    $scope.createRoute = function(){
        $http({
            method: "POST",
            url: api_url.route,
            data: $scope.routePostData
        }).then((response) => {
            Materialize.toast("Submitted", 800);
            $('.modal').modal('hide');
            $scope.Route = response.data.result;
        },(response) => {
            Materialize.toast("Fill the fields correctly", 800);
        });
    },
   $(document).ready(function(){
       $('.modal').modal();
    });
   $scope.capitalizeFirstLetter = function(string) {
       if(!string)return;
       return string.charAt(0).toUpperCase() + string.slice(1);
    };

}]);
