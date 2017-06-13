//User Defined Modules
var config = require('./config');
var logger = require('./utils/logger');

//Low-Level Modules
var ip = require('ip');
var minimist = require('minimist')(process.argv.slice(2));

//ExpressJS (Server-Side) Modules
var express = require('express');
var app = express();
var bodyParser = require('body-parser');

//MongoDB Modules
var mongoose = require('mongoose');

// =========================================== START SETUP ========================================================== //
//Set the port for the server
var port = process.env.PORT || config.httpPort;

// ========================================= EXPRESS ======================================================== //
//Configure app to use bodyParser()
//Allows for parsing information from POST requests
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

//Tell the app to use the router config we defined in /routes
//In this case, every route is prefixed with '/api/'
//This could be anything, but considering it's an API operation, this prefix should be suitable
app.use('/api', require('./routes/index'));

// ====================================== CMD LINE ARGS ===================================================== //
//Check if the prod flag was set (-p or --prod)
var prod = false;
if (minimist.p || minimist.prod) {
    prod = true;
    app.use(express.static('dist'));
}

else {
    app.use(express.static('app'));
}

//Check if the test flag was set (-t or --test)
var test = false;
if (minimist.t || minimist.test) {
    test = true;
    /*
     WARNING!!!

     The following code tells NodeJS to ignore ALL HTTPS security (SSL/TLS).
     This is OK for testing, but should NEVER be enabled in production.
     Since the server was started with the -t flag, we are running on a test version.
     */
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
}

// ========================================= MONGODB ======================================================== //
var dbOptions = {
    user: config.db.username,
    pass: config.db.password,
    auth: {
        authdb: 'admin'
    }
};

mongoose.connect(config.db.tools.path, dbOptions);
mongoose.connection.on('error', function () {
    logger.error("ERROR CONNECTING TO DB. Check that the DB is online.");
    process.exit(1);
});

// ============================================ END SETUP =========================================================== //


app.listen(port);
console.log('Server is running on port: ' + port);