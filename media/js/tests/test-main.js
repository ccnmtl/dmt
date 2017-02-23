var allTestFiles = [];
var TEST_REGEXP = /(spec|test)\.js$/i;

var pathToModule = function(path) {
    return path.replace(/^\/base\//, '').replace(/\.js$/, '');
};

Object.keys(window.__karma__.files).forEach(function(file) {
    if (TEST_REGEXP.test(file)) {
        // Normalize paths to RequireJS module names.
        allTestFiles.push(pathToModule(file));
    }
});

Object.keys(window.__html__).forEach(function(templateName) {
    var template = window.__html__[templateName];
    $('body').append(template);
});

require.config({
    // Karma serves files under /base, which is the basePath from your config file
    baseUrl: '/base',

    // dynamically load all test files
    deps: allTestFiles,
    callback: window.__karma__.start,

    // The path for including JS files in the app is slightly different during
    // testing. We have to manually prepend the src/ directory here.
    map: {
        '*': {
            'models/notify': 'src/models/notify',
            'utils/markdown_renderer': 'src/utils/markdown_renderer',
            'utils/markdown_preview': 'src/utils/markdown_preview'
        }
    },

    paths: {
        jquery: 'libs/jquery/jquery-min',
        underscore: 'libs/underscore/underscore-min',
        backbone: 'libs/backbone/backbone-min'
    }
});
