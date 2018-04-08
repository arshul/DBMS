app.controller("trackerController",["$scope" , "$http", function($scope , $http){
    var loader = document.getElementsByClassName("preloader-wrapper")[0],
    filter_loader = document.getElementsByClassName("filter-loading")[0];

    $scope.channel = {};
    $scope.agentData = function(messageData){
        console.log(messageData);
        $scope.alterMessageData = messageData;
    };

    $scope.agentType = {
        1 : "Vendor",
        2 : "Client"
    };
    $scope.filter = {};
    $('.modal').modal();

    $http({
        method:"GET",
        url:api_url.tracking
    }).then(function(response){
        $scope.trackingData = response.data.result;
        console.log("tracking data = ",$scope.trackingData);
        loader.classList.remove("active");
    }, function(response){
        console.log(response);
        loader.classList.remove("active");
        Materialize.toast('Error occurs :(', 13000, 'error')            
    });

    $scope.applyFilter = function(){
        filter_loader.classList.add("progress");
        $http({
            method: "GET",
            url: api_url.whatsappData,
            params:$scope.filter
        }).then(function(response){
            $scope.whatsappData = response.data.result;
            console.log($scope.whatsappData);
            filter_loader.classList.remove("progress");
        } , function(response){
            filter_loader.classList.remove("progress");
            Materialize.toast('Error occurs :(', 3000, 'error')            
        })
    };

    $http({
        method: "GET",
        url: api_url.channel
    }).then(function(response){
        var channelData = response.data.result;
        for(var i=0; i<channelData.length;i++){
            $scope.channel[channelData[i].id] = channelData[i].name;
        }
        console.log("$scope.channel= ",$scope.channel);
    })
}]);



