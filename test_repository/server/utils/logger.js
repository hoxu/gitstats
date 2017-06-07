/* Common logging functions */

var winston = require('winston');

//Add a debugging level logger
winston.loggers.add('debug', {
    console: {
        level: 'debug',
        colorize: true,
    },

    file: {
        filename: './logs/debug.log'
    }
});

//Add an error level logger
winston.loggers.add('error', {
    console: {
        level: 'error',
        colorize: true,
    },

    file: {
        filename: './logs/errors.log'
    }
});

//Add an info level logger
winston.loggers.add('info', {
    console: {
        level: 'info',
        colorize: true,
    },

    file: {
        filename: './logs/info.log'
    }
});

//Export the loggers so we can use them throughout
var debug = winston.loggers.get('debug');
var error = winston.loggers.get('error');
var info = winston.loggers.get('info');

module.exports = {
    debug: function (message) {
        debug.debug(message);
    },

    error: function (message) {
        error.error(message)
    },

    info: function (message) {
        info.info(message);
    }
};