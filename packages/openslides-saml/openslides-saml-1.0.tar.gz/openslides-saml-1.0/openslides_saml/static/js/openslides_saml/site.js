(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_saml.site', [
    'OpenSlidesApp.openslides_saml',
    'OpenSlidesApp.users.site',
])

.run([
    'templateHooks',
    '$window',
    'SAMLSettings',
    function (templateHooks, $window, SAMLSettings) {
        templateHooks.registerHook({
            Id: 'loginFormButtons',
            // I do not know, why the href attribute does not work here. But with JS setting the
            // window.location works...
            template:   '<a href="/saml/?sso" class="btn btn-primary pull-right" translate ng-click="samlLogin()">' +
                            SAMLSettings.loginButtonText +
                        '</a>',
            noDivWrap: true,
            scope: {
                samlLogin: function () {
                    $window.location = "/saml/?sso";
                },
            },
        });
    }
])

.factory('isSamlUser', [
    '$http',
    function ($http) {
        var _isSamlUser = false;
        $http.get('/saml/isSamlUser/').then(function (success) {
            _isSamlUser = success.data;
        });
        return function () {
            return _isSamlUser;
        };
    }
])

.factory('SamlAboutMeForm', [
    'gettextCatalog',
    'Editor',
    'Mediafile',
    function (gettextCatalog, Editor, Mediafile) {
        return {
            // ngDialog for user form
            getDialog: function () {
                return {
                    // Use the original parofile dialog.
                    template: 'static/templates/users/profile-password-form.html',
                    // ...but another controller
                    controller: 'SamlAboutMeCtrl',
                    className: 'ngdialog-theme-default wide-form',
                    closeByEscape: false,
                    closeByDocument: false,
                };
            },
            // and just the about me field
            getFormFields: function (hideOnCreateForm) {
                var images = Mediafile.getAllImages();
                return [
                    {
                        key: 'about_me',
                        type: 'editor',
                        templateOptions: {
                            label: gettextCatalog.getString('About me'),
                        },
                        data: {
                            ckeditorOptions: Editor.getOptions(images)
                        },
                    }
                ];
            }
        };
    }
])

.controller('SamlAboutMeCtrl', [
    '$scope',
    'Editor',
    'User',
    'operator',
    'SamlAboutMeForm',
    'gettext',
    'ErrorMessage',
    function($scope, Editor, User, operator, SamlAboutMeForm, gettext, ErrorMessage) {
        $scope.model = angular.copy(operator.user);
        $scope.title = gettext('Edit profile');
        $scope.formFields = SamlAboutMeForm.getFormFields();
        $scope.save = function (user) {
            User.inject(user);
            User.save(user).then(
                function(success) {
                    $scope.closeThisDialog();
                },
                function(error) {
                    // save error: revert all changes by restore
                    // (refresh) original user object from server
                    User.refresh(user);
                    $scope.alert = ErrorMessage.forAlert(error);
                }
            );
        };
    }
])

.decorator('UserMenu', [
    '$delegate',
    '$window',
    'ngDialog',
    'UserProfileForm',
    'UserPasswordForm',
    'SamlAboutMeForm',
    'isSamlUser',
    'SAMLSettings',
    function ($delegate, $window, ngDialog, UserProfileForm, UserPasswordForm,
        SamlAboutMeForm, isSamlUser, SAMLSettings) {
        $delegate = {
            logout: function () {
                $window.location = "/saml/?slo";
            },
            editProfile: function () {
                if (isSamlUser()) {
                    ngDialog.open(SamlAboutMeForm.getDialog());
                } else {
                    ngDialog.open(UserProfileForm.getDialog());
                }
            },
            changePassword: function () {
                if (isSamlUser()) {
                    $window.location = SAMLSettings.changePasswordUrl;
                } else {
                    ngDialog.open(UserPasswordForm.getDialog());
                }
            },
        };
        return $delegate;
    }
]);

})();
