/* Common validation functions */

var Joi = require('joi');

/**
 * Validator for a new News item.
 * Checks that a title String and contents String was supplied.
 *
 * @param res The response object passed over from calling method (so that an error can be sent if validation fails)
 * @param params The params to validate the schema against
 */
exports.validateNewsItem = function (res, params) {
    var schema = {
        title: Joi.string().required(),
        contents: Joi.string().required()
    };

    return commonValidator(res, schema, params);
};

/**
 * Validator for a user/pass combo.
 * Checks that a username String and password String was supplied.
 *
 * @param res The response object passed over from calling method (so that an error can be sent if validation fails)
 * @param params The params to validate the schema against
 */
exports.validateUserPass = function (res, params) {
    var schema = {
        username: Joi.string().required(),
        password: Joi.string().required()
    };

    return commonValidator(res, schema, params);
};

/**
 * Validator for a tool id.
 * Checks that the tool id is a positive integer.
 *
 * @param res The response object passed over from calling method (so that an error can be sent if validation fails)
 * @param params The params to validate the schema against
 */
exports.validateToolId = function (res, params) {
    var schema = {
        toolId: Joi.number().integer().positive().required()
    };

    return commonValidator(res, schema, params);
};

/**
 * Validator for a tool id and tool name.
 * Checks that the tool id is a positive integer and that the tool name is a String.
 *
 * @param res The response object passed over from calling method (so that an error can be sent if validation fails)
 * @param params The params to validate the schema against
 */
exports.validateToolIdName = function (res, params) {
    var schema = {
        toolId: Joi.number().integer().positive().required(),
        toolName: Joi.string().required()
    };

    return commonValidator(res, schema, params);
};

/**
 * Validator for a tool id and section name.
 * Checks that the tool id is a positive integer and that the tool section is a String.
 *
 * @param res The response object passed over from calling method (so that an error can be sent if validation fails)
 * @param params The params to validate the schema against
 */
exports.validateToolAndSection = function (res, params) {
    var schema = {
        toolId: Joi.number().integer().positive().required(),
        sectionName: Joi.string().required()
    };

    return commonValidator(res, schema, params);
};

/**
 * Validator for a tool id, section name and item number.
 * Checks that the tool id is a positive integer, that the tool section is a String and that the item number is positive integer.
 *
 * @param res The response object passed over from calling method (so that an error can be sent if validation fails)
 * @param params The params to validate the schema against
 */
exports.validateToolSectionItem = function (res, params) {
    var schema = {
        toolId: Joi.number().integer().positive().required(),
        sectionName: Joi.string().required(),
        itemNum: Joi.number().integer().positive().required()
    };

    return commonValidator(res, schema, params);
};

/**
 * Validator helper method. Wraps the Joi.validate() method such that params are checked against a schema.
 * Also sends back a generic HTTP 400 for a bad request.
 * @param res The response object sent from calling method so that errors can be sent back to client.
 * @param schema The schema to validate the params against.
 * @param params The params to validate the schema against.
 * @returns {boolean} The validity of the params (i.e. do they fulfil the requirements).
 */
function commonValidator(res, schema, params) {
    var valid = false;

    //Run the validation
    Joi.validate(params, schema, function (err, value) {
        //If there is no error, the params are valid.
        if (err == null)
            valid = true;
        //Otherwise, the params are invalid, and we should send back an error to the client
        else {
            res.status(400).send({message: "Missing/Bad params.", errors: err});
            valid = false;
        }
    });

    //The caller needs to know if the validation went through successfully or not, so send back the Boolean.
    return valid;
}