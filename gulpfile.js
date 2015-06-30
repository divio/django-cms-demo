/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';

// #####################################################################################################################
// #IMPORTS#
var autoprefixer = require('gulp-autoprefixer');
var gulp = require('gulp');
var gutil = require('gulp-util');
var karma = require('karma').server;
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var minifyCss = require('gulp-minify-css');
var protractor = require('gulp-protractor').protractor;
// Download and update the selenium driver
var webdriverUpdate = require('gulp-protractor').webdriver_update;

// #####################################################################################################################
// #SETTINGS#
var PROJECT_ROOT = '.';
var PROJECT_PATH = {
    'sass': PROJECT_ROOT + '/private/sass',
    'css': PROJECT_ROOT + '/static/css'
};

var PROJECT_PATTERNS = {
    'sass': [
        PROJECT_PATH.sass + '/**/*.{scss,sass}'
    ]
};

// #####################################################################################################################
// #TASKS#
gulp.task('sass', function () {
    gulp.src(PROJECT_PATTERNS.sass)
        .pipe(sourcemaps.init())
        .pipe(sass())
        .on('error', function (error) {
            gutil.log(gutil.colors.red('Error (' + error.plugin + '): ' + error.messageFormatted));
        })
        .pipe(autoprefixer({
            browsers: ['last 2 versions'],
            cascade: false
        }))
        .pipe(minifyCss())
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(PROJECT_PATH.css));
});

// #########################################################
// #TESTS#
gulp.task('tests', function () {
    // run javascript tests
    karma.start({
        'configFile': __dirname + '/tests/karma.conf.js',
        'singleRun': true
    });
});

gulp.task('webdriver:update', webdriverUpdate);
gulp.task('tests:integration', ['webdriver:update'], function () {
    gulp.src(['./tests/integration/*.js'])
        .pipe(protractor({
            configFile: 'tests/protractor.conf.js',
            args: ['--baseUrl', 'http://127.0.0.1:8000']
        }))
        .on('error', function (error) {
            gutil.log(gutil.colors.red('Error (' + error.plugin + '): ' + error.message));
        });
});

gulp.task('karma', function () {
    // run javascript tests
    karma.start({
        'configFile': __dirname + '/tests/karma.conf.js'
    });
});

// #####################################################################################################################
// #COMMANDS#
gulp.task('watch', function () {
    gulp.watch(PROJECT_PATTERNS.sass, ['sass']);
});

gulp.task('default', ['sass', 'watch']);
