(function() {
    'use strict';

    angular.module('flashcards', [
        // angular modules
        'ngAnimate',
        // flashcards modules
        'flashcards.focuson', 'flashcards.stateService', 'flashcards.tagInput',
        'flashcards.onenter'])
        .controller('LoginController', LoginController)
        .controller('OptionsController', OptionsController)
        .config(ConfigureApp)
        .run(InitialiseApp)
    ;

    ConfigureApp.$inject = ['$locationProvider'];
    function ConfigureApp($locationProvider) {
        $locationProvider.html5Mode(true);
    }

    InitialiseApp.$inject = ['$http', '$location', '$rootScope', '$timeout', 'StateService'];
    function InitialiseApp($http, $location, $rootScope, $timeout, state) {
        $http.defaults.xsrfCookieName = '_xsrf';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.headers.delete = {'Content-Type' : 'application/json'};

        $rootScope.state = state;
        $http.get('/init').success(function(data) {
            $timeout(function() {
                state.replace(function() {
                    state.loading = false;
                    if (!data.user) {
                        state.section = 'login';
                        return '/';
                    } else {
                        var path = $location.path().split('/');
                        while (path.length > 0 && path[path.length - 1] === "") {
                            path.pop();
                        }
                        if (path.length) {
                            state.section = path[path.length - 1];
                        } else {
                            state.section = 'home';
                        }
                        state.user = data.user;
                        return path.join('/') + '/';
                    }
                });
            }, 1000 - performance.now());
        });
    }

    LoginController.$inject = ['$http', 'StateService'];
    function LoginController($http, state) {
        var ctrl = this;

        ctrl.submit = function() {
            if (!state.create_user) {
                $http.post('/login', {
                    username: ctrl.username,
                    password: ctrl.password
                }).success(function(data) {
                    state.replace(function() {
                        state.section = 'home';
                        delete state.create_user;
                        state.user = data.user;
                    });
                }).error(function(data) {
                    if (data.message === "no_such_username") {
                        state.push(function() {
                            state.create_user = true;
                        });
                    }
                });
            } else {
                $http.post('/signup', {
                    username: ctrl.username,
                    password: ctrl.password,
                    name: ctrl.name
                }).success(function(data) {
                    state.replace(function() {
                        state.section = 'home';
                        delete state.create_user;
                        state.user = data.user;
                    });
                }).error(function(data) {
                    state.pop();
                });
            }
        };
    }

    OptionsController.$inject = ['$http', 'StateService'];
    function OptionsController($http, state) {
        var ctrl = this;

        this.logout = function() {
            $http.post('/logout').finally(function() {
                state.reset(function() {
                    state.section = 'login'
                });
            });
        };
        this.setup = function() {
            state.push(function() {
                state.section = 'setup'
            }, '/setup/');
        };
        this.start = function() {
            state.push(function() {
                state.section = 'session'
            });
        };
    }
})();
