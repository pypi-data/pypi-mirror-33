(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_saml', [
    'OpenSlidesApp.core.site',
    'OpenSlidesApp.openslides_saml',
])

.config([
    'OpenSlidesPluginsProvider',
    function(OpenSlidesPluginsProvider) {
        OpenSlidesPluginsProvider.registerPlugin({
            name: 'openslides_saml',
            display_name: 'SAML',
            languages: ['de']
        });
    }
]);

})();
