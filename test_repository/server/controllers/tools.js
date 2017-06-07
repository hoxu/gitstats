var ip = require('ip');

var Tool = require('../models/Tool');
var logger = require('../utils/logger');
var validation = require('../validation');

/*      CREATE (GUARDED)        */

/*      READ (UNGUARDED)        */

/**
 * Function for getting all the tools from the DB.
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getTools = function (req, res) {
    //Find all tools
    Tool.find({}, function (err, tools) {
        if (err)
            res.status(404).send({message: "Could not retrieve Tools.", errors: err});
        else
            res.status(200).send(tools);
    });
};

/**
 * Function for getting info for all the tools (ids and names)
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getToolInfo = function (req, res) {
    //Find all tools, only returning the id and name for each
    Tool.find({}, {_id: false, id: true, name: true}, function (err, tools) {
        if (err)
            res.status(404).send({message: "Could not retrieve Tools.", errors: err});
        else
            res.status(200).send(tools);
    });
};

/**
 * Function for getting all the tool names
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getToolNames = function (req, res) {
    //Find all tools, only returning the name
    Tool.find({}, {_id: false, name: true}, function (err, tools) {
        var toolsMap = [];

        tools.forEach(function (tool) {
            toolsMap.push(tool.name);
        });

        if (err)
            res.status(404).send({message: "Could not retrieve Tools.", errors: err});
        else
            res.status(200).send(toolsMap);
    });
};

/**
 * Function for getting all the tool ids
 * @param req The request object sent over from the route.
 * @param res The response object sent over from the route.
 */
exports.getToolIds = function (req, res) {
    //Find all the tools, only returning the id
    Tool.find({}, {_id: false, id: true}, function (err, tools) {
        var toolsMap = [];

        tools.forEach(function (tool) {
            toolsMap.push(tool.id);
        });

        if (err)
            res.status(404).send({message: "Could not retrieve Tools.", errors: err});
        else
            res.status(200).send(toolsMap);
    });
};

/*      UPDATE (GUARDED)        */

/*      DELETE (GUARDED)        */