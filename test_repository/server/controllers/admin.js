/* Controller for /admin resources */

var jwt = require('jsonwebtoken');
var ip = require('ip');

var config = require('../config');
var Admin = require('../models/Admin');
var logger = require('../utils/logger');
var passCrypt = require('../utils/passCrypt');
var validation = require('../validation');

/**
 * Function for creating an admin in the DB.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.createAdmin = function (req, res) {
    var username = req.body.username;
    var password = req.body.password;

    //Check that a valid username/password was supplied
    var valid = validation.validateUserPass(res, {username: username, password: password});

    //If valid
    if (valid) {
        //Make a new Admin obj with the given creds
        var admin = new Admin({
            _id: username,
            username: username,
            //Hash the password using the bcrypt util
            password: passCrypt.generateHash(password)
        });

        //Save the new admin in the DB
        admin.save(function (err) {
            if (err) {
                logger.info("[" + ip.address() + "] New admin creation failed. Admin username= " + username);

                res.status(422).send({message: "New admin creation failed. Admin username= " + username, errors: err});
            }

            else {
                logger.info("[" + ip.address() + "] New admin creation succeeded. Admin username= " + username);

                res.status(201).send({added: true});
            }
        });
    }
};

/**
 * Function for admin login
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.login = function (req, res) {
    //Find the admin in the DB that matches the supplied username
    Admin.findOne({username: req.body.username}, function (err, admin) {
        //Following if statements check for general errors/bad username
        if (err)
            res.status(400).send({errors: err});

        if (!admin) {
            res.status(404).send({success: false, errors: "Authentication failed. User not found."});
        }

        //Otherwise, a matching admin was found
        else if (admin) {
            //If the passwords match (i.e. user gave the correct password)
            if (passCrypt.checkPass(req.body.password, admin.password)) {
                //Create a token
                var token = jwt.sign({username: admin.username}, config.secretKey, {
                    expiresIn: "1d"
                });

                res.status(200).send({success: true, token: token});
            }

            //Passwords don't match (i.e. user gave the WRONG password)
            else {
                res.status(401).send({success: false, errors: "Authentication failed. Incorrect password."});
            }
        }
    });
};