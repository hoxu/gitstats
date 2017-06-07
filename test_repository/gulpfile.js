const PATHS = {
    //Input Paths
    admin_in: 'app/admin/**/*',
    elements_in: 'app/elements/elements.html',
    html_in: 'app/*.html',
    img_in: 'app/images/**/*',
    scripts_in: 'app/scripts/**/*',

    //Output Paths
    admin_out: 'dist/admin',
    elements_out: 'dist/elements',
    html_out: 'dist/',
    img_out: 'dist/images',
    scripts_out: 'dist/scripts'
};

var gulp = require('gulp');
var crisper = require('gulp-crisper');
var minify = require('gulp-htmlmin');
var gulpif = require('gulp-if');
var gulpSeq = require('gulp-sequence');
var uglify = require('gulp-uglify');
var vulcanize = require('gulp-vulcanize');

var del = require('del');

gulp.task('build', ['default'], function () {
    return gulp.src(['dist']).pipe(gulp.dest('_build'));
});

/**
 * Default Gulp task
 *
 * Runs a clean (to clear out /build) and then builds the project
 */
gulp.task('default', gulpSeq('clean', 'build'));

/**
 * Gulp clean task
 *
 * Cleans out /build by deleting the entire folder using 'del'
 */
gulp.task('clean', function () {
    return del(['dist']);
});

/**
 * Gulp build task
 *
 * Builds the project by doing the following:
 * 1) Vulcanizing HTML imports by calling helper method
 * 2) Moving all HTML files
 * ...
 * TODO: More
 */
gulp.task('build', ['vulcanize', 'moveAdmin', 'moveHTML', 'moveImg', 'moveScripts'], function () {

});

/** Gulp move admin task. Moves the /admin folders to dist */
gulp.task('moveAdmin', function () {
    return moveAdmin();
});

/** Helper method to move all HTML files in /app/admin to /dist/admin */
function moveAdmin() {
    return gulp.src(PATHS.admin_in).pipe(gulpif('*.html', minifyHTML())).pipe(gulp.dest(PATHS.admin_out));
}

/** Gulp move HTML task. Moves all HTML files in /app by calling helper method */
gulp.task('moveHTML', function () {
    return moveHTML();
});

/** Helper method to move all HTML files /app to the /dist dir */
function moveHTML() {
    return gulp.src(PATHS.html_in).pipe(gulpif('*.html', minifyHTML())).pipe(gulp.dest(PATHS.html_out));
}

/** Gulp move images task. Moves given images to /dist by calling helper method */
gulp.task('moveImg', function () {
    return moveImg();
});

/** Helper method to move all images in /app to the /dist dir */
function moveImg() {
    return gulp.src(PATHS.img_in).pipe(gulp.dest(PATHS.img_out));
}

/** Gulp move scripts task. Moves scripts to /dist by calling helper method */
gulp.task('moveScripts', function () {
    return moveScripts();
});

/** Helper method to move all scripts in /app to the /dist dir */
function moveScripts() {
    return gulp.src(PATHS.scripts_in).pipe(gulp.dest(PATHS.scripts_out));
}

/** Gulp vulcanize task. Calls helper method to vulcanize HTML imports */
gulp.task('vulcanize', function () {
    return vulcanizeImports();
});

/**
 * Vulcanize the given HTML file.
 *
 * This will use the 'vulcanize' tool to inline all HTML imports in a given file (reduces network activity)
 *
 * Order of Events:
 * 1) Pipes to source HTML file to 'vulcanize' with args. Inlines the HTML/CSS/JS and strips all comments (except @license decelerations)
 * 2) Pipes to 'crisper' to separate the JS into it's own file for CSP compliance and reduction of HTML parser load
 * 3) Pipes to 'HTMLminifier' to minify the HTML code (remove whitespace, etc). ONLY MINIFIES IF .HTML
 * 4) Pipes to 'uglify' to minify the JS code. ONLY MINIFIES IF .JS
 * 5) Pipes the output to the specified directory
 */
function vulcanizeImports() {
    return gulp.src(PATHS.elements_in)
        .pipe(vulcanizeHTML())
        .pipe(crisper())
        .pipe(gulpif('*.html', minifyHTML()))
        .pipe(gulpif('*.js', uglifyJS()))
        .pipe(gulp.dest(PATHS.elements_out))
}

function vulcanizeHTML() {
    console.log("=== VULCANIZE ===");
    return vulcanize({
        inlineScripts: true,
        inlineCss: true,
        stripComments: true
    });
}

function minifyHTML() {
    console.log("=== MINIFY ===");
    return minify({collapseWhitespace: true})
}

function uglifyJS() {
    console.log("=== UGLIFY ===");
    return uglify({preserveComments: 'some'});
}