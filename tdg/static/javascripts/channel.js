app.controller("channelController",["$scope" , "$http" , function($scope , $http){

    $scope.chat = {};
    $scope.newTag={};
    $scope.tagsData = [];
    let groupCheck = false, page = 1;
    $scope.channelData = [];
    $scope.csvContacts = {
        list : []
    };


    let loader = document.getElementsByClassName("preloader-wrapper")[0],
    loadMoreDataLoader = $("#load-more-data .preloader-wrapper")[0],
    loadMoreMessageLoader = $("#load-more-message .preloader-wrapper")[0];

    // recursiveForSorting();
     $http({
         method:"GET",
         url: api_url.channel+"?group=false&per_page=100"
     }).then(function(response){
         $scope.channelData = response.data.result;
         $scope.groupData = createStructure($scope.channelData);
         console.log($scope.channelData);
         console.log($scope.groupData);
         loader.classList.remove("active");
     });

    $http({
         method:"GET",
         url: api_url.channel+"?group=false "
    }).then(function(response){
         $scope.individualData = createStructure(response.data.result);
         console.log($scope.individualData);
    });

    $http({
      method:"GET",
      url: api_url.tag
    }).then(function(response){
      $scope.tagsData = response.data.result;
      console.log($scope.tagsData);
    });


    $scope.getChannelsByTagName = function(tagId){
           $http({
            method:"GET",
            url: api_url.channel+"?group=false&per_page=100&tag_id="+tagId
           }).then(function(response){
             $scope.channelData = response.data.result;
             // $scope.groupData = createStructure($scope.channelData);
             console.log($scope.channelData);
             // console.log($scope.groupData);
             // loader.classList.remove("active");
           })

    };

    $scope.addTag = function(channelId){

      if(!$scope.newTag[channelId]){
        return Materialize.toast('Tag not added', 5000, "error");
      }
      var newlyAddedaTag;
      console.log($scope.newTag[channelId]);
      $http({
        method:"GET",
        url: api_url.tag+"?name="+$scope.newTag[channelId],
      }).then(function(response){
          console.log(response);
          var tagId;
          if(!response.data.result.length){

            $http({
              method:"POST",
              url: api_url.tag,
              data : {
                name : $scope.newTag[channelId]
              },
              json: true
            }).then(function(response){
              newlyAddedaTag =  response.data.result;
              tagId = response.data.result.id;
              addTagWithChannel();

            });



          }else{
            tagId = response.data.result[0].id;
            addTagWithChannel();
          }

          function addTagWithChannel(){

            $http({
              method:"POST",
              url: api_url.channel_tag,
              data : {
                tag_id : tagId,
                channel_id : channelId
              }
            }).then(function(response){
              var result = response.data;
              console.log(result);
              $scope.tagsData.push(newlyAddedaTag);
              $scope.newTag[channelId] = undefined;
              return Materialize.toast('Tag Added', 5000);


            });

          }
      }, function (resaponse) {
        return Materialize.toast('Tag not added', 5000, "error");

      })

    };


    $scope.showMessage = function(channel) {
        $scope.chat = {};
        $scope.chat = channel; 
        loadMoreMessageLoader.classList.remove("removeElement");
        $http({
            method:"GET",
            url: api_url.message+"?"+(channel.group ? "group_id" : "channel_id")+"="+channel.id
        }).then(function(response){
            $scope.messageData = response.data.result;
            console.log($scope.messageData);
            loadMoreMessageLoader.classList.add("removeElement");
        
        })
    };

    $scope.removeClass = function(event) {
        event.target.parentNode.getElementsByClassName("line-clamp")[0].classList.remove("line-clamp");
        event.target.remove();
    };

    $scope.toggleChannels = function(fetchGroup){
        groupCheck = fetchGroup;
        loader.classList.add("active");
        $http({
            method:"GET",
            url: api_url.channel+"?group="+groupCheck+"&per_page=100"
        }).then(function(response){
            $scope.channelData = response.data.result;
            console.log($scope.channelData);
            loader.classList.remove("active");
        })
    };


    $scope.downloadContactsAsCsv = function(){

        console.log($scope.csvContacts.list);

        if(!$scope.csvContacts.list.length){
            return Materialize.toast('Please select channels.', 5000 , "error");
        }

        let items = [], csv = "";

      for(let i = 0 ; i < $scope.csvContacts.list.length ; i++){
            items.push({
                "Name"                : $scope.csvContacts.list[i].name,
                "Subject"			  : "",
                "Notes"				  : "",
                "Group Membership"	  : "* My Contacts",
                "Phone 1 - Type"      : "Mobile",
                "Phone 1 - Value"     : $scope.csvContacts.list[i].number,
                "E-mail 1 - Type"     : "* Work",
                "E-mail 1 - Value"    : $scope.csvContacts.list[i].email,
                "Website 1 - Type"	  : "Work",
                "Website 1 - Value"   : $scope.csvContacts.list[i].website

            });
            console.log("items = ");
            console.log(items);


        }

        console.log("items = ",items);

        // Loop the array of objects
        for(let row = 0; row < items.length; row++){
            let keysAmount = Object.keys(items[row]).length;
            let keysCounter = 0;

            // If this is the first row, generate the headings
            if(row === 0){

               // Loop each property of the object
               for(let key in items[row]){

                                   // This is to not add a comma at the last cell
                                   // The '\n' adds a new line
                   csv += key + (keysCounter+1 < keysAmount ? ',' : '\r\n' );
                   keysCounter++;
               }
               keysCounter = 0;

               for(let key in items[row]){
                   csv += items[row][key] + (keysCounter+1 < keysAmount ? ',' : '\r\n' );
                   keysCounter++;
               }


            }else{
               for(let key in items[row]){
                   csv += items[row][key] + (keysCounter+1 < keysAmount ? ',' : '\r\n' );
                   keysCounter++;
               }
            }


        }
        console.log("csv =",csv)

        //var data = ($("#customers").text().trim().replace(/[\n]+/g, ";").replace(/  /g, "").replace(/;;;/g, ";\n") + ";").replace(/\n/g, "\r\n");

        let link = document.createElement('a');
        link.download = "contact.csv";
//        link.href = 'data:application/csv;base64,' + btoa(csv);
        link.setAttribute('href', 'data:text/plain;charset=utf-16,' + encodeURIComponent(csv));
        link.click();



    };

    // turn off fetch data
  var fetchData = false;

  $("#channelContainer").scroll(function() {
        if($("#channelContainer")[0].scrollHeight - $("#channelContainer")[0].scrollTop < 700) {
            // ajax call get data from server and append to the div
            if(fetchData){
                fetchData = false;
                loadMoreDataLoader.classList.add("active");
                $http({
                    method: "GET",
                    url: api_url.channel+"?group="+groupCheck+"&per_page=100&page="+page
                }).then(function(response){
                  let channelData = response.data.result;
                  console.log(channelData);

                    if(!channelData.length) {
                        loadMoreDataLoader.classList.remove("active");
                        fetchData = false;
                        return Materialize.toast('No more record!', 5000);
                    }
                    for(i=0;i<channelData.length; i++){
                        $scope.channelData.push(channelData[i])

                    }
                    loadMoreDataLoader.classList.remove("active");
                    setTimeout(function() {
                        page++;
                        fetchData = true;
                    }, 2000);
                
                },function(response){
                    Materialize.toast('Error! Please reload page :(', 5000, 'error')// error is our custom class
                    loadMoreDataLoader.classList.remove("active");
                })
            }
        }
    });


    function createStructure(object){
      let structuredData = {};
      for(i=0; i < object.length; i++){
            structuredData[object[i].id] = object[i]
        }
        return structuredData;
    }

    function recursiveForSorting() {

        if(true){
            fetchData = false;
            loadMoreDataLoader.classList.add("active");
            $http({
                method: "GET",
                url: api_url.channel+"?group="+groupCheck+"&per_page=100&page="+page
            }).then(function(response){
              let channelData = response.data.result;
              console.log(channelData);

                if(!channelData.length) {
                    console.log(channelData.length);
                    loadMoreDataLoader.classList.remove("active");
                    fetchData = false;
                    return Materialize.toast('No more record!', 5000)
                }
                for(i=0;i<channelData.length; i++){
                    $scope.channelData.push(channelData[i])

                }
                loadMoreDataLoader.classList.remove("active");
                loader.classList.remove("active");
                // setTimeout(function() {
                    page++;
                    recursiveForSorting();
                    // fetchData = true;
                // }, 2000);
            
            },function(response){
                Materialize.toast('Error! Please reload the page :(', 5000, 'error')// error is custom class
                loadMoreDataLoader.classList.remove("active");
            })
        }

        
    }







    // timeDifference(Date.now()/1000 , 1598456201 )
    $scope.timeDifference = function(previous) {

        var msPerMinute = 60;
        var msPerHour = msPerMinute * 60;
        var msPerDay = msPerHour * 24;
        var msPerMonth = msPerDay * 30;
        var msPerYear = msPerDay * 365;
        var current = Date.now()/1000;

        var elapsed = current - previous;

        if (elapsed < msPerMinute) {
                return (Math.round(elapsed) ==1 ?  Math.round(elapsed)+ ' second ago':Math.round(elapsed)+ ' seconds ago');   
        }

        else if (elapsed < msPerHour) {
                return (Math.round(elapsed/msPerMinute)==1 ?  Math.round(elapsed/msPerMinute) + ' minute ago':Math.round(elapsed/msPerMinute) + ' minutes ago');   
        }

        else if (elapsed < msPerDay ) {
                return (Math.round(elapsed/msPerHour )==1 ? Math.round(elapsed/msPerHour )+ ' hour ago':Math.round(elapsed/msPerHour )+ ' hours ago');   
        }

        else if (elapsed < msPerMonth) {
            return (Math.round(elapsed/msPerDay)==1 ?  Math.round(elapsed/msPerDay)+ ' day ago': Math.round(elapsed/msPerDay)+ ' days ago');   
        }

        else if (elapsed < msPerYear) {
            return (Math.round(elapsed/msPerMonth)==1 ? Math.round(elapsed/msPerMonth)  + ' month ago': Math.round(elapsed/msPerMonth)  + ' months ago');   
        }

        else {
            return (Math.round(elapsed/msPerYear)==1 ?  Math.round(elapsed/msPerYear)+ ' year ago' : Math.round(elapsed/msPerYear)+ ' years ago');   
        }
    }







}]);

