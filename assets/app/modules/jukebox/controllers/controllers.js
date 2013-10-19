/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

"use strict";

/* ----------- */
/* CONTROLLERS */
/* ----------- */

/* slides_controller */
angular.module('mainApp.jukebox').controller('jukebox_controller', function($scope, $location, $routeParams, $timeout, users_service, jukebox_service, ui, logging, player_service) {

	// All these need rearrangement
	$scope.jukebox_id = $routeParams.jukebox_id;
	//logging.info("Requested JukeBox ID", $scope.jukebox_id);
	$scope.jukeboxes = jukebox_service.jukeboxes();
	$scope.user = users_service.user();
	$scope.user.logged_in = users_service.user_is_logged_in();
	$scope.track_playing = jukebox_service.get_track_playing();
	$scope.new_queued_track = {};
	$scope.player_status = false;
	$scope.player_status.state = -1;

	/* Function to check if the logged in user is the same with the jukebox owner */
	$scope.is_owner = function(user, jukebox){
		if (!user.id)
			return false
		if (user.id === jukebox.owner_key_id)
			return true;
		return false;
	};

	/* Funtion to convert query param slide_id to int */
	$scope.current_jukebox_id = function(){
		// stub for getting id
		return jukeboxes[0]
		var current_jukebox_id = $location.search().jukebox_id;
		if (!current_jukebox_id)
			return false;
		return current_jukebox_id;
	};


	/* jukebox_player: Send command to start playing specific track at specific time*/
	$scope.start_playing_queued_track = function(jukebox, queued_track_id, seek, autostart) {
		jukebox_service.start_playing_async(jukebox.id, queued_track_id, seek).then(
			function(status) {
				if (status.code === 200) {
					// If all went well the player dictates start
					console.log('Found track to play');
					$scope.get_playing_track(jukebox);
					jukebox.player.on=true;
					$scope.get_queued_tracks(jukebox, {
						'archived': true,
						'order': 'edit_date',
						'short_desc': true
					});

					if (autostart)
						$scope.start_playing(jukebox);

				}else if (status.code === 403) {
					ui.show_notification_warning('Server says: "' + status.message
					+ '" I asked the backend about the reason and replied: "' + status.info +'"');
				}else if (status.code === 404) {
					ui.show_notification_warning('He is talking again about 404\'s and shit...')
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


	/* Find the jukebox total play time */
	$scope.get_jukebox_total_play_duration = function(jukebox){
		var total_play_time = 0;
		if (!jukebox.queued_tracks)
			return total_play_time;
		for (var i=0; jukebox.queued_tracks.length > i; i++){
			total_play_time = total_play_time + jukebox.queued_tracks[i].duration;
		}
		return total_play_time;
	};


	/* slide: Get Current Playing track */
	$scope.get_playing_track = function(jukebox) {
		jukebox_service.get_playing_track_async(jukebox.id).then(
			function(status) {
				if (status.code === 200) {
					console.log('playing track found');
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


	/* slide: Get jukeboxes according */
	$scope.get_jukeboxes = function(jukebox_ids, filters) {
		jukebox_service.get_jukeboxes_async(jukebox_ids, filters).then(
			function(status) {
				if (status.code === 200) {
					//stub
					$scope.get_playing_track($scope.jukeboxes[0]);
					$scope.get_queued_tracks($scope.jukeboxes[0], {
						'archived': false
					});
					$scope.get_queued_tracks($scope.jukeboxes[0], {
						'archived': true,
						'order': 'edit_date',
						'short_desc': true
					});
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
				logging.error('The server encountered an errror');
				return;
			}
		);
	};


	/* queued_track: Get queued_tracks according */
	$scope.get_queued_tracks = function(jukebox, filters) {
		jukebox_service.get_queued_tracks_async(jukebox, filters).then(
			function(status) {
				if (status.code === 200) {

				}else if (status.code === 403) {
					ui.show_notification_warning('Server says: "' + status.message
					+ '" I asked the backend about the reason and replied: "' + status.info +'"');
				}else if (status.code === 404) {
					ui.show_notification_warning('Sorry ququed_tracks NOT found');

				}else{
					ui.show_notification_error('Error Undocumented status code');
				}
				return;
			},
			function(status){
				logging.error('The server encountered an errror');
				return;
			}
		);
	};


	/* queued_track: Add single queued_track */
	$scope.add_new_queued_track = function(jukebox, video_id) {

		var playerRegExp= /(http:\/\/|https:\/\/)www\.youtube\.com\/watch\?v=([A-Za-z0-9\-\_]+)/;
		var video_id = video_id || false;
		console.log(video_id)
		if (!video_id)
			var match_groups  = $scope.new_queued_track.video_url.match(playerRegExp);

		if (match_groups && match_groups.length > 2 && video_id==false)
			video_id = match_groups[2];

		if (!video_id){
			ui.show_notification_warning('Sorry could not add the track check the shit you pasted and try again. I did my best...');
			$scope.new_queued_track.video_url = '';
			return false;
		}

		jukebox_service.add_queued_track_async(jukebox, video_id).then(
			function(status) {

				if (status.code === 200) {
					ui.show_notification_info('Track added to queue... Enjoy');
					$scope.new_queued_track.video_url = '';
				}else if (status.code === 400) {
					ui.show_notification_error('Bad request. Parameters are invailid... ? Are we serious here ?');
				}else if (status.code === 401) {
					ui.show_notification_warning('Unauthorized. Probably you are logged out... :-(');
				}else if (status.code === 403) {
					ui.show_notification_warning('Server says: "' + status.message
					+ '" I asked the backend about the reason and replied: "' + status.info +'"');
				}else if (status.code === 404) {
					ui.show_notification_warning('Sorry the track was not found? Is that possible? Copy paste after you visit');
				}else{
					ui.show_notification_warning('I have no fucking idea what went wrong. It\'s logged though... hopefully... at the server backlogs...');
				}
				return;

			},
			function(status){
				logging.error('[!!] ADD/QueuedTrack: The server encountered an errror');
				return;
			}
		);;
	};


	/* jukebox: save single jukebox */
	$scope.save_jukebox = function(jukebox) {
		//console.log('saving', jukebox);
		jukebox_service.save_jukebox_async(jukebox).then(
			function(status) {
				// GUI HERE
				if (status.code === 200) {
					$scope.get_jukeboxes([jukebox.id]);
					ui.show_notification_info('Jukebox changed state');
				}else if (status.code === 403) {
					ui.show_notification_warning('hmmmm ' + status.message);
				}else if (status.code === 404) {
					ui.show_notification_warning('It was not found?');
				}else{
					ui.show_notification_warning('Something undocumented happeend... wtf...');
				}
				return;
			},
			function(status){
				ui.show_notification_warning('The backend encountered an error. That\'s wierd.. >:| ');
				return;
			}
		);
	};


	/* queued_track: Remove single track */
	$scope.remove_queued_track = function(jukebox, queued_track, archive) {
		jukebox_service.remove_queued_track_async(jukebox, queued_track, archive).then(
			function(status) {
				// GUI HERE
				if (status.code === 200) {
					if (archive)
						ui.show_notification_info('Queued Track Removed from queue');
					else
						ui.show_notification_info('Queued Track Deleted!!!');
				}else if (status.code === 401) {
					ui.show_notification_warning('Hey!!! You are not authorized to do this...');
				}else if (status.code === 403) {
					ui.show_notification_warning('hmmmm ' + status.message);
				}else if (status.code === 404) {
					ui.show_notification_warning('It was not found?');
				}else{
					ui.show_notification_warning('Something undocumented happeend... wtf...');
				}
				return;
			},
			function(status){
				ui.show_notification_warning('The backend encountered an error. That\'s wierd.. >:| ');
				return;
			}
		);
	};

	// Contains a lot of $scope.jukeboxes[0] stubs. take care
	$scope.$on('handlePlayerChangedState', function(event, state) {

		logging.info('Player changed state', state);
		var prev_state = false;
		if ($scope.player_status.state)
			prev_state = $scope.player_status.state;

		//-1 (unstarted), 0 (ended), 1 (playing), 2 (paused), 3 (buffering), 5(video cued)
		// seeking 1, 2, 1
		// Start playing -1, 5, 1

		console.log('prev state', prev_state);
		console.log('new state', state.state);

		// First actions when it's not an admin/owner
		if ($scope.is_owner($scope.user, $scope.jukeboxes[0]) === false){

		}

		// Then if he is admin/owner
		if ($scope.is_owner($scope.user, $scope.jukeboxes[0]) === true){
			if (prev_state === 1 && state.state === 2){// seeking or stop or end
				// if ended I have to detect it. it's going to be almost the same duration so -1s
				if (state.current_time < ($scope.track_playing.duration - 1))
					$scope.stop_playing($scope.jukeboxes[0]);
			}
			if (prev_state === 2 && state.state === 1)// from paused or seek to apply play
				$scope.start_playing_queued_track($scope.jukeboxes[0], $scope.track_playing.id, state.current_time + 2, false);
		}

		// Last common actions
		if (prev_state === 2 && state.state === 0){//ended and now?
			console.log('Going to next')
			$scope.get_queued_tracks($scope.jukeboxes[0], {
				'archived': false,
			});
			$scope.get_queued_tracks($scope.jukeboxes[0], {
				'archived': true,
				'order': 'edit_date',
				'short_desc': true
			});
			$scope.start_playing($scope.jukeboxes[0]);
		}

		// Finally cahnge the state...
		$scope.player_status = state;

	});

	$scope.start_playing = function(jukebox){
		player_service.broadcast_start_playing(jukebox.id);
	};

	$scope.pause_playing = function(jukebox){
		player_service.broadcast_pause_playing(jukebox.id);
	};

	$scope.resume_playing = function(jukebox){
		player_service.broadcast_resume_playing(jukebox.id);
	};


	$scope.stop_playing = function(jukebox){
		jukebox_service.stop_playing_async(jukebox.id).then(
			function(status) {
				if (status.code === 200) {
					console.log('Stopping video');
					jukebox.player.on = false;
					//player_service.broadcast_stop_playing(jukebox.id);
				}else if (status.code === 401) {
					ui.show_notification_warning('Unauthorized!!!');
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


	///* Hack function to force a change if no change in search */
	//$scope.go_to_slide_id = function(slide_id){
		//if ($scope.current_slide_id() === slide_id) // If yes force!
			//$scope.$emit('$locationChangeSuccess');
		//else // Or else just change the location search trigger the routeupdate
			//$location.search({'slide_id': slide_id})
	//};


	///* Setup to detect when there is a change in the search */
	//$scope.$on('$routeUpdate', function(next, current) {
		//var slide_id = $location.search().slide_id;
		//$scope.display_slide_id(slide_id);
	//});


	$scope.get_jukeboxes();

	$scope.duration_to_HHMMSS = function (duration) {
		if (!duration)
			return null;
		var sec_num = parseInt(duration, 10); // don't forget the second parm
		var hours   = Math.floor(sec_num / 3600);
		var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
		var seconds = sec_num - (hours * 3600) - (minutes * 60);

		if (hours   < 10) {hours   = "0" + hours;}
		if (minutes < 10) {minutes = "0" + minutes;}
		if (seconds < 10) {seconds = "0" + seconds;}
		//var time    = hours + ':' + minutes + ':' + seconds;
		var time = minutes + ':' + seconds;
		return time;
	}


});
