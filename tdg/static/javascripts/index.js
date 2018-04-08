app.controller("indexController",["$scope" , "$http", function($scope , $http){
    var loader = document.getElementsByClassName("preloader-wrapper")[0],
    filter_loader = document.getElementsByClassName("filter-loading")[0],
    loadMoreDataLoader = $("#load-more-data .preloader-wrapper")[0],
    page = 2    ;

    $scope.agentType = {
        1 : "Vendor",
        2 : "Client"
    };
    $scope.filter = {};

    $http({
        method: "GET",
        url: api_url.whatsappData
    }).then(function(response){
        $scope.whatsappData = response.data.result;
        console.log($scope.whatsappData);
        loader.classList.remove("active");
    }, function(response){
        loader.classList.remove("active");
        Materialize.toast('Error occurs :(', 5000, 'error')            
        
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
        })
    };

    var fetchData = true;

    $(window).scroll(function() {
        if($(window).scrollTop() == $(document).height() - $(window).height()) {
            // ajax call get data from server and append to the div
            if(fetchData){
                fetchData = false;
                loadMoreDataLoader.classList.add("active");
                $scope.filter.page = page;
                $http({
                method: "GET",
                url: api_url.whatsappData,
                params:$scope.filter
                }).then(function(response){
                    var whatsappData = response.data.result;
                    console.log(whatsappData);

                    if(!whatsappData.length) {
                        loadMoreDataLoader.classList.remove("active");
                        fetchData = true;
                        return Materialize.toast('No more record!', 5000)
                    }
                    for(i=0;i<whatsappData.length; i++){
                        $scope.whatsappData.push(whatsappData[i])

                    }
                    loadMoreDataLoader.classList.remove("active");
                    setTimeout(function() {
                        page++;
                        fetchData = true;
                    }, 1000);
                
                },function(response){
                    Materialize.toast('Error! Please reload page :(', 5000, 'error')
                    loadMoreDataLoader.classList.remove("active");
                })
            }
        }
    });

}]);