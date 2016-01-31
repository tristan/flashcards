(function() {
    'use strict';

    angular.module('flashcards.fontSize', [])
        .directive('fcFontSize', FontSizeDirective)
    ;

    FontSizeDirective.$inject = [];
    function FontSizeDirective() {
        return function($scope, $element, $attrs) {
            $scope.$watch(function() {
                return $element.text();
            }, function(val, old) {
                if (val && val !== old) {
                    console.log($element[0].offsetWidth, val.length, 5 / val.length);
                    var size = Math.max(1, Math.min(5, 5 / val.length));
                    $element.css({"font-size": size + "em"});
                }
            });
        };
    }
})();
