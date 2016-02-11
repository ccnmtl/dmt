module.exports = function(config) {
  config.set({
    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: 'media/js',

    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['requirejs', 'qunit', 'sinon'],

    // list of files / patterns to load in the browser
    files: [
        'libs/jquery/jquery-min.js',
        { pattern: 'libs/**/*.js', included: false },
        { pattern: 'src/**/*.js', included: false },
        { pattern: 'tests/fixtures/**/*.html', watched: false },
        { pattern: 'tests/**/*.spec.js', included: false },
        'tests/test-main.js'
    ],

    // list of files to exclude
    exclude: [
        'src/client_edit.js',
        'src/item.js'
    ],

    preprocessors: {
        '**/*.html': ['html2js']
    },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['dots', 'junit'],

    junitReporter: {
        outputFile: '../../karma-test-results.xml'
    },

    // web server port
    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true
  });
};
