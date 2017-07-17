var ip = require('ip');

var Tool = require('../models/Tool');
var logger = require('../utils/logger');
var validation = require('../validation');

/*      CREATE (GUARDED)     */

/**
 * Function for creating a new Tool in the DB.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.createTool = function (req, res) {
    //Get the toolId and toolName from the body of the request
    var toolId = parseInt(req.body.toolId);
    var toolName = req.body.toolName;

    //Check that the tool id and name are valid
    var valid = validation.validateToolIdName(res, {toolId: toolId, toolName: toolName});

    //Only proceed if the parameters were valid.
    //Bad params will be handled in helper method
    if (valid) {
        //Declare a new Tool object using the model
        var newTool = new Tool({
            _id: toolId,
            id: toolId,
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
                res.status(422).send({created: false, message: message, errors: err});

                //Log this request
                logger.info("[" + ip.address() + "] New tool creation failed. Tool id= " + toolId + " Reason: " + message);
            }

            //Otherwise, the addition was successful
            else {
                //Send an HTTP 201 (Created)
                res.status(201).send({created: true});

                //Log this request
                logger.info("[" + ip.address() + "] New tool creation succeeded. toolId= " + toolId);
            }
        });
    }
};

/*      READ (UNGUARDED)        */

/**
 * Get a particular tool.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getTool = function (req, res) {
    //Get the toolId from the body of the request
    var toolId = parseInt(req.params.toolId);

    //Check that the tool id is valid.
    var valid = validation.validateToolId(res, {toolId: toolId});

    //Only proceed if the parameters were valid.
    //Bad params will be handled in helper method
    if (valid) {
        //Look for a matching document in the DB
        Tool.findOne({'id': toolId}, function (err, tool) {
            //Catch any general errors and send them back to the client
            if (err)
                res.status(404).send({message: "Error finding matching document.", errors: err});

            //Otherwise, send back the matching tool
            else {
                //If the matching matching tool could not be found
                if (tool == undefined || tool == null)
                    res.status(404).send({message: "Could not find matching tool.", errors: err});
                //Otherwise, send back the matching tool
                else
                    res.status(200).send(tool);
            }
        });
    }
};

/**
 * Function for getting a particular tool's section.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getToolSection = function (req, res) {
    //Get the tool id and section name from the params of the request
    var toolId = parseInt(req.params.toolId);
    var sectionName = req.params.sectionName.toLowerCase();

    //Check that the tool id and section name is valid.
    var valid = validation.validateToolAndSection(res, {toolId: toolId, sectionName: sectionName});

    //Only proceed if the parameters were valid.
    //Bad params will be handled in helper method
    if (valid) {
        //Look for a matching document in the DB
        Tool.findOne({'id': toolId}, function (err, tool) {
            //Catch any general errors and send them back to the client
            if (err)
                res.status(404).send({message: "Error finding matching document.", errors: err});

            //Otherwise, send back the matching tool
            else {
                //If the matching toolId + sectionName combo was not found, send back a 404
                if (tool[sectionName] == undefined || tool[sectionName] == null)
                    res.status(404).send({
                        message: "Could not find matching toolId and sectionName combo.",
                        errors: err
                    });

                //Otherwise, send back the matching section
                else
                    res.status(200).send(tool[sectionName]);
            }
        });
    }
};

/**
 * Function for getting a particular item from a tool's section.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getToolSectionItem = function (req, res) {
    //Get the tool id and section name from the params of the request
    var toolId = parseInt(req.params.toolId);
    var sectionName = req.params.sectionName.toLowerCase();
    var itemNum = parseInt(req.params.itemNum);

    //Check that the tool id, section name and item number are valid
    var valid = validation.validateToolSectionItem(res, {toolId: toolId, sectionName: sectionName, itemNum: itemNum});

    if (valid) {
        Tool.findOne({'id': toolId}, function (err, tool) {
            //Catch any general errors and send them back to the client
            if (err)
                res.status(404).send({errors: err});

            //Otherwise, there was (or was not) a matching document
            else {
                //If the matching toolId + sectionName combo was not found, send back a 404
                if (tool[sectionName] == undefined || tool[sectionName] == null)
                    res.status(404).send({
                        message: "Could not find matching toolId and sectionName combo.",
                        errors: err
                    });

                //Otherwise, send back the item
                else {
                    if (tool[sectionName][itemNum] == undefined || tool[sectionName][itemNum] == null)
                        res.status(404).send({message: "Could not find given item.", errors: err});
                    else
                        res.status(200).send(tool[sectionName][itemNum]);
                }
            }
        });
    }
};

/**
 * Function for getting the count of items in a tool's section.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getToolSectionItemCount = function (req, res) {
    //Get the tool id and section name from the params of the request
    var toolId = parseInt(req.params.toolId);
    var sectionName = req.params.sectionName.toLowerCase();

    //Check that the tool id and section name are valid.
    var valid = validation.validateToolAndSection(res, {toolId: toolId, sectionName: sectionName});

    //Only proceed if the parameters were valid.
    //Bad params will be handled in helper method
    if (valid) {
        //Look for a matching document in the DB
        Tool.findOne({'id': toolId}, function (err, tool) {
            //Catch any general errors and send them back to the client
            if (err)
                res.status(404).send({message: "Error finding matching document.", errors: err});

            //Otherwise, send back the matching tool
            else {
                //If the matching toolId + sectionName combo was not found, send back a 404
                if (tool[sectionName] == undefined || tool[sectionName] == null)
                    res.status(404).send({
                        message: "Could not find matching toolId and sectionName combo.",
                        errors: err
                    });
                //Otherwise, send back the matching section
                else
                    res.status(200).send({count: tool[sectionName].length});
            }
        });
    }
};

/*      UPDATE (GUARDED)      */

/**
 * Function for adding an item to a tool's section
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
//TODO: Add this
exports.addItem = function (req, res) {
};

/*      DELETE (GUARDED)      */

/**
 * Function for deleting an item from a tool's section.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
//TODO: Add this
exports.deleteItem = function (req, res) {
};

/**
 * Function for deleting a tool from the DB.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.deleteTool = function (req, res) {
    //Get the tool id and section name from the params of the request
    var toolId = parseInt(req.params.toolId);

    //Check that the tool id is valid.
    var valid = validation.validateToolId(res, {toolId: toolId});

    if (valid) {
        Tool.remove({_id: toolId}, function (err) {
            if (err)
                res.status(404).send({deleted: false, message: "Error finding matching document.", errors: err});
            else
                res.status(200).send({deleted: true});
        });
    }
};


