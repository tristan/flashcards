(function() {
    'use strict';

    angular.module('flashcards.box', [])
        .directive('fcBox', BoxDirective)
    ;

    BoxDirective.$inject = ['$timeout'];
    function BoxDirective($timeout) {
        return {
            link: {
                post: function($scope, $element, $attrs) {
                    /*
                    var h = $element[0].offsetHeight;
                    var w = $element[0].offsetWidth;
                    $element.css({
                        "margin-left": "-" + (w / 2) + "px",
                        "margin-top": "-" + (h / 2) + "px",
                    });
                    var before = angular.element('<div fc-box-before>「</div>');
                    $element.prepend(before);
                    before.css({
                        "margin-left": "-" + ((w / 2) + (before[0].offsetWidth)) + "px",
                        "margin-top": "-" + ((h / 2) + (before[0].offsetHeight / 2)) + "px",
                    });
                    var after = angular.element('<div fc-box-after>」</div>');
                    $element.append(after);
                    after.css({
                        "margin-left": (w / 2) + "px",
                        "margin-top": ((h / 2) - (after[0].offsetHeight / 2)) + "px",
                    });
                    */
                }
            }
        };
    }
})();
