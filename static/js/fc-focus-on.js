(function() {
    'use strict';

    angular.module('flashcards.focuson', [])
        .directive('fcFocusOn', FocusOnDirective)
        .directive('fcFocusOnLink', FocusOnLinkDirective)
    ;

    FocusOnDirective.$inject = ['$parse', '$timeout'];
    function FocusOnDirective($parse, $timeout) {
        return function($scope, $element, $attrs) {
            var first_call = true;
            var exp = $parse($attrs.fcFocusOn);
            $scope.$watch(exp, function(val, old) {
                if (val && (first_call || val !== old)) {
                    first_call = false;
                    $timeout(function() {
                        $element[0].focus();
                    }, 10);
                }
            });
        };
    }

    function FocusOnLinkDirective($parse, $timeout) {
        return {
            link: {
                post: function($scope, $element, $attrs) {
                    console.log('...');
                    $element[0].focus();
                }
            }
        };
    }
})();
