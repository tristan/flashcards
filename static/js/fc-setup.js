(function() {
    'use strict';

    angular.module('flashcards')
        .controller('SetupController', SetupController)
        .controller('LanguageSetupController', LanguageSetupController)
        .controller('ConceptSetupController', ConceptSetupController)
    ;

    SetupController.$inject = ['$http', 'StateService'];
    function SetupController($http, state) {
        var ctrl = this;

        this.languages = function() {
            state.push(function() {
                state.section = 'languages';
            }, '/setup/languages/');
        };

        this.concepts = function() {
            state.push(function() {
                state.section = 'concepts';
            }, '/setup/concepts/');
        };

        this.done = function() {
            state.push(function() {
                state.section = 'home'
            }, '/');
        };
    }

    LanguageSetupController.$inject = ['$http', 'StateService'];
    function LanguageSetupController($http, state) {
        var ctrl = this;

        $http.get('/api/language').success(function(data) {
            ctrl.languages = data.languages;
        });

        this.createNewLanguage = function() {
            $http.post('/api/language', {
                name: ctrl.new_language_name
            }).success(function(data) {
                ctrl.languages.push(data);
                ctrl.new_language_name = '';
            });
        };

        this.done = function() {
            state.push(function() {
                state.section = 'setup'
            }, '/setup/');
        };
    }

    ConceptSetupController.$inject = ['$http', 'StateService'];
    function ConceptSetupController($http, state) {
        var ctrl = this;
        $http.get('/api/concept').success(function(data) {
            ctrl.concepts = data.concepts;
        });

        this.openEditConceptForm = function(concept) {
            ctrl.concept = concept || {};
            $http.get('/api/tag').success(function(data) {
                ctrl.tags = data.tags;
            });
            $http.get('/api/language').success(function(data) {
                ctrl.languages = data.languages;
            });
            if (!state.edit_concept) {
                state.push(function() {
                    state.edit_concept = true;
                });
            }
        };

        this.saveConcept = function() {
            if (ctrl.concept.concept_id) {
                $http.put('/api/concept/' + ctrl.concept.concept_id, ctrl.concept)
                    .success(function(data) {
                        state.push(function() {
                            state.edit_concept = false;
                        });
                        ctrl.concepts.push(data);
                        ctrl.concept = {};
                    });
            } else {
                $http.post('/api/concept', ctrl.concept)
                    .success(function(data) {
                        state.push(function() {
                            state.edit_concept = false;
                        });
                        ctrl.concepts.push(data);
                        ctrl.concept = {};
                    });
            }
        };

        this.resetNewConcept = function() {
            ctrl.concept = {};
        };

        this.done = function() {
            state.push(function() {
                state.section = 'setup'
                state.edit_concept = false;
            }, '/setup/');
        };
    }

})();
