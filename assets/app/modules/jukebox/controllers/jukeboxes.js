/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

"use strict";

angular.module('mainApp.jukebox').controller('jukeboxes_controller', function($scope, $location, $routeParams, users_service, jukebox_service, ui) {

    $scope.jukeboxes = jukebox_service.jukeboxes();

    $scope.get_jukeboxes = function(jukebox_ids, filters) {
        jukebox_service.get_jukeboxes_async(jukebox_ids, filters).then(
            function(status) {
                if (status.code === 200) {
                    // All ok
                    console.log($scope.jukeboxes );
                }else if (status.code === 403) {
                    ui.show_notification_warning('Server says: "' + status.message
                    + '" I asked the backend about the reason and replied: "' + status.info +'"');
                }else if (status.code === 404) {
                    ui.show_notification_warning('Sorry jukeboxes NOT found');

                }else{
                    ui.show_notification_error('Error Undocumented status code');
                }
                return;
            },
            function(status){
                console.log('The server encountered an errror');
                return;
            }
        );
    };

    $scope.go_to_jukebox = function(jukebox_id){
        $location.path('/jukebox/' + String(jukebox_id));
    };

    $scope.get_jukeboxes();
});