app.controller("priceController", ["$scope", "$http", function ($scope, $http) {
    $scope.routePostData={'price':{}};
    $scope.cabData = {'cab_category':null};
    $scope.cabCategory =[
        'hatchback',
        'sedan',
        'suv'
   ];
   $scope.cabIcons={
       "hatchback":"http://cdn1.carbuyer.co.uk/sites/carbuyer_d7/files/car_images/renault-megane.jpg",
       "sedan": "https://imgd.aeplcdn.com/1280x720/cw/ec/28343/Lexus-ES-Right-Front-Three-Quarter-93381.jpg?wm=0&q=100",
       "suv": "https://www.drivespark.com/car-image/540x400x80/car/6054634-tata_nexon.jpg"
   };
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
        $scope.edit = function(route){
        $scope.editData = route;

    },
        $scope.del = function(route_id){
        $scope.delId = route_id;

    },
        $scope.delete = function () {
            $http({
            method: "DELETE",
            url: api_url.route+"/"+$scope.delId.toString(),
            }).then((response) => {
            Materialize.toast("Deleted", 800);
        },(response) => {
            Materialize.toast("Something went wrong", 800);
        });
        }
        $scope.update = function () {
            console.log($scope.editData);
            $http({
            method: "PUT",
            url: api_url.route,
            data: $scope.editData
        }).then((response) => {
            Materialize.toast("Updated", 800);
        },(response) => {
            Materialize.toast("Fill the fields correctly", 800);
        });
        }

   $(document).ready(function(){
       $('.modal').modal();
    });
   $scope.capitalizeFirstLetter = function(string) {
       if(!string)return;
       return string.charAt(0).toUpperCase() + string.slice(1);
    };

}]);
