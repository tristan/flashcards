(function() {
    'use strict';

    angular.module('flashcards.tagInput', [])
        .directive('fcTagInput', TagInputDirective)
    ;

    CursorService.$inject = ['$window'];
    function CursorService($window) {
        this.get = function() {
            var selection = $window.getSelection();
            if (selection.rangeCount > 0) {
                var range = selection.getRangeAt(0);
                return range.startOffset;
            }
            return -1;
        };
    }

    function getCursorPos(element) {
        element = element[0];
        if (element.createTextRange) {
            var r = document.selection.createRange().duplicate();
		    r.moveEnd('character', element.value.length);
		    if (r.text == '')
                return element.value.length;
		    return element.value.lastIndexOf(r.text);
        } else
            return element.selectionStart;
    }

    function getCurrentWord(element) {
        var val = element.val();
        var pos = getCursorPos(element);
        var word_start = val.substring(0, pos).lastIndexOf(' ') + 1;
        return val.substring(word_start, pos);
    }

    function findWordMatch(word, matches, offset, key) {
        for (var i = offset; i < matches.length; i++) {
            var match = matches[i];
            if (key) {
                match = match[key];
            }
            if (match.indexOf(word) == 0) {
                return i;
            }
        }
        // if there was an offset, wrap the matcher back to the start
        if (offset > 0) {
            return findWordMatch(word, matches.slice(0, offset), 0, key);
        }
        return -1;
    }

    function updateInputWithMatch(element, word, match) {
        var rest = match.substring(word.length);
        var sels = element[0].selectionStart;
        element[0].setRangeText(rest, sels, element[0].selectionEnd);
        element[0].setSelectionRange(sels, sels + rest.length);
    }

    TagInputDirective.$inject = ['$http', '$parse', '$timeout'];
    function TagInputDirective($http, $parse, $timeout) {
        return {
            scope: {
                options: '=fcOptions',
                model: '=fcModel',
            },
            link: function($scope, $element, $attrs) {
                $scope.$watch('model', function(n, o) {
                    if (n == o) {
                        return;
                    }
                    if (angular.isUndefined(n)) {
                        $scope.model = [];
                        return;
                    }
                    if (!n) {
                        $element.val('');
                    } else {
                        var val = $scope.model.join(' ');
                        if ($element.val() != val) {
                            $element.val(val);
                        }
                    }
                }, true);
                var match_index = -1;
                var deleting = false;
                $element.on('keydown', function(event) {
                    // on tab
                    if (event.which == 9 && $element[0].selectionStart != $element[0].selectionEnd) {
                        var current_word = getCurrentWord($element);
                        if (current_word != '') {
                            event.preventDefault();
                            match_index = findWordMatch(current_word, $scope.options, match_index + 1, $attrs.fcOptionsKey);
                            if (match_index >= 0) {
                                var match = $scope.options[match_index];
                                if ($attrs.fcOptionsKey) {
                                    match = match[$attrs.fcOptionsKey];
                                }
                                updateInputWithMatch($element, current_word, match);
                                updateModel();
                            }
                        }
                    } else if (event.which == 8 || event.which == 46) {
                        deleting = true;
                    }
                });

                $element.on('input', function(event) {
                    if (deleting) {
                        deleting = false;
                    } else {
                        var current_word = getCurrentWord($element);
                        if (current_word != '') {
                            match_index = findWordMatch(current_word, $scope.options, 0, $attrs.fcOptionsKey);
                            if (match_index >= 0) {
                                var match = $scope.options[match_index];
                                if ($attrs.fcOptionsKey) {
                                    match = match[$attrs.fcOptionsKey];
                                }
                                updateInputWithMatch($element, current_word, match);
                            }
                        } else {
                            match_index = -1
                        }
                    }
                    updateModel();
                });

                function updateModel() {
                    var tags = $element.val().split(' ')
                        .filter(function(t) { return t != ""; });
                    $scope.$apply(function() {
                        if ($scope.model) {
                            $scope.model.splice(0, $scope.model.length);
                        } else {
                            $scope.model = [];
                        }
                        Array.prototype.push.apply($scope.model, tags);
                    });
                }
            }
        };
    }

})();
