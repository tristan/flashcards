(function() {
    'use strict';

    angular.module('flashcards')
        .directive('fcKanjiCards', CardsDirective)
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

    function data2card(data) {
        if (data.hasOwnProperty('frame')) {
            var frame = data.frame;
            return {
                card_id: frame.frame_id,
                type: 'frame',
                front: {
                    language: "漢字",
                    text: frame.kanji
                },
                back: {
                    case_sensitive: false,
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

        ctrl.state = 'answering';

        $http.post('/api/session', {type: 'kanji'}).success(function(data) {
            session_id = data.session_id;
            ctrl.session_start = Date.now();
            ctrl.card = data2card(data);
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
            $http.put('/api/session', card2config(ctrl.card, correct))
                .success(function(data) {
                    ctrl.next_card.resolve(data2card(data));
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

})();
