/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */
"use strict";

/* First define the modules
 * No dependancies so far we'll load that later.
*/

var mainApp = angular.module('mainApp', [
        'ngRoute',
        'ngAnimate',
        'mainApp.jukebox'
    ],
    function($interpolateProvider) {
        /* INTERPOLATION
        * Normal Angular {{}} now becomes {[{}]} so take care. */
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
});

/* Config */
mainApp.config(function($locationProvider, $routeProvider) {
    /*
     * Enabled HTML5 mode. Probably will not support
     * any browser especially < IE10
     */
    $locationProvider.html5Mode(true);
    $routeProvider.when('/', {
        templateUrl: '/assets/app/views/index.html',
        controller: 'index_controller'
    });
    $routeProvider.otherwise({redirectTo: '/404.html'}); // stub for production
});