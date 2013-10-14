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
		});
	});