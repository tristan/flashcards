(function() {
    'use strict';

    angular.module('flashcards')
        .directive('fcCards', CardsDirective)
        .directive('fcTimeSince', TimeSinceDirective)
    ;

    CardsDirective.$inject = ['$window'];
    function CardsDirective($window) {
        var w = angular.element($window);
        return {
            controllerAs: 'ctrl',
            controller: SessionController,
            link: function($scope, $element, $attrs, ctrl) {
                w.bind('keypress', handleKeypress);
                $scope.$on('$destroy', function() {
                    w.unbind('keypress', handleKeypress);
                });

                function handleKeypress(event) {
                    if (event.which === 13 && ctrl.state !== 'answering') {
                        ctrl.changeCard();
                    }
                }
            }
        };
    }

    SessionController.$inject = ['$scope', '$http', '$q', '$timeout', 'StateService'];
    function SessionController($scope, $http, $q, $timeout, state) {
        var ctrl = this;

        var session_id;

        ctrl.state = 'answering';

        $http.post('/api/session').success(function(data) {
            session_id = data.session_id;
            ctrl.session_start = Date.now();
            ctrl.card = data.card;
            ctrl.card_count = 0;
            ctrl.correct = 0;
        });

        this.checkAnswer = function(value) {
            var correct;
            if (ctrl.card.back.case_sensitive) {
                correct = value === ctrl.card.back.text;
            } else {
                correct = value.toLowerCase() === ctrl.card.back.text.toLowerCase();
            }
            $scope.$apply(function() {
                if (correct) {
                    ctrl.correct += 1;
                }
                ctrl.card_count += 1;
                ctrl.state = correct ? 'correct' : 'incorrect';
            });
            ctrl.next_card = $q.defer();
            $http.put('/api/session', {
                card_id: ctrl.card.card_id,
                success: correct
            }).success(function(data) {
                ctrl.next_card.resolve(data.card);
            });
        };

        this.changeCard = function() {
            if (ctrl.next_card) {
                ctrl.next_card.promise.then(function(card) {
                    ctrl.state = 'answering';
                    ctrl.answer = '';
                    ctrl.card = card;
                    ctrl.next_card = null;
                });
            } else {
            }
        };

        this.stop = function() {
            ctrl.session_end = Date.now();
            ctrl.state = 'stopped';
            $http.delete('/api/session');
        };
    }

    function getTimeSince(time, now) {
        now = now || Date.now();
        var ms = now - time;
        var s = ms / 1000; ms %= 1000;
        var m = s / 60; s %= 60;
        var h = m / 60; m %= 60;
        var d = h / 24; h %= 24;
        var w = d / 7; d %= 7;
        var y = w / 52; w %= 52;
        var result = [];
        if (y >= 1) {
            y = Math.floor(y);
            result.push(y + "y");
        }
        if (w >= 1) {
            w = Math.floor(w);
            result.push(w + "w");
        }
        if (d >= 1) {
            d = Math.floor(d);
            result.push(d + "d");
        }
        if (h >= 1) {
            h = Math.floor(h);
            result.push(h + "h");
        }
        if (m >= 1) {
            m = Math.floor(m);
            result.push(m + "m");
        }
        result.push(Math.floor(s) + "s");
        return result.join(" ");
    }

    TimeSinceDirective.$inject = ['$interval', '$parse'];
    function TimeSinceDirective($interval, $parse) {
        return function($scope, $element, $attrs) {
            if (!$attrs.start) {
                return;
            }
            var sfn = $parse($attrs.start);
            var efn, wkill, ikill;
            if ($attrs.end) {
                efn = $parse($attrs.end);
                wkill = $scope.$watch(efn, update);
            } else {
                efn = Date.now;
                ikill = $interval(update, 1000);
            }
            $scope.$on("$destroy", function tsdD() {
                if (ikill) {
                    $interval.cancel(ikill);
                } else if (wkill) {
                    wkill();
                }
            });
            function update() {
                $element.html(getTimeSince(sfn($scope), efn($scope)));
            }
        };
    }

})();
