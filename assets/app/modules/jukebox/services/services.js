/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

 "use strict";

 /* -------- *
 * SERVICES *
 * -------- */

/* jukebox_service */
angular.module('mainApp.jukebox').factory('jukebox_service', function($rootScope, $http, $q, logging) {

	var jukebox_service = {};
	var jukeboxes = [];
	var track_playing = {};


	/* jukebox: Get jukebox by id or by filters */
	jukebox_service.get_jukeboxes_async = function(jukebox_ids, filters) {
		// Defaults
		jukebox_ids = jukebox_ids || false;
		filters = filters || false;
		var deffered = $q.defer();
		$http.post('/AJAX/jukeboxes/get/', {
			"jukebox_ids" : jukebox_ids,
			'filters': filters
		})
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				return;
			}
			var new_jukeboxes = response.data;
			logging.ok("Got new jukeboxes", new_jukeboxes);
			for (var i = 0; i < new_jukeboxes.length; i++)
				jukebox_service.update_or_insert_jukebox(new_jukeboxes[i]);
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};


	/* queued_tracks: Get queued_track by id or by filters */
	jukebox_service.get_queued_tracks_async = function(jukebox, filters) {
		// Defaults
		var jukebox_id = jukebox.id || false;
		filters = filters || false;
		var deffered = $q.defer();
		$http.post('/AJAX/jukebox/get/queued_tracks', {
			"jukebox_id" : jukebox_id,
			'filters': filters
		})
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				return;
			}
			var queued_tracks = response.data;
			logging.ok("Got new queued tracks", queued_tracks);
			for (var i = 0; i < queued_tracks.length; i++)
				jukebox_service.update_or_insert_queued_track(jukebox, queued_tracks[i]);
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};


	/* jukebox_player: Start playing a track */
	jukebox_service.start_playing_async = function(jukebox_id, queued_track_id, seek) {
		var deffered = $q.defer();
		$http.post('/AJAX/jukebox/player/startplaying/',
			{
				'jukebox_id': jukebox_id,
				'queued_track_id': queued_track_id,
				'seek': seek
			}
		)
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				return;
			}
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};

	/* jukebox_player: Stop playing */
	jukebox_service.stop_playing_async = function(jukebox_id) {
		var deffered = $q.defer();
		$http.post('/AJAX/jukebox/player/stopplaying/',
			{
				'jukebox_id': jukebox_id,
			}
		)
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				//track_playing = {}; //reset
				return;
			}
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};

	/* jukebox: Get playing track */   // this  should be moved to the palyer service
	jukebox_service.get_playing_track_async = function(jukebox_id) {
		var deffered = $q.defer();
		$http.post('/AJAX/jukebox/get/playing_track',
			{
				'jukebox_id': jukebox_id,
			}
		)
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				track_playing.title = ''; //reset
				track_playing.duration = 0;
				return;
			}
			// Should do check eg first one is consumed
			angular.extend(track_playing, response.data);
			console.log(response.data);
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};


	/* jukebox: Save jukebox */
	jukebox_service.save_jukebox_async = function(jukebox) {
		var deffered = $q.defer();
		$http.post('/AJAX/jukebox/save/',
			 jukebox
		)
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				// Should restore old - Done
				jukebox_service.update_or_insert_jukebox(jukebox);
				deffered.resolve(response.status);
				return;
			}
			// Should do check eg first one is consumed
			jukebox = response.data;
			console.log(jukebox);
			jukebox_service.update_or_insert_jukebox(jukebox);
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};


	/* queued_track: Add new queued_track */
	jukebox_service.add_queued_track_async = function(jukebox, new_queued_track_video_id) {
		var deffered = $q.defer();
		$http.post('/AJAX/queued_track/save/', {
			"jukebox_id": jukebox.id,
			"video_id": new_queued_track_video_id
		})
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				return;
			}
			var queued_track = response.data;
			logging.ok("Track queued...", queued_track);
			jukebox_service.update_or_insert_queued_track(jukebox, queued_track);
			deffered.resolve(response.status);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};


	/* queued_track: remove_queued_track */
	jukebox_service.remove_queued_track_async = function(jukebox, queued_track, archive) {
		//console.log('here');
		var deffered = $q.defer();
		$http.post('/AJAX/queued_track/remove/', {
			"jukebox_id": jukebox.id,
			"queued_track_id": queued_track.id,
			"archive": archive
		})
		.success(function(response, status, headers, config) {
			if (response.status.code !== 200){
				deffered.resolve(response.status);
				return;
			}
			if (archive){
				queued_track.archived = true;
				 // Forcing it. Probably server is about 2sec earlier
				queued_track.edit_date = new Date();
			}else
				jukebox_service.remove_queued_track(jukebox, queued_track);
		})
		.error(function(response, status, headers, config) {
			deffered.reject(response.status);
			logging.error(response, status, headers, config);
		});
		return deffered.promise;
	};

	/* jukebox: Modification functions for jukebox array */
	jukebox_service.add_jukebox = function(jukebox) {
		jukeboxes.push(jukebox);
		return true;
	};

	jukebox_service.remove_jukebox = function(jukebox) {
		var index = jukeboxes.indexOf(jukebox);

		jukeboxes.splice(index, 1);
		return true;
	};

	jukebox_service.update_or_insert_jukebox = function(new_jukebox) {
		var found_position = jukebox_service.check_if_jukebox_id_exists(new_jukebox.id);
		if (found_position === false){
			jukebox_service.add_jukebox(new_jukebox);
			return true;
		}
		jukeboxes[found_position] = new_jukebox;
		return true;
	};

	jukebox_service.check_if_jukebox_id_exists = function(jukebox_id) {
		var jukebox_id = jukebox_id
		var found_position = false;
		for (var i = 0; i < jukeboxes.length; i++) {
			if (jukeboxes[i].id === jukebox_id)
				found_position = i;
		}
		return found_position;
	};

	jukebox_service.jukeboxes = function() {
		return jukeboxes;
	};

	jukebox_service.get_track_playing = function(){
		return track_playing;
	}


	jukebox_service.add_queued_track = function(jukebox, queued_track) {
		// Here I need to do the conversion to date obj from json string
		queued_track.creation_date = new Date(queued_track.creation_date)
		queued_track.edit_date = new Date(queued_track.edit_date)
		console.log(queued_track.edit_date)
		jukebox.queued_tracks.push(queued_track);
		return true;
	};
	jukebox_service.remove_queued_track = function(jukebox, queued_track) {
		var found_position = jukebox_service.check_if_queued_track_id_exists(jukebox, queued_track.id);
		if (found_position === false){
			return false;
		}
		jukebox.queued_tracks.splice(found_position, 1);
		return true;
	};
	jukebox_service.update_or_insert_queued_track = function(jukebox, new_queued_track) {
		// First check if it exists as an array and if not create it.
		jukebox.queued_tracks = jukebox.queued_tracks || [];
		var found_position = jukebox_service.check_if_queued_track_id_exists(jukebox, new_queued_track.id);
		if (found_position === false){
			jukebox_service.add_queued_track(jukebox, new_queued_track);
			return true;
		}
		jukebox.queued_tracks[found_position] = new_queued_track;
		jukebox.queued_tracks[found_position].creation_date = new Date(jukebox.queued_tracks[found_position].creation_date)
		jukebox.queued_tracks[found_position].edit_date = new Date(jukebox.queued_tracks[found_position].edit_date)
		return true;
	};

	jukebox_service.check_if_queued_track_id_exists = function(jukebox, queued_track_id) {
		console.log(queued_track_id)
		var queued_track_id = queued_track_id;
		var found_position = false;
		for (var i = 0; i < jukebox.queued_tracks.length; i++) {
			if (jukebox.queued_tracks[i].id === queued_track_id)
				found_position = i;
		}
		//console.log(found_position)
		return found_position;
	};

	//jukebox_service.start_playing = function() {
		//console.log(jukeboxes)
		//jukebox_service.broadcastNotification();
	//};

	//jukebox_service.broadcastNotification = function() {
		//$rootScope.$broadcast('handleStartPlaying');
	//};


	return jukebox_service;

});


/* Hehe this should be assembled elsewhere */
angular.module('mainApp.jukebox').factory('player_service', function($rootScope) {

	var player_service = {};

	// Just for the sake of it or future

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


	return player_service;
});