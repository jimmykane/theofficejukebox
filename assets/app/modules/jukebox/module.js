/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

'use strict';

 /*
 * Module - jukebox */

angular.module('mainApp.jukebox', [])
.config(function($locationProvider, $routeProvider) {
    $routeProvider.when('/jukebox/:jukebox_id', {
        templateUrl: '/assets/app/modules/jukebox/views/jukebox.html',
        controller: 'jukebox_controller',
        reloadOnSearch: false
    }).when('/jukeboxes/', {
        templateUrl: '/assets/app/modules/jukebox/views/jukeboxes.html',
        controller: 'jukeboxes_controller',
        reloadOnSearch: false
    });
});