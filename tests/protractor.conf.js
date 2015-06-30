exports.config = {
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
