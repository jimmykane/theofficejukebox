/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

"use strict";

/* ----------- */
/* CONTROLLERS */
/* ----------- */


/* notifications_controller
 * Basically its a shared controller that gets commands from the notifications service
 * which is shared as well.
 * */
mainApp.controller('notifications_controller', function($scope, $timeout, notifications_service) {

	$scope.notifications = [];

	$scope.timeouts = {
		'info': 5000, //5000 in css
		'warning': 6200, //6200 in css
		'error': 9400 //9400 in css
	};

	$scope.$on('handleNotification', function() {

		var notification = {
			'message': notifications_service.message,
			'type': notifications_service.type
		};
		// Here switch on type
		// and fire call back with timer
		$scope.notifications.push(notification);
		// after displaying a bit find and destroy it from the dom as well please its in repeat
		$timeout(function(){
			var index = $scope.notifications.indexOf(notification);
			$scope.notifications.splice(index, 1);
		},$scope.timeouts[notification.type]);
	});

});


/* user_controller */
mainApp.controller('user_controller', function($location, $scope, users_service, logging,ui) {

	$scope.user = users_service.user();
	$scope.url = $location.absUrl();

	/* GET current user */
	$scope.get_current_user = function() {
		users_service.get_current_user_async().then(
			function(status) {
				// GUI Here
				if (status.code === 200) {
					//ui.show_notification_info('[OK] GET/User: Found');
				}else if (status.code === 404) {
					//ui.show_notification_warning('[W] GET/User: Sorry the user was NOT found');
					$scope.user = false;
				}else{
					ui.show_notification_warning('[W] GET/User: Error Undocumented status code');
					$scope.user = false;
				}
				return;
			},
			function(status){
				logging.error('[!!] GET/User: The server encountered an errror');
				return;
			}
		);
	}
	$scope.get_current_user();
});