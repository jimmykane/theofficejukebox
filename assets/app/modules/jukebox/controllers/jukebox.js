/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

"use strict";

angular.module('mainApp.jukebox').controller('jukebox_controller', function($scope, $location, $routeParams, $timeout, users_service, jukebox_service, ui, player_service) {

    $scope.jukebox_id = $routeParams.jukebox_id;
    console.log($scope.jukebox_id)
    $scope.jukeboxes = jukebox_service.jukeboxes();
    $scope.user = users_service.user();
    $scope.track_playing = jukebox_service.get_track_playing();
    $scope.new_queued_track = {};
    $scope.player_status = false;
    $scope.player_status.state = -1;
    $scope.jukebox = false;
    $scope.membership_types = {
            'admins': ['admin','owner'],
            'members': ['admin','owner', 'member']
    };

    $scope.get_current_jukebox = function(){
        console.log('Getting current jukebox');
        if (!$scope.jukebox_id)
            return false;
        var found = jukebox_service.check_if_jukebox_id_exists($scope.jukebox_id);
        if (found === false)
            return false;
        $scope.jukebox = $scope.jukeboxes[found];
        return $scope.jukeboxes[found];
    };

    $scope.is_owner_or_admin = function(user, jukebox){
        //console.log("Security Check");
        if (!user.id || !user.memberships)
            return false;
        if (user.is_admin) // bad
            return true;
        for (var i=0; i < user.memberships.length; i++ ){
            if (user.memberships[i].jukebox_id === jukebox.id
            && $scope.membership_types.admins.indexOf(user.memberships[i].type) !== -1){
                user.is_admin = true;
                return true;
            }
        }
        return false;
    };

    $scope.is_member = function(user, jukebox){
        //console.log("Security check", user);
        if (!user.id || !user.memberships)
            return false;
        if (user.is_member)  // bad
            return true;
        for (var i=0; i < user.memberships.length; i++ ){
            if (user.memberships[i].jukebox_id === jukebox.id
            && $scope.membership_types.members.indexOf(user.memberships[i].type) !== -1){
                user.is_member = true;
                return true;
            }
        }
        return false;
    };

    $scope.start_playing_queued_track = function(jukebox, queued_track_id, seek, autostart) {
        jukebox_service.start_playing_async(jukebox.id, queued_track_id, seek).then(
            function(status) {
                if (status.code === 200) {
                    // If all went well the player dictates start
                    //console.log('Found track to play');
                    $scope.get_playing_track(jukebox);
                    jukebox.player.on=true;

                    if (!autostart)
                        return;
                    $scope.start_playing(jukebox);
                    $scope.get_queued_tracks(jukebox, {
                        'archived': true,
                        'order': 'edit_date',
                        'short_desc': true
                    });
                }else if (status.code === 401) {
                    ui.show_notification_warning('You cann\'t start this....');
                }else if (status.code === 403) {
                    ui.show_notification_warning('Server says: "' + status.message
                    + '" I asked the backend about the reason and replied: "' + status.info +'"');
                }else if (status.code === 404) {
                    ui.show_notification_warning('He is talking again about 404\'s and shit...');
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

    $scope.get_jukebox_total_play_duration = function(jukebox, archived){
        var total_play_time = 0;
        if (!jukebox || !jukebox.queued_tracks)
            return total_play_time;
        for (var i=0; jukebox.queued_tracks.length > i; i++){
            if (jukebox.queued_tracks[i].archived === archived)
                total_play_time = total_play_time + jukebox.queued_tracks[i].duration;
        }
        return total_play_time;
    };

    $scope.get_playing_track = function(jukebox) {
        jukebox_service.get_playing_track_async(jukebox.id).then(
            function(status) {
                if (status.code === 200) {
                    ui.show_notification_info('Now playing: ' + $scope.track_playing.title)
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

    $scope.get_jukeboxes = function(jukebox_ids, filters) {
        jukebox_service.get_jukeboxes_async(jukebox_ids, filters).then(
            function(status) {
                if (status.code === 200) {
                    // Try to set the current one
                    var current_jukebox = $scope.get_current_jukebox();
                    $scope.get_playing_track(current_jukebox);
                    $scope.get_queued_tracks(current_jukebox, {
                        'archived': false
                    });
                    $scope.get_queued_tracks(current_jukebox, {
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
                console.log('The server encountered an errror');
                return;
            }
        );
    };

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
                console.log('The server encountered an errror');
                return;
            }
        );
    };

    $scope.get_memberships = function(jukebox) {
        jukebox_service.get_memberships_async(jukebox).then(
            function(status) {
                if (status.code === 200) {

                }else if (status.code === 403) {
                    ui.show_notification_warning('Server says: "' + status.message
                    + '" I asked the backend about the reason and replied: "' + status.info +'"');
                }else if (status.code === 404) {
                    ui.show_notification_warning('Sorry memberships NOT found');

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

    $scope.save_membership = function(membership) {
        jukebox_service.save_membership_async(membership).then(
            function(status) {
                if (status.code === 200) {

                }else if (status.code === 401) {
                    ui.show_notification_warning('Nope not allowed bitchy...');
                }else if (status.code === 403) {
                    ui.show_notification_warning('Server says: "' + status.message
                    + '" I asked the backend about the reason and replied: "' + status.info +'"');
                }else if (status.code === 404) {
                    ui.show_notification_warning('Sorry memberships NOT found');
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

    $scope.request_membership = function(jukebox) {
        jukebox_service.request_membership_async(jukebox.id).then(
            function(status) {
                if (status.code === 200) {

                }else if (status.code === 401) {
                    ui.show_notification_warning('Probably not logged in');
                }else if (status.code === 403) {
                    ui.show_notification_warning('Server says: "' + status.message
                    + '" I asked the backend about the reason and replied: "' + status.info +'"');
                }else if (status.code === 404) {
                    ui.show_notification_warning('Sorry something was not found');
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

    $scope.approve_membership = function(membership) {
        membership.type = 'member';
        $scope.save_membership(membership);
    }

    $scope.add_new_queued_track = function(jukebox, video_id) {

        var playerRegExp= /(http:\/\/|https:\/\/)www\.youtube\.com\/watch\?v=([A-Za-z0-9\-\_]+)/;
        var video_id = video_id || false;
        //console.log(video_id)
        if (!video_id && $scope.new_queued_track.video_url) // fix it
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
                console.log('[!!] ADD/QueuedTrack: The server encountered an errror');
                return;
            }
        );;
    };

    $scope.save_jukebox = function(jukebox) {
        jukebox_service.save_jukebox_async(jukebox).then(
            function(status) {
                if (status.code === 200) {
                    $scope.get_jukeboxes([jukebox.id]);
                    ui.show_notification_info('Jukebox changed state');
                }else if (status.code === 401) {
                    ui.show_notification_warning('Unauthorized... Nope dont do that ' + status.message);
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

    $scope.remove_queued_track = function(jukebox, queued_track, archive) {
        jukebox_service.remove_queued_track_async(jukebox, queued_track, archive).then(
            function(status) {
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

    $scope.$on('handlePlayerChangedState', function(event, state) {

        //console.log('Player changed state', state);
        var prev_state = false;
        var current_jukebox = $scope.get_current_jukebox();
        if (!current_jukebox)
            return;
        if ($scope.player_status.state)
            prev_state = $scope.player_status.state;
        //-1 (unstarted), 0 (ended), 1 (playing), 2 (paused), 3 (buffering), 5(video cued)
        // seeking 1, 2, 1 and not sure
        // Start playing -1, 5, 1 and not sure
        //console.log('prev state', prev_state);
        //console.log('new state', state.state);
        if ($scope.is_owner_or_admin($scope.user, current_jukebox) === false){

        }
        if ($scope.is_owner_or_admin($scope.user, current_jukebox) === true){
            // Seeking or stop or end
            if (prev_state === 1 && state.state === 2 ){
                // If ended I have to detect it.
                // This doesnt work that well. It passes through here many times
                //$scope.stop_playing(current_jukebox);
            }
            // From paused or seek to apply play
            if (prev_state === 2 && state.state === 1){
                // This goes wrong as well.
                //$scope.start_playing_queued_track(current_jukebox , $scope.track_playing.id, state.current_time, false);
            }
        }
        // If from buffering or paused to end then request next
        if ((prev_state === 2 || prev_state === 3) && state.state === 0){
            //console.log('Going to next')
            $scope.get_queued_tracks(current_jukebox, {
                'archived': false
            });
            $scope.get_queued_tracks(current_jukebox, {
                'archived': true,
                'order': 'edit_date',
                'short_desc': true
            });
            $scope.start_playing(current_jukebox);
        }
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
                    //console.log('Stopping video');
                    jukebox.player.on = false;
                }else if (status.code === 401) {
                    ui.show_notification_warning('Unauthorized!!! How the hell did you get access to this command. Mind it!!!');
                }else if (status.code === 403) {
                    ui.show_notification_warning('Server says: "' + status.message
                    + '" I asked the backend about the reason and replied: "' + status.info +'"');
                }else if (status.code === 404) {
                    ui.show_notification_warning('Sorry but the jukebox was not found...')
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

    // This should be moved to a service or something
    $scope.track_playing_timer = function(msecs){
        //console.log($scope.track_playing)
        //if $scope.player_status.current_time
        var timeoutId = $timeout(function() {
            $scope.track_playing_timer(msecs); // schedule another update
        }, msecs);
        if ($scope.track_playing
            && $scope.track_playing.start_seconds < $scope.track_playing.duration)
            $scope.track_playing.start_seconds = $scope.track_playing.start_seconds + msecs/1000;
        // Nice idea it to put SAFE triggers here to get next etc
        // That would need futher implementation of this this as a service or so
    }

    if ($scope.jukebox_id){
        $scope.get_jukeboxes([$scope.jukebox_id]);
        //$scope.track_playing_timer(1000);
    }else{
        $location.path('115442273060497622362')
    }

    /* Help function. */
    $scope.duration_to_HHMMSS = function (duration) {
        if (duration === false)
            return null;
        var sec_num = parseInt(duration, 10); // don't forget the second parm
        var hours   = Math.floor(sec_num / 3600);
        var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
        var seconds = sec_num - (hours * 3600) - (minutes * 60);

        if (hours  < 10) {hours   = "0" + hours;}
        if (minutes < 10) {minutes = "0" + minutes;}
        if (seconds < 10) {seconds = "0" + seconds;}
        var time    = hours + ':' + minutes + ':' + seconds;
        if (hours  < 1)
            time = minutes + ':' + seconds;
        return time;
    }

});