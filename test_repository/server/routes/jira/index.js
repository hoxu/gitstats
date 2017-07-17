//TODO: Modify this to use controllers/guards

/* API Routes for /api/jira/ (Unguarded Routes) */
var config = require('../../config');
var logger = require('../../utils/logger');

var fs = require('fs');
var ip = require('ip');
var url = require('url');

var Client = require('node-rest-client').Client;
var JiraRestClient = new Client();

var router = require('express').Router();

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

router.route('/issue')

//Create a new issue in JIRA
    .post(function (req, res) {
        //Check that a cookie exists first and foremost. This resource requires authentication.
        if (req.body.cookie) {
            //Also check that the summary, description and toolId were supplied
            if (req.body.summary && req.body.description && req.body.toolId && req.body.issueType) {
                //At this point, it is safe to attempt to retrieve the data
                var cookie = req.body.cookie,
                    summary = req.body.summary,
                    description = req.body.description,
                    toolId = req.body.toolId,
                    issueType = req.body.issueType;

                //Arguments to the POST request
                var args = {
                    data: {
                        fields: {
                            project: {
                                //Project ID SHOULD NOT change. If it does change in JIRA, update the config
                                id: config.jira.toolSupport.projectId
                            },
                            issuetype: {
                                //Issuetype ID SHOULD NOT change. If it does change in JIRA, update the config
                                id: issueType
                            },
                            //Summary that was passed in by the user
                            summary: summary,
                            customfield_10501: {
                                //JIRA REQUIRES that this be a string and not a number despite the fact that it is represented as a number in JSON
                                //Regardless, cast to a string. If it was supplied as a string already, this should have no effect
                                id: "" + toolId
                            },
                            //Description that was passed in by the user
                            description: description
                        }
                    },
                    headers: {
                        cookie: "JSESSIONID=" + cookie,
                        "Content-Type": "application/json"
                    }
                };

                JiraRestClient.post(_constructUrl(config.jira.api.issue), args, function (data, response) {
                    var statusCode = response.statusCode;

                    //HTTP 201 | Created
                    if (statusCode == 201) {
                        res.status(201).send({
                            success: true,
                            issue: {
                                id: data.id,
                                key: data.key,
                                link: _constructIssueUrl(data.key)
                            }
                        });

                        logger.info("[" + ip.address() + "] JIRA Issue Created: " + data.key);
                    }

                    //HTTP 400 | Bad Request
                    else if (statusCode == 400) {
                        res.status(400).send({
                            success: false,
                            error: "Invalid Input. Check for missing fields or invalid values (see 'errorMessages' for specific errors).",
                            errorMessages: data.errorMessages
                        });
                    }

                    else if (statusCode == 401) {
                        res.status(401).send({
                            success: false,
                            error: "Authorization failure."
                        });
                    }

                    //Fallback
                    else {
                        res.status(statusCode).send({
                            success: false,
                            error: "Uncaught Error. Status Code= " + statusCode
                        })
                    }
                });
            }

            else {
                res.status(401).send('Missing field. Check that you supplied a description, summary, tool id AND issue type id.');
            }
        }

        else {
            res.status(401).send('Missing cookie. This resource requires authentication. Check that you supplied a cookie.');
        }
    });

router.route('/user')

//Get a particular users details (display name/avatar)
    .get(function (req, res) {
        //Check that the cookie and the username were passed in
        //BOTH are required, so one check can be used (validity checks are handle below (HTTP 401/404)
        //If it was, continue
        if (req.query.cookie && req.query.username) {
            var cookie = req.query.cookie;
            var username = req.query.username;
            var args = {
                headers: {
                    "cookie": "JSESSIONID=" + cookie,
                    "Content-Type": "application/json"
                },

                parameters: {username: username}
            };

            JiraRestClient.get(_constructUrl(config.jira.api.user), args, function (data, response) {
                //Possible HTTP Status Codes according to JIRA REST API Docs: 200,401,404
                var statusCode = response.statusCode;

                //HTTP 200 | OK
                if (statusCode == 200) {

                    //TODO: Cache the avatar


                    res.status(200).send({
                        success: true,
                        avatar: data.avatarUrls["32x32"],
                        displayName: data.displayName
                    });
                }

                //HTTP 401 | Unauthorized
                else if (statusCode == 401) {
                    res.status(401).send({
                        success: false,
                        error: "Authentication Error. User is not authenticated."
                    })
                }

                //HTTP 404 | Not Found
                else if (statusCode == 404) {
                    res.status(404).send({
                        success: false,
                        error: "Not Found. The requested user was not found."
                    })
                }

                //Fallback
                else {
                    res.status(statusCode).send({
                        success: false,
                        error: "Uncaught Error. Status Code= " + statusCode
                    })
                }
            });
        }

        //If either param was not passed in, send a HTTP 400 back to the client
        else {
            res.status(400).send('Missing parameters. Check that you supplied a valid JIRA cookie and a valid JIRA username.');
        }
    });

router.route('/login')

//Login to JIRA
    .post(function (req, res) {

        if (req.body.username && req.body.password) {
            var username = req.body.username;
            var password = req.body.password;

            var args = {
                data: {
                    "username": username,
                    "password": password
                },
                headers: {
                    "Content-Type": "application/json"
                }
            };

            JiraRestClient.post(_constructUrl(config.jira.api.login), args, function (data, response) {
                var statusCode = response.statusCode;

                //HTTP 200 | Success
                if (statusCode == 200) {
                    res.send({
                        success: true,
                        session: data.session
                    });
                    logger.info("[" + ip.address() + "] JIRA login success for user: " + username);
                }

                //HTTP 401 | Unauthorized
                else if (statusCode == 401) {
                    res.status(401).send({
                        success: false,
                        error: "Authentication Error. Invalid user credentials."
                    });
                    logger.info("[" + ip.address() + "] JIRA login failure for user: " + username);
                }

                //HTTP 403 | Forbidden
                else if (statusCode == 403) {
                    res.status(403).send({
                        success: false,
                        error: "Login Denied. CAPTCHA required, connection throttled, etc. Try logging in later."
                    });
                    logger.info("[" + ip.address() + "] JIRA login failure for user: " + username);
                }

                //Fallback
                else {
                    res.status(statusCode).send({
                        success: false,
                        error: "Uncaught Error. Status Code= " + statusCode
                    });
                    logger.info("[" + ip.address() + "] JIRA login failure for user: " + username);
                }
            });
        }

        //If either param was not passed in, send a HTTP 400 back to the client
        else {
            res.status(400).send('Missing parameters. Check that you supplied a valid username and password.');
        }
    })

    //Logout of JIRA
    .delete(function (req, res) {
        if (req.query.cookie) {
            var args = {
                headers: {
                    "cookie": "JSESSIONID=" + req.query.cookie,
                    "Content-Type": "application/json"
                }
            };

            JiraRestClient.delete(_constructUrl(config.jira.api.login), args, function (data, response) {
                var statusCode = response.statusCode;

                if (statusCode == 204) {
                    res.status(204).send({loggedOut: true});
                    logger.info("[" + ip.address() + "] Logout succeeded.");
                }

                else if (statusCode == 401) {
                    res.status(401).send({loggedOut: false});
                    logger.info("[" + ip.address() + "] Logout failed.");
                }

                else {
                    res.status(statusCode).send({
                        loggedOut: false,
                        error: "Uncaught Error. Status Code= " + statusCode
                    });
                    logger.info("[" + ip.address() + "] Logout failed.");
                }
            });
        }

        else {
            res.status(400).send('Missing cookie. Make sure you supplied a valid cookie.');
        }
    })

    //Get the user's username from the session cookie
    .get(function (req, res) {
        //Check that the cookie was actually passed in
        if (req.query.cookie) {
            //Grab cookie from the query params
            var cookie = req.query.cookie;

            //Pack the cookie into the header (for authentication)
            var args = {
                headers: {
                    "cookie": "JSESSIONID=" + cookie,
                    "Content-Type": "application/json"
                }
            };

            JiraRestClient.get(_constructUrl(config.jira.api.login), args, function (data, response) {
                var statusCode = response.statusCode;

                //HTTP 200 | OK
                if (statusCode == 200) {
                    res.status(200).send({
                        success: true,
                        name: data.name
                    });
                }

                //HTTP 401 | Unauthorized
                else if (statusCode == 401) {
                    res.status(401).send({
                        success: false,
                        error: "Authentication Error. User is not authenticated."
                    })
                }

                //Fallback
                else {
                    res.status(statusCode).send({
                        success: false,
                        error: "Uncaught Error. Status Code= " + statusCode
                    })
                }
            });
        }

        //If the cookie was not passed in, send an HTTP 400 back to the client
        else {
            res.status(400).send('Missing parameters. Check that you supplied a valid JIRA cookie.');
        }
    });

//Helper method for constructing URLs for JIRA REST API
function _constructUrl(endpoint) {
    var fullUrl = url.format({
        protocol: 'https',
        hostname: config.jira.url,
        port: 443,
        pathname: endpoint
    });

    return decodeURIComponent(fullUrl);
}

//Helper method for constructing URLs for JIRA issues
function _constructIssueUrl(key) {
    var fullUrl = url.format({
        protocol: 'https',
        hostname: config.jira.url,
        pathname: '/browse/' + key
    });

    return decodeURIComponent(fullUrl);
}

module.exports = router;