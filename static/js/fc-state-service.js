(function() {
    'use strict';

    angular.module('flashcards.stateService', [])
        .service('StateService', StateService)
    ;

    StateService.$inject = ['$rootScope', '$window'];
    function StateService($rootScope, $window) {
        var service = this;
        service.loading = true;

        angular.element($window).bind('popstate', function(event) {
            event.preventDefault();
            $rootScope.$apply(function() {
                applyState(event.state);
            });
        });

        service.push = function(fn, url) {
            var rurl = fn();
            url = url || rurl;
            var state = getState();
            history.pushState(state, null, url);
        };
        service.replace = function(fn, url) {
            var rurl = fn();
            url = url || rurl;
            var state = getState();
            history.replaceState(state, null, url);
        };
        service.pop = function() {
            history.back();
        };
        service.reset = function(fn, url) {
            applyState({});
            history.go(-history.length);
            service.replace(fn, url);
        };

        function getState() {
            var state = {};
            for (var key in service) {
                if (service.hasOwnProperty(key) && !angular.isFunction(service[key])) {
                    state[key] = service[key];
                }
            }
            return state;
        }
        function applyState(state) {
            for (var key in service) {
                if (service.hasOwnProperty(key) && !angular.isFunction(service[key])) {
                    if (state.hasOwnProperty(key)) {
                        service[key] = state[key];
                        delete state[key];
                    } else {
                        delete service[key];
                    }
                }
            }
            for (var key in state) {
                if (state.hasOwnProperty(key) && !angular.isFunction(state[key])) {
                    service[key] = state[key];
                }
            }
        }
    }
})();
