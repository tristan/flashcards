(function() {
    'use strict';

    angular.module('flashcards')
        .directive('fcTimeSince', TimeSinceDirective)
    ;

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
