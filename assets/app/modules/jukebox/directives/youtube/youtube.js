/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

"use strict";

angular.module('mainApp.jukebox').directive('youtubePlayer', function($window, ui, jukebox_service, player_service) {
    return {
        restrict: 'A', // only activate on element attribute
        scope: true, // New scope to use but rest inherit proto from parent
        compile: function(tElement, tAttrs) {
            var youtube_api_src = 'https://www.youtube.com/iframe_api';
            // Helper
            var myScriptIsLoaded = function (url) {
                var scripts = document.getElementsByTagName('script');
                for (var i = scripts.length; i--;) {
                    if (scripts[i].src == url) return true;
                }
                return false;
            }
            // Load the Youtube js api if not found
            if (myScriptIsLoaded(youtube_api_src) === false){
                var jsCode = document.createElement('script');
                jsCode.setAttribute('src', youtube_api_src);
                document.body.appendChild(jsCode);
                return;
            }
            $window.onYouTubeIframeAPIReady(); // Let's signal the new player
        },
        controller: function($scope, $element, $attrs) {

            // Bind once
            $scope.player = player_service.getPlayer();

            $scope.start_playing = function (jukebox_id){
                console.log('Yes I am starting...');
                $scope.player = player_service.getPlayer();
                console.log($scope.player);
                jukebox_service.get_playing_track_async(jukebox_id).then(
                    function(status) {
                        if (status.code === 200) {
                            $scope.player.cueVideoById({
                                'videoId': jukebox_service.get_track_playing().id,
                                'suggestedQuality': 'default'
                            });
                            $scope.player.seekTo(jukebox_service.get_track_playing().start_seconds);
                            //console.log($scope.player)
                        }else if (status.code === 403) {
                            ui.show_notification_warning('Server says: "' + status.message
                            + '" I asked the backend about the reason and replied: "' + status.info +'"');
                        }else if (status.code === 404) {
                            ui.show_notification_warning('The server did not respond with a playing track. Should I play something from the previous things? ')
                        }else{
                            ui.show_notification_error('Uknown error');
                        }
                        return;
                    },
                    function(status){
                        console.log('The server encountered an errror');
                        return;
                    }
                );
            };

            $scope.player_status =  function (){
                try {
                    var status = $scope.player.getPlayerState();
                    //console.log(status);
                    return status;
                }
                catch (e) {
                    // console.log(e); // pass exception object to error handler
                    return false;
                }
            };

            $scope.$on('handleStartPlaying', function(event, jukebox_id) {
                console.log('Got the message I ll play');
                $scope.start_playing(jukebox_id);
            });

            $scope.$on('handlePausePlaying', function() {
                console.log('Got the message I ll pause');
                $scope.player.pauseVideo();
            });

            $scope.$on('handleResumePlaying', function() {
                console.log('Got the message I ll resume');
                $scope.player.playVideo();
            });

            $scope.$on('handleStopPlaying', function() {
                console.log('Got the message I ll stop');
                $scope.player.stopVideo();
            });

        },
        link: function(scope, elm, attrs, ctrl) {

        }
    }
});

angular.module('mainApp.jukebox').factory('player_service', function($rootScope, $window) {

    var player_service = {};

     // This is called when the player is loaded from YT
    $window.onYouTubeIframeAPIReady = function() {
        player_service.player = new YT.Player('player', {
            height: '250',
            width: '400',
            playerVars: {
                'autoplay': 0,
                'controls': 1,
                'autohide': 2
            },
            events: {
                'onReady': player_service.onPlayerReady,
                'onStateChange': player_service.onPlayerStateChange,
                'onError': player_service.onError
            }
        });
        console.log(player_service.player);
    };

    // When the player has been loaded and is ready to play etc
    player_service.onPlayerReady = function (event) {
        $rootScope.$apply(function(){
            // Lets also broadcast a change state for the others to catch up
            player_service.broadcast_change_state({"state": player_service.player.getPlayerState()});
            // Should try to just load the track so that the users can press play on the playa
        });
    };

    // When the player changes a state
    player_service.onPlayerStateChange = function(event) {
        $rootScope.$apply(function(){
            console.log("Playa changed state");
            // unstarted
            if (player_service.player.getPlayerState() === -1){
                player_service.broadcast_change_state({
                    "state": -1,
                    "current_time": player_service.player.getCurrentTime()
                });
            }
            // ended
            if (player_service.player.getPlayerState() === 0){
                player_service.broadcast_change_state({
                    "state": 0,
                    "current_time": player_service.player.getCurrentTime()
                });
            }
            // playing
            if (player_service.player.getPlayerState() === 1){
                player_service.broadcast_change_state({
                    "state": 1,
                    "current_time": player_service.player.getCurrentTime()
                });
            }
            // paused
            if (player_service.player.getPlayerState() === 2){
                player_service.broadcast_change_state({
                    "state": 2,
                    "current_time": player_service.player.getCurrentTime()
                });
            }
            // buffering
            if (player_service.player.getPlayerState() === 3){
                player_service.broadcast_change_state({
                    "state": 3,
                    "current_time": player_service.player.getCurrentTime()
                });
            }
            // video cued
            if (player_service.player.getPlayerState() === 5){
                player_service.broadcast_change_state({
                    "state": 5,
                    "current_time": player_service.player.getCurrentTime()
                });
            }
        });
    };

    // When the player has been loaded and is ready to play etc
    player_service.onError = function(event) {
        $rootScope.$apply(function(){
            console.log("Playa Encountered and ERROR");
            console.log(event)
        });
    };

    // BroadCasts here
    player_service.broadcast_change_state = function(state){
        console.log("Broadcasting Player State change")
        $rootScope.$broadcast('handlePlayerChangedState', state);
    };

    player_service.broadcast_start_playing = function(jukebox_id) {
        $rootScope.$broadcast('handleStartPlaying', jukebox_id);
    };

    player_service.broadcast_pause_playing = function(jukebox_id) {
        $rootScope.$broadcast('handlePausePlaying');
    };

    player_service.broadcast_resume_playing = function(jukebox_id) {
        $rootScope.$broadcast('handleResumePlaying');
    };

    player_service.broadcast_stop_playing = function(jukebox_id) {
        $rootScope.$broadcast('handleStopPlaying');
    };

    player_service.getPlayer = function(){
        return player_service.player;
    }

    return player_service;

});