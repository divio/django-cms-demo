var formatTaskName = function (browserName) {
    return [
        'Test', browserName, 'for',
        process.env.TRAVIS_REPO_SLUG,
        (provess.env.TRAVIS_PULL_REQUEST ? 'pull request #' + process.env.TRAVIS_PULL_REQUEST : ''),
        '#' + process.env.TRAVIS_BUILD_NUMBER
    ].join(' ');
};

var config = {
    // Capabilities to be passed to the webdriver instance.
    capabilities: {
        'browserName': 'phantomjs',
        'phantomjs.binary.path': require('phantomjs').path
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

if (process.env.SAUCE_USERNAME && process.env.SAUCE_ACCESS_KEY) {
    config.capabilities = null;
    config.sauceUser = process.env.SAUCE_USERNAME;
    config.sauceKey = process.env.SAUCE_ACCESS_KEY;
    config.multiCapabilities = [
        {
            name: formatTaskName('Firefox'),
            browserName: 'firefox',
            shardTestFiles: true,
            maxInstances: 2
        }, {
            name: formatTaskName('Chrome'),
            browserName: 'chrome',
            shardTestFiles: true,
            maxInstances: 2,
            chromeOptions: {
                // Get rid of --ignore-certificate yellow warning, run in
                // 'incognito' mode (disabled as blocks screenshots creation)
                // and set English language.
                args: ['--no-sandbox', '--test-type=browser', '--lang=en']
            }
        }
    ];
}

exports.config = config;
