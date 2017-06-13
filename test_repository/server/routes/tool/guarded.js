/* API Routes for /api/tool/guarded (Guarded Routes) */

var router = require('express').Router();
var config = require('../../config');

var adminGuard = require('../../guards/adminGuard');
var toolCtrl = require('../../controllers/tool');

//Middleware to use for every request
router.use(function (req, res, next) {
    //Use the admin guard
    adminGuard.adminGuard(req, res, next);
});

router.route('/')

//Creates a new tool in the DB
    .post(function (req, res) {
        toolCtrl.createTool(req, res)
    });

router.route('/:toolId')

//Deletes a tool in the DB
    .delete(function (req, res) {
        toolCtrl.deleteTool(req, res)
    });

router.route('/:toolId/:sectionName')

//Adds a new item (i.e. card) to a tool section
    .post(function (req, res) {
        toolCtrl.addItem(req, res)
    });

router.route('/:toolId/:sectionName/:item')

//Deletes an item (i.e. card) from a tool section
    .delete(function (req, res) {
        toolCtrl.deleteItem(req, res)
    });

module.exports = router;