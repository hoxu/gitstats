/* Guard that only allows admins to access whatever route the guard is attached to */

var jwt = require('jsonwebtoken');

var config = require('../config');

exports.adminGuard = function (req, res, next) {
    //Check for a token in the body, params or headers
    var token = req.body.token || req.query.token || req.headers['x-access-token'];

    //Check that a token was actually supplied
    if (token) {
        //Now check that the token is actually legitimate
        jwt.verify(token, config.secretKey, function (err, decoded) {
            //If there was an error during the verification, the user is not authenticated
            if (err)
                return res.status(403).send({success: false, error: "Failed to authenticate token."});

            //Otherwise, the user is valid
            else {
                req.decoded = decoded;
                next();
            }
        });
    }

    //Otherwise, do not proceed and send back an error
    else {
        return res.status(403).send({success: false, error: "No token provided in request."});
    }
};