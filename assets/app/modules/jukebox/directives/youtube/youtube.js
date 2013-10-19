/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

"use strict";

angular.module('mainApp.jukebox').directive('youTube', function($window, logging, ui, jukebox_service, player_service) {
	return {
		restrict: 'A', // only activate on element attribute
		scope: true, // New scope to use but rest inherit from parent
		controller: function($scope, $element, $attrs) {

			// This is called when the player is loaded from YT
			$window.onYouTubeIframeAPIReady = function() {
				$scope.player = new YT.Player('player', {
					height: '100',
					width: '350',
					playerVars: {
						'autoplay': 0,
						'controls': 1,
						'autohide': 2
					},
					//videoId: $scope.live_track.video_id,
					events: {
						'onReady': $scope.onPlayerReady,
						'onStateChange': $scope.onPlayerStateChange
					}
				});
			};

			// When the player has been loaded and is ready to play etc
			$scope.onPlayerReady = function (event) {
				$scope.$apply(function(){
					logging.info("Playa is ready");
					logging.info($scope.player);
					$scope.player.controls = 0; //wtf doesnt it work?
					// Lets also broadcast a change state for the others to catch up
					player_service.broadcast_change_state({"state": $scope.player.getPlayerState()});
				});
			};

			// When the player changes a state
			$scope.onPlayerStateChange = function(event) {
				$scope.$apply(function(){

					console.log("Playa changed state");
					// unstarted
					if ($scope.player.getPlayerState() === -1){
						player_service.broadcast_change_state({"state": -1});
					}
					// ended
					if ($scope.player.getPlayerState() === 0){
						player_service.broadcast_change_state({"state": 0});
					}
					// playing
					if ($scope.player.getPlayerState() === 1){
						player_service.broadcast_change_state({
							"state": 1,
							"current_time": $scope.player.getCurrentTime()
						});
					}
					// paused
					if ($scope.player.getPlayerState() === 2){
						player_service.broadcast_change_state({
							"state": 2,
							"current_time": $scope.player.getCurrentTime()
						});
					}
					// buffering
					if ($scope.player.getPlayerState() === 3){
						player_service.broadcast_change_state({"state": 3});
					}
					// video cued
					if ($scope.player.getPlayerState() === 5){
						player_service.broadcast_change_state({
							"state": 5,
							"current_time": $scope.player.getCurrentTime()
						});
					}

				});
			};


			// When the player has been loaded and is ready to play etc
			$scope.onError = function (event) {
				$scope.$apply(function(){
					logging.info("Playa Encountered and ERROR");
					logging.info(event)
				});
			};


			$scope.start_playing = function (jukebox_id){
				logging.info('Yes I am starting...');
				jukebox_service.get_playing_track_async(jukebox_id).then(
					function(status) {
						if (status.code === 200) {
							$scope.player.cueVideoById({
								'videoId': jukebox_service.get_track_playing().id,
								'suggestedQuality': 'default'
							});
							$scope.player.seekTo(jukebox_service.get_track_playing().start_seconds);

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
						logging.error('The server encountered an errror');
						return;
					}
				);
			};


			$scope.player_status =  function (){

				try {
					var status = $scope.player.getPlayerState();
					console.log(status);
					return status;
				}
				catch (e) {
					// probably this happens a lot due to several apply digest cirlces
					// logging.info(e); // pass exception object to error handler
					return false;
				}

			};

			$scope.$on('handleStartPlaying', function(event, jukebox_id) {
				logging.info('Got the message I ll play');
				$scope.start_playing(jukebox_id);
			});

			$scope.$on('handlePausePlaying', function() {
				logging.info('Got the message I ll pause');
				$scope.player.pauseVideo();
			});

			$scope.$on('handleResumePlaying', function() {
				logging.info('Got the message I ll resume');
				$scope.player.playVideo();
			});


			$scope.$on('handleStopPlaying', function() {
				logging.info('Got the message I ll stop');
				$scope.player.stopVideo();
			});


		},
		link: function(scope, elm, attrs, ctrl) {

			// Load the Yotube js api
			var tag = document.createElement('script');
			tag.src = "https://www.youtube.com/iframe_api";
			var firstScriptTag = document.getElementsByTagName('script')[0];
			firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

		}
	}
});