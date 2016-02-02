(function() {
    'use strict';

    angular.module('flashcards')
        .directive('fcKeywordCards', CardsDirective)
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
                    console.log(event.keyCode);
                    if (event.keyCode == 32 || event.keyCode == 13) {
                        $scope.$apply(ctrl.showBack);
                    } else if (ctrl.state == 'back' && event.keyCode == 43) { // +
                        ctrl.scoreCard(true);
                    } else if (ctrl.state == 'back' && event.keyCode == 45) { // -
                        ctrl.scoreCard(false);
                    }
                }
            }
        };
    }

    function data2card(data) {
        if (data.hasOwnProperty('frame')) {
            var frame = data.frame;
            return {
                card_id: frame.frame_id,
                type: 'frame',
                back: {
                    language: "漢字",
                    text: frame.kanji
                },
                front: {
                    text: frame.keyword,
                    language: "keyword"
                }
            }
        }
    }

    function card2config(card, success) {
        if (card.type == 'frame') {
            return {
                type: 'frame',
                frame_id: card.card_id,
                success: success
            };
        }
    }

    SessionController.$inject = ['$scope', '$http', '$q', '$timeout', 'StateService'];
    function SessionController($scope, $http, $q, $timeout, state) {
        var ctrl = this;

        var session_id;

        ctrl.state = 'front';

        $http.post('/api/session', {type: 'keyword'}).success(function(data) {
            session_id = data.session_id;
            ctrl.session_start = Date.now();
            ctrl.card = data2card(data);
            ctrl.card_count = 0;
            ctrl.correct = 0;
        });

        this.showBack = function() {
            ctrl.state = 'back';
        }

        this.scoreCard = function(correct) {
            var next_card = $q.defer();
            $http.put('/api/session', card2config(ctrl.card, correct))
                .success(function(data) {
                    ctrl.card_count += 1;
                    if (correct) {
                        ctrl.correct += 1;
                    }
                    next_card.resolve(data2card(data));
                });
            next_card.promise.then(function(card) {
                ctrl.state = 'front';
                ctrl.card = card;
                ctrl.next_card = null;
            });
        };

        this.stop = function() {
            ctrl.session_end = Date.now();
            ctrl.state = 'stopped';
            $http.delete('/api/session');
        };
    }
})();
