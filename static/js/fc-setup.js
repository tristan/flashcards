(function() {
    'use strict';

    angular.module('flashcards')
        .controller('ConfigController', ConfigController)
        .directive('fcEditable', EditableDirective)
    ;

    ConfigController.$inject = ['$http', 'StateService'];
    function ConfigController($http, state) {
        var ctrl = this;
        var reverse_kanji_lookup = {};
        $http.get('/api/frame').success(function(data) {
            ctrl.frames = data.frames;
            for (var i = 0; i < ctrl.frames.length; i++) {
                var frame = ctrl.frames[i];
                var primatives = [];
                for (var p_id in frame.primatives) {
                    primatives.push(frame.primatives[p_id]);
                }
                frame._primatives = primatives.join(' ');
                // copy the original id, incase it gets changed
                frame._id = frame.frame_id;
                reverse_kanji_lookup[frame.kanji] = frame;
            }
        });

        this.saveRow = function(index) {
            var frame = ctrl.frames[index];
            if (!frame) {
                return;
            }
            // find ids for primatives
            var primatives = [];
            var primative_kanjis = frame._primatives.split('');
            console.log(primative_kanjis);
            for (var i = 0; i < primative_kanjis.length; i++) {
                var kanji = primative_kanjis[i].trim();
                if (kanji) {
                    // make sure the primative exists
                    var primative = reverse_kanji_lookup[kanji];
                    if (!primative) {
                        frame.error = true;
                        return;
                    }
                    primatives.push(primative.frame_id);
                }
            }
            var config = {
                frame_id: frame.frame_id,
                kanji: frame.kanji,
                keyword: frame.keyword,
                primative: frame.primative,
                primatives: primatives
            };
            var req = frame._id ? $http.put('/api/frame/' + frame._id, config) : $http.post('/api/frame', config);
            req.success(function(data) {
                frame.dirty = 0;
                frame._id = data.frame_id;
                reverse_kanji_lookup[frame.kanji] = frame;
            });
        };

        this.addRow = function(index) {
            ctrl.frames.splice(index, 0, {
                frame_id: ctrl.frames[index-1].frame_id + 1,
                dirty: true,
                primative: "",
                keyword: "",
                kanji: "",
                _primatives: ""
            });
            for (var i = index + 1; i < ctrl.frames.length; i++) {
                ctrl.frames[i].frame_id += 1;
                if (ctrl.frames[i]._id) {
                    ctrl.frames[i]._id += 1;
                }
            }
        };

        this.deleteRow = function(index) {
            var frame = ctrl.frames[index];
            if (frame) {
                if (frame._id) {
                    $http.delete('/api/frame/' + frame._id);
                }
                ctrl.frames.splice(index, 1);
                for (var i = index; i < ctrl.frames.length; i++) {
                    ctrl.frames[i].frame_id -= 1;
                    if (ctrl.frames[i]._id) {
                        ctrl.frames[i]._id -= 1;
                    }
                }
            }

        };

        this.done = function() {
            state.push(function() {
                state.section = 'home'
            }, '/');
        };
    }

    EditableDirective.$inject = ['$compile', '$window']
    function EditableDirective($compile, $window) {
        return {
            scope: {
                value: '=fcEditable',
                dirty: '=dirtyCount'
            },
            link: function($scope, $element, $attrs) {
                var original_value = $scope.value;
                var current_clone, is_dirty;
                function close_editable(event) {
                    if (event.keyCode == 13 || event.keyCode == 27) {
                        if (current_clone) {
                            current_clone.off('keyup', close_editable);
                            current_clone = null;
                        }
                        if (event.keyCode == 27) {
                            $scope.value = original_value;
                        }
                        $element.html($scope.value);
                    }
                }
                $element.on('click', function($event) {
                    var selection = $window.getSelection();
                    if (!selection.isCollapsed && selection.containsNode($element[0], true)) {
                        return;
                    }
                    if (!current_clone) {
                        $compile('<input type="text" ng-model="value">')($scope, function(clone) {
                            $element.empty();
                            $element.append(clone);
                            current_clone = clone;
                            clone.on('keyup', close_editable);
                            clone[0].focus();
                        });
                    }
                });
                $element.html($scope.value);
                $scope.$watch('value', function(n, o) {
                    if (n && n != o) {
                        if (n != original_value && !is_dirty) {
                            $element.addClass('dirty');
                            is_dirty = true;
                            if ($scope.dirty) {
                                $scope.dirty += 1;
                            } else {
                                $scope.dirty = 1;
                            }
                        } else if (n == original_value && is_dirty) {
                            $element.removeClass('dirty');
                            is_dirty = false;
                            if ($scope.dirty) {
                                $scope.dirty -= 1;
                            }
                        }
                    }
                });
                $scope.$on('$destroy', function() {
                    if (current_clone) {
                        current_clone.off('keyup', close_editable);
                        current_clone = null;
                    }
                });
            }
        };
    }

})();
