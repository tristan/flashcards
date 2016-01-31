(function() {
    'use strict';

    angular.module('flashcards.onenter', [])
        .directive('fcOnEnter', OnEnterDirective)
        .directive('fcDisableFocus', DisableFocusDirective)
    ;

    OnEnterDirective.$inject = ['$parse', '$timeout'];
    function OnEnterDirective($parse, $timeout) {
        return function($scope, $element, $attrs) {
            var fn = $parse($attrs.fcOnEnter);
            var disabled = false;
            $element.on('keypress', function(event) {
                if (event.which === 13 && $element.val().trim() !== '') {
                    event.stopPropagation();
                    event.preventDefault();
                    $element[0].blur();
                    //$element[0].disabled = "disabled";
                    fn($scope, {$value: $element.val()});
                }
            });
        };
    }

    DisableFocusDirective.$inject = ['$parse'];
    function DisableFocusDirective($parse) {
        return function($scope, $element, $attrs) {
            var fn = $parse($attrs.fcDisableFocus);
            $element.on('focus', function(event) {
                console.log('...', fn($scope));
                if (fn($scope)) {
                    event.preventDefault();
                }
            });
        };
    }
})();
