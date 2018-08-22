const gulp = require('gulp');
const babel = require('gulp-babel');
const concat = require('gulp-concat');
const rename = require('gulp-rename');
const prefix = require('gulp-autoprefixer');
const minifyCSS = require('gulp-minify-css');
const del = require('del');
const htmlmin = require('gulp-htmlmin');
const runSequence = require('run-sequence');
const uglify = require('gulp-uglify');

let styles = [
  'css/vendors/nucleo.css',
  'css/vendors/argon.min.css',
  'css/style.css'
];

let scripts = [
  'js/script.js'
];

gulp.task('styles', function () {
  return gulp.src(styles)
    .pipe(concat('styles.css'))
    .pipe(minifyCSS())
    .pipe(prefix('last 2 versions'))
    .pipe(rename('styles.min.css'))
    .pipe(gulp.dest('./css'))
});

// Gulp task to minify JavaScript files
gulp.task('scripts', function () {
  return gulp.src(scripts)
    .pipe(concat('scripts.js'))
    .pipe(babel())
    .pipe(rename('scripts.min.js'))
    .pipe(uglify().on('error', function (e) {
      console.log(e);
    }))
    .pipe(gulp.dest('./js'));
});

gulp.task('watch', function() {
    gulp.watch(styles, ['styles']);
    gulp.watch(scripts, ['scripts']);
});

// Clean output directory
gulp.task('clean', () => del(['dist']));

// Gulp task to minify all files
gulp.task('default', ['clean'], function () {
  runSequence(
    'styles',
    'scripts',
    'watch'
  );
});