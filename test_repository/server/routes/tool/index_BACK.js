//Dedicated router for retrieving 'tool'
var logger = require('../../../utils/logger');

var ip = require('ip');

var router = require('express').Router();
var Tool = require('../../../models/Tool');

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

/* ================================================================================================================== */
/**
 * ROUTE:       /api/tool/
 * METHOD(S):   POST
 */
/* ================================================================================================================== */
router.route('/')

/**
 * Request:     POST /api/tool/
 * Returns:     JSON Object
 * Logged:      YES
 *
 * Description:
 * Creates a new (empty) tool in the DB.
 * Requires that an id and name be supplied for the new tool in the body of the request.
 *
 * Body (Required):
 *      toolId      [Number]    The id of the tool to be added.
 *      toolName    [String]    The name of the tool to be added.
 *
 * Responses:
 *      HTTP 200    [Success]   Returned if tool was created.
 *          { created: true }
 *
 *      HTTP 400    [Error]     Returned if there was a missing parameter. Response -> 'errors' will contain the missing field
 *          {
 *              created: false,
 *              errors: "Missing parameter 'XXXXXX'"
 *          }
 *      HTTP 422    [Error]     Returned if the request went through successfully, but there was an issue creating the tool.
 *          {
 *              created: false,
 *              errors: "New tool creation failed. Duplicate tool id. Please check all inputs."
 *          }
 */
    .post(function (req, res) {
        //Get the toolId and toolName from the body of the request
        var toolId = req.body.toolId;
        var toolName = req.body.toolName;

        //Check that the request body contains the required data
        if (toolId && toolName) {
            //Parse the int just to make sure it is actually an integer before we create the tool
            var _id = parseInt(toolId);

            //Declare a new Tool object using the model
            var newTool = new Tool({
                _id: _id,
                id: _id,
                name: toolName,

                about: [],
                training: [],
                links: []
            });

            //Save to MongoDB
            newTool.save(function (err) {
                //If there was an error while saving, send it back to the client
                if (err) {
                    var message = "";

                    //In this case, 11000 is the error code for a duplicate key
                    if (err.code == 11000)
                        message = "New tool creation failed. Duplicate tool id. Please check all inputs.";
                    //Otherwise, just set the message = error message from mongoose
                    else
                        message = err.errmsg;

                    //Send an HTTP 422 (Unprocessable Entity) with the error message.
                    //Why HTTP 422: HTTP 400 is bad syntax. Correct syntax was supplied, but something went wrong during the request
                    res.status(422).send({created: false, errors: message});

                    //Log this request
                    logger.info("[" + ip.address() + "] New tool creation failed. Tool id=" + toolId + " Reason: " + message);
                }

                //Otherwise, the addition was successful
                else {
                    //Send an HTTP 201 (Created)
                    res.status(201).send({created: true});

                    //Log this request
                    logger.info("[" + ip.address() + "] New tool creation succeeded. toolId=" + toolId);
                }
            });
        }

        //Otherwise, the required data was not supplied in the request. DO NOT attempt to access the DB in this case.
        else {
            var message = "";

            //If-else block to determine which parameter was missing. Sets the message text = missing param
            if (!req.body.toolId)
                message = "Missing body parameter 'toolId'.";
            else
                message = "Missing body parameter 'toolName'.";

            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({created: false, errors: message});
        }
    });

/* ================================================================================================================== */
/**
 * ROUTE:       /api/tool/:tool_id
 * METHOD(S):   GET
 */
/* ================================================================================================================== */
router.route('/:toolId')
/**
 * Request:     GET /api/tool/:toolId
 * Returns:     JSON Object
 * Logged:      NO
 *
 * Description:
 * Retrieves a single tool from the DB in its entirety.
 *
 * Body (Required):
 *      toolId      [Number]    The id of the tool to retrieve.
 *
 * Responses:
 *      HTTP 200    [Success]   Returned if a tool was found with a matching id.
 *          {
 *              _id: 01234,
 *              id: 01234,
 *              name: "Test Tool",
 *              about: [],
 *              training: [],
 *              links: []
 *          }
 *
 *      HTTP 400    [Error]     Returned if the 'toolId' param was not supplied.
 *          { errors: ""Missing parameter 'toolId'" }
 *
 *      HTTP 404    [Error]     Returned if a tool could not be found with the given id.
 *          { errors: "Could not find a tool with id=12345" }
 */
    .get(function (req, res) {
        //Get the toolId from the request params
        var toolId = req.params.toolId;

        //Check that a toolId was given
        if (toolId) {
            //Query the DB for a matching document
            Tool.findOne({'id': toolId}, function (err, tool) {
                //If there was an error while querying, send it as an error back to the client
                if (err)
                    res.status(404).send({errors: err});
                //If the tool retrieved is null, a matching tool was not found
                else if (tool == null)
                    res.status(404).send({errors: "Could not find a tool with id=" + toolId});
                //Otherwise, a matching tool was found
                else
                    res.status(200).send(tool);
            });
        }

        //Otherwise, the toolId is missing
        else {
            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({errors: "Missing parameter 'toolId'"});
        }
    });

/* ================================================================================================================== */
/**
 * ROUTE:       /api/tool/:toolId/:sectionName
 * METHOD(S):   GET / POST
 */
/* ================================================================================================================== */
router.route('/:toolId/:sectionName')
/**
 * Request:     GET /api/tool/:toolId/:sectionName
 * Returns:     JSON Array
 * Logged:      NO
 *
 * Description:
 * Retrieves a single tool section for a particular tool from the DB.
 *
 * Params (Required):
 *      toolId              [Number]    The id of the tool to retrieve.
 *      sectionName         [String]    The name of the section (i.e. 'About') to retrieve.
 *
 * Responses:
 *      HTTP 200    [Success]   Returned if the matching toolId and sectionName combo was found.
 *      [
 *        {
     *          "heading": "What is JIRA?",
     *          "contents": "JIRA is the name of our new Change Management System that will replace ClearQuest, CDG and CEM. JIRA is a proprietary issue tracking product, developed by [Atlassian](https://atlassian.com). It provides bug and issue tracking, and project management functions. It also provides the capability to manage Agile Backlog records."
     *        }
 *
 *        ...
 *      ]
 *
 *      HTTP 400    [Failure]   Returned if there was a missing param in the request body
 *      { errors: "Missing body parameter 'toolId'" }
 *
 *      HTTP 404    [Failure]   Returned if the matching toolId and sectionName combo was NOT found.
 *      { errors: "Could not find matching toolId and sectionName combo." }
 */
    .get(function (req, res) {
        //Get the tool id and section name from the params of the request
        var toolId = req.params.toolId;
        var sectionName = req.params.sectionName.toLowerCase();

        //Check that the params were actually supplied in the request
        if (toolId && sectionName) {
            //Look for a matching document in the DB
            Tool.findOne({'id': toolId}, function (err, tool) {
                //Catch any general errors and send them back to the client
                if (err)
                    res.status(404).send({errors: err});
                //Otherwise, there was (or was not) a matching document
                else
                //If the matching toolId + sectionName combo was not found, send back a 404
                if (tool[sectionName] == undefined || tool[sectionName] == null)
                    res.status(404).send({errors: "Could not find matching toolId and sectionName combo."});
                //Otherwise, send back the matching JSON Array
                else
                    res.status(200).send(tool[sectionName]);
            });
        }

        //Otherwise, the required data was not supplied in the request. DO NOT attempt to access the DB in this case.
        else {
            var message = "";

            //If-else block to determine which parameter was missing. Sets the message text = missing param
            if (!toolId)
                message = "Missing parameter 'toolId'.";
            else
                message = "Missing parameter 'sectionName'.";

            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({errors: message});
        }
    })

    /**
     * Request:     POST /api/tool/:toolId/:sectionName
     * Returns:     JSON Object
     * Logged:      YES
     *
     * Description:
     * Adds a new item to the tool/section name list (i.e. a new card)
     *
     * Body (Required):
     *      toolId              [Number]    The id of the tool to retrieve.
     *      sectionName         [String]    The name of the section (i.e. 'About') to retrieve.
     *
     * Responses:
     *      HTTP 201    [Success]   Returned if the new item was successfully added.
     *      { added: true }
     *
     *      HTTP 400    [Failure]   Returned if there was a missing param.
     *      { errors: "Missing parameter 'toolId'" }
     *
     *      HTTP 404    [Failure]   Returned if the matching toolId and sectionName combo was NOT found.
     *      { errors: "Could not find matching toolId and sectionName combo." }
     *
     *      HTTP 422    [Failure]   Returned if there was an error while saving the document.
     *      { added: false, errors: err }
     */
    .post(function (req, res) {
        //Get the tool id and section name from the params of the request
        var toolId = req.params.toolId;
        var sectionName = req.params.sectionName.toLowerCase();

        //Check that the params were actually supplied in the request
        if (toolId && sectionName) {
            var heading = req.body.heading;
            var contents = req.body.contents;

            //Check that the heading and contents were supplied in the body of the request
            if (heading && contents) {
                Tool.findOne({'id': toolId}, function (err, tool) {
                    //Catch any general errors and send them back to the client
                    if (err)
                        res.status(404).send({errors: err});

                    else {
                        //If the matching toolId + sectionName combo was not found, send back a 404
                        if (tool[sectionName] == undefined || tool[sectionName] == null)
                            res.status(404).send({errors: "Could not find matching toolId and sectionName combo."});
                        //Otherwise, a matching toolId and sectionName combo was found
                        else {
                            //Push a new document with the request body supplied to the sectionName array
                            tool[sectionName].push({"heading": heading, "contents": contents});

                            //Attempt to save the document (tool)
                            tool.save(function (err) {
                                //If there was an error while saving, send back a 422 (Unprocessable Entity)
                                if (err) {
                                    logger.info("[" + ip.address() + "] New item addition failed. Tool ID / Section Name=" + toolId + " " + sectionName + " | Reason= " + err);
                                    res.status(422).send({added: false, errors: err});
                                }
                                //Otherwise, the document was saved successfully
                                else {
                                    logger.info("[" + ip.address() + "] New item addition succeeded. Tool ID / Section Name=" + toolId + " " + sectionName);
                                    res.status(201).send({added: true});
                                }
                            });
                        }
                    }
                });
            }

            else {
                var errorMessage = "";

                //If-else block to determine which parameter was missing. Sets the message text = missing param
                if (!toolId)
                    errorMessage = "Missing parameter 'heading'.";
                else
                    errorMessage = "Missing parameter 'contents'.";

                //Send an HTTP 400 (Bad Request) back with the error message
                res.status(400).send({errors: errorMessage});
            }
        }

        //Otherwise, the required data was not supplied in the request. DO NOT attempt to access the DB in this case.
        else {
            var message = "";

            //If-else block to determine which parameter was missing. Sets the message text = missing param
            if (!toolId)
                message = "Missing parameter 'toolId'.";
            else
                message = "Missing parameter 'sectionName'.";

            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({errors: message});
        }
    });

/* ================================================================================================================== */
/**
 * ROUTE:       /api/tool/:toolId/:sectionName/count
 * METHOD(S):   GET / POST
 */
/* ================================================================================================================== */
router.route('/:toolId/:sectionName/count')

/**
 * Request:     GET /api/tool/:toolId/:sectionName/count
 * Returns:     JSON Object
 * Logged:      NO
 *
 * Description:
 * Retrieves the count of items in a tool & section combo.
 *
 * Params (Required):
 *      toolId              [Number]    The id of the tool to retrieve.
 *      sectionName         [String]    The name of the section (i.e. 'About') to retrieve.
 *
 * Responses:
 *      HTTP 200    [Success]   Returned if a matching tool and section combo was found.
 *      { count: 10 }
 *
 *      HTTP 400    [Failure]   Returned if there was a missing param.
 *      { errors: "Missing parameter 'toolId'" }
 *
 *      HTTP 404    [Failure]   Returned if the matching toolId and sectionName combo was NOT found.
 *      { errors: "Could not find matching toolId and sectionName combo." }
 */
    .get(function (req, res) {
        var toolId = req.params.toolId;
        var sectionName = req.params.sectionName.toLowerCase();

        //Check that the params were actually supplied in the request
        if (toolId && sectionName) {
            Tool.findOne({'id': toolId}, function (err, tool) {
                //Catch any general errors and send them back to the client
                if (err)
                    res.status(404).send({errors: err});
                //Otherwise, there was (or was not) a matching document
                else
                //If the matching toolId + sectionName combo was not found, send back a 404
                if (tool[sectionName] == undefined || tool[sectionName] == null)
                    res.status(404).send({errors: "Could not find matching toolId and sectionName combo."});
                //Otherwise, send back the count
                else
                    res.status(200).send({count: tool[sectionName].length});
            });
        }

        //Otherwise, the required data was not supplied in the request. DO NOT attempt to access the DB in this case.
        else {
            var message = "";

            //If-else block to determine which parameter was missing. Sets the message text = missing param
            if (!toolId)
                message = "Missing parameter 'toolId'.";
            else
                message = "Missing parameter 'sectionName'.";

            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({errors: message});
        }
    });

/* ================================================================================================================== */
/**
 * ROUTE:       /api/tool/:toolId/:sectionName/:itemNum
 * METHOD(S):   GET / DELETE
 */
/* ================================================================================================================== */
router.route('/:toolId/:sectionName/:itemNum')

/**
 * Request:     GET /api/tool/:toolId/:sectionName/:itemNum
 * Returns:     JSON Object
 * Logged:      NO
 *
 * Description:
 * Retrieves the particular item (i.e. card) from the given section name list for the given tool
 *
 * Params (Required):
 *      toolId              [Number]    The id of the tool to retrieve.
 *      sectionName         [String]    The name of the section (i.e. 'About') to retrieve.
 *      itemNum             [Number]    The position of the item in the list (ex: 0 = 1st item).
 *
 * Responses:
 *      HTTP 200    [Success]   Returned if a matching item was found
 *      { heading: "What is JIRA?", contents: "..." }
 *
 *      HTTP 400    [Failure]   Returned if there was a missing param.
 *      { errors: "Missing parameter 'toolId'" }
 *
 *      HTTP 404    [Failure]   Returned if the matching toolId and sectionName combo was NOT found. ALSO returned if the matching item was NOT found.
 *      { errors: "Could not find matching toolId and sectionName combo." }
 */
    .get(function (req, res) {
        var toolId = req.params.toolId;
        var sectionName = req.params.sectionName.toLowerCase();
        var itemNum = req.params.itemNum;

        //Check that the params were actually supplied in the request
        if (toolId && sectionName && itemNum) {
            Tool.findOne({'id': toolId}, function (err, tool) {
                //Catch any general errors and send them back to the client
                if (err)
                    res.status(404).send({errors: err});

                //Otherwise, there was (or was not) a matching document
                else {
                    //If the matching toolId + sectionName combo was not found, send back a 404
                    if (tool[sectionName] == undefined || tool[sectionName] == null)
                        res.status(404).send({errors: "Could not find matching toolId and sectionName combo."});

                    //Otherwise, send back the item
                    else {
                        if (tool[sectionName][itemNum] == undefined || tool[sectionName][itemNum] == null)
                            res.status(404).send({errors: "Could not find given item."});
                        else
                            res.status(200).send(tool[sectionName][itemNum]);
                    }
                }
            });
        }

        //Otherwise, the required data was not supplied in the request. DO NOT attempt to access the DB in this case.
        else {
            var message = "";

            //If-else block to determine which parameter was missing. Sets the message text = missing param
            if (!toolId)
                message = "Missing parameter 'toolId'.";
            else if (!sectionName)
                message = "Missing parameter 'sectionName'.";
            else
                message = "Missing parameter 'itemNum'.";

            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({errors: message});
        }
    })

    /**
     * Request:     DELETE /api/tool/:toolId/:sectionName/:itemNum
     * Returns:     JSON Object
     * Logged:      YES
     *
     * Description:
     * Deletes a particular item (i.e. card) from the given section name list for the given tool.
     *
     * Params (Required):
     *      toolId              [Number]    The id of the tool to retrieve.
     *      sectionName         [String]    The name of the section (i.e. 'About') to retrieve.
     *      itemNum             [Number]    The position of the item in the list (ex: 0 = 1st item).
     *
     * Responses:
     *      HTTP 200    [Success]   Returned if a matching item was found
     *      { heading: "What is JIRA?", contents: "..." }
     *
     *      HTTP 400    [Failure]   Returned if there was a missing param.
     *      { errors: "Missing parameter 'toolId'" }
     *
     *      HTTP 404    [Failure]   Returned if the matching toolId and sectionName combo was NOT found. ALSO returned if the matching item was NOT found.
     *      { errors: "Could not find matching toolId and sectionName combo." }
     *
     *      HTTP 422    [Failure]   Returned if there was an error while saving the updated document.
     *      { deleted: false, errors: "..."}
     */
    .delete(function (req, res) {
        var toolId = req.params.toolId;
        var sectionName = req.params.sectionName.toLowerCase();
        var itemNum = req.params.itemNum;

        //Check that the params were actually supplied in the request
        if (toolId && sectionName && itemNum) {
            Tool.findOne({'id': toolId}, function (err, tool) {
                //Catch any general errors and send them back to the client
                if (err)
                    res.status(404).send({errors: err});

                //Get the item that the user wants to delete
                var itemToDel = tool[sectionName][itemNum];

                //If the item doesn't exist, send an error back to the client
                if (!itemToDel) {
                    res.status(404).send({deleted: false, errors: "Item to delete was not found."})
                }

                //Otherwise, the deletion step can be executed
                else {
                    //Remove the first indexed item
                    tool[sectionName].splice(itemNum, 1);

                    //Attempt to save the tool now that item was removed
                    tool.save(function (err) {
                        //If there was an error while saving, send the error back to the client
                        if (err) {
                            logger.info("[" + ip.address() + "] Item deletion failed. Tool/Section/Item = " + toolId + "/" + sectionName + "/" + itemNum);
                            res.status(422).send({deleted: false, errors: err});
                        }
                        //Otherwise, the save was successful
                        else {
                            logger.info("[" + ip.address() + "] Item deletion succeeded. Tool/Section/Item = " + toolId + "/" + sectionName + "/" + itemNum);
                            res.status(200).send({deleted: true});
                        }
                    });
                }
            });
        }

        //Otherwise, the required data was not supplied in the request. DO NOT attempt to access the DB in this case.
        else {
            var message = "";

            //If-else block to determine which parameter was missing. Sets the message text = missing param
            if (!toolId)
                message = "Missing parameter 'toolId'.";
            else if (!sectionName)
                message = "Missing parameter 'sectionName'.";
            else
                message = "Missing parameter 'itemNum'.";

            //Send an HTTP 400 (Bad Request) back with the error message
            res.status(400).send({errors: message});
        }
    });

module.exports = router;