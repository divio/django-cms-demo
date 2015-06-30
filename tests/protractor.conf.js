// // CONFIGURATION
// //#############################################################################
// 'use strict';
// #<{(| global browser |)}>#
//
// // var aldrynTestsLibrary = require('./pages/alteli.js');
//
// // To run in 2 browsers at the same time.
// var multiBrowserEnabled = false;
//
// // Set window size
// var setWindowSize = function () {
//     browser.driver.manage().window().setSize(
//         browser.params.browserConfig.width,
//         browser.params.browserConfig.height
//     );
// };
//
// var globalConfig = {
//     // The file path to the selenium server jar (to launch selenium server automatically)
//     // seleniumServerJar: './node_modules/protractor/selenium/selenium-server-standalone-2.45.0.jar',
//
//     // // The location of all specs that should be launched.
//     // specs: ['specs#<{(|.js'],
//
//     // Capabilities to be passed to the webdriver instance (use this to run
//     // one browser locally or on Sauce Labs).
//     capabilities: {
//         browserName: 'firefox',
//         name: 'django CMS benchmark tests',
//         shardTestFiles: true,
//         maxInstances: 2
//     },
//
//     // Name of the process executing this capability.  Not used directly by
//     // protractor or the browser, but instead pass directly to third parties
//     // like SauceLabs as the name of the job running this test
//     name: 'django CMS benchmark',
//
//     // Params for setting browser window width and height - can be also
//     // changed via the command line as: --params.browserConfig.width 1024
//     params: {
//         browserConfig: {
//             // to enable setting window width and height
//             width: 1280,
//             height: 1024
//         }
//     },
//
//     // Spec patterns are relative to the location of the spec file. They may
//     // include glob patterns. To run use: protractor conf.js --suite admin
//     suites: {
//         benchmark: 'specs/test_benchmark.js'
//     },
//
//     // If set, protractor will save the test output in .json at this path.
//     resultJsonOutputFile: 'reports/results.json',
//
//     framework: 'jasmine2',
//
//     // Maximum defaultTimeoutInterval can be set to 360000
//     jasmineNodeOpts: {
//         isVerbose: true,
//         showColors: true,
//         defaultTimeoutInterval: 900000
//     },
//
//     // A callback function called once protractor is ready and available, and
//     // before the specs are executed.
//     // You can specify a file containing code to run by setting onPrepare to
//     // the filename string.
//     onPrepare: function () {
//         setWindowSize();
//         // Set Angular site flag
//         browser.ignoreSynchronization = true;
//         // aldrynTestsLibrary.preCreateFolder('screenshots');
//         // aldrynTestsLibrary.preCreateFolder('reports');
//         // // Automatically store a screenshot at the end of each test
//         // aldrynTestsLibrary.storeScreenshot();
//     }
// };
//
// if (multiBrowserEnabled === false) {
//     exports.config = {
//         seleniumServerJar: globalConfig.seleniumServerJar,
//
//         // If true, Protractor will connect directly to the browser Drivers.
//         // Only Chrome and Firefox are supported for direct connect.
//         // directConnect: true,
//
//         specs: globalConfig.specs,
//
//         capabilities: globalConfig.capabilities,
//
//         params: globalConfig.params,
//
//         suites: globalConfig.suites,
//
//         resultJsonOutputFile: globalConfig.resultJsonOutputFile,
//
//         framework: globalConfig.framework,
//
//         jasmineNodeOpts: globalConfig.jasmineNodeOpts,
//
//         onPrepare: globalConfig.onPrepare
//     };
// } else {
//     exports.config = {
//         seleniumServerJar: globalConfig.seleniumServerJar,
//
//         specs: globalConfig.specs,
//
//         // To run in 2 browsers at the same time.
//         multiCapabilities: [{
//             browserName: 'firefox',
//             name: 'django CMS benchmark tests',
//             shardTestFiles: true,
//             maxInstances: 2
//         }, {
//             browserName: 'chrome',
//             name: 'django CMS benchmark tests',
//             shardTestFiles: true,
//             maxInstances: 2,
//             chromeOptions: {
//                 // Get rid of --ignore-certificate yellow warning, run in
//                 // 'incognito' mode (disabled as blocks screenshots creation)
//                 // and set English language.
//                 args: ['--no-sandbox', '--test-type=browser', '--lang=en']
//             }
//         }],
//
//         params: globalConfig.params,
//
//         suites: globalConfig.suites,
//
//         resultJsonOutputFile: globalConfig.resultJsonOutputFile,
//
//         framework: globalConfig.framework,
//
//         jasmineNodeOpts: globalConfig.jasmineNodeOpts,
//
//         onPrepare: globalConfig.onPrepare
//     };
// }
exports.config = {
    // Capabilities to be passed to the webdriver instance.
    capabilities: {
        'browserName': 'phantomjs'
    },

    onPrepare: function () {
        browser.ignoreSynchronization = true;
    },

    // Options to be passed to Jasmine-node.
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 30000
    }
};
