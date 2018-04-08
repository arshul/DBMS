app.controller("senderMessageController", ["$scope", "$http", function ($scope, $http) {
    var loader = document.getElementsByClassName("preloader-wrapper")[0];

    $scope.select = {
        channels: []
    };
    $scope.senderId = {};
    $scope.messageState = [];


    $scope.CATEGORY = {
        1: 'Tour',
        2: 'Cab',
        3: 'Flight',
        4: 'Visa',
        5: 'Stay',
        6: 'Forex',
        7: 'Job',
        8: 'Girls',
        9: 'Others'
    }

    var currentTime = new Date();
    $scope.currentTime = currentTime;
    $scope.month = ['Januar', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    $scope.monthShort = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    $scope.weekdaysFull = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    $scope.weekdaysLetter = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    $scope.disable = [false, 1, 7];
    $scope.today = 'Today';
    $scope.clear = 'Clear';
    $scope.close = 'Close';
    var days = 15;
    $scope.time = currentTime.getHours() + ":" + currentTime.getMinutes();
    $scope.minDate = (new Date($scope.currentTime.getTime() - (1000 * 60 * 60 * 24 * days))).toISOString();
    $scope.maxDate = (new Date($scope.currentTime.getTime() + (1000 * 60 * 60 * 24 * days))).toISOString();

    $http({
        method: "GET",
        url: api_url.channel
    }).then(function (response) {
        $scope.channelData = response.data.result;
        loader.classList.remove("active");

    },
        function (response) {
            Materialize.toast('Error occurs :(', 5000, 'red');

        });

    $scope.sendMessage = function () {


        console.log($scope.select.channels);
        var dateString = $scope.currentTime + " " + $scope.time,
            dateTimeParts = dateString.split(' '),
            timeParts = dateTimeParts[1].split(':'),
            dateParts = dateTimeParts[0].split('/'),
            date;

        date = new Date(dateParts[2], parseInt(dateParts[1], 10) - 1, dateParts[0], timeParts[0], timeParts[1]);


        var channelArray = $scope.select.channels;
        //console.log("channelArray = ",channelArray);
        // var senderArray = $scope.select.senders;
        delete $scope.select.channels;
        // var sender_id = $scope.senderId
        //console.log("sender_id = ",$scope.senderId.id);

        //console.log("select = ",$scope.select);
        // return;
        $http({
            method: "POST",
            url: api_url.message,
            data: $scope.select
        }).then(function (response) {
            //console.log(response.data);
            console.log("response : ", response.data);

            //console.log( "above for loop ",$scope.messageState);

            for (i = 0; i < channelArray.length; i++) {
                $scope.messageState.push({
                    'schedule_date': date.getTime() / 1000,
                    'status': 1,
                    'message_id': response.data.result.id,
                    'sender_id': $scope.senderId.id

                })
                //console.log("channelArray[i] = ",channelArray[i]);
                //console.log("channelArray[i].id = ",channelArray[i].id);
                //console.log("channelArray[i].group = ",channelArray[i].group);

                if (channelArray[i].group) {

                    $scope.messageState[i].channel_id = $scope.messageState[i].group_id = channelArray[i].id;
                    console.log($scope.messageState);
                } else {
                    $scope.messageState[i].channel_id = channelArray[i].id;
                    $scope.messageState[i].group_id = null;

                }
                //console.log("for loop ",$scope.messageState[i]);


                $http({
                    method: "POST",
                    url: api_url.message_state,
                    data: $scope.messageState[i]

                }).then(function (reponse) {


                    loader.classList.remove("active");
                    Materialize.toast("Message Added", 5000, "teal");

                }, function (response) {
                    console.log(response)
                })
            }
            $scope.messageState = [];
        },
            function (response) {
                Materialize.toast('Error occurs :(', 5000, 'red');
                console.log(response);

            });
    }



    $http({
        method: "GET",
        url: api_url.sender
    }).then(function (response) {
        $scope.senderData = response.data.result;
        console.log("senderData = ", $scope.senderData);

    }, function (response) {

    })




}]);

/*

api/v1/message
CATEGORY = {
   1: 'Tour',
   2: 'Cab',
   3: 'Flight',
   4: 'Visa',
   5: 'Stay',
   6: 'Forex',
   7: 'Job',
   8: 'Girls',
   9: 'Others'
}
type =  1 or 2












*/
