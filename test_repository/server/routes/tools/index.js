//TODO: Modify this to use controllers/guards

/* API Routes for /api/tools/ (Unguarded Routes) */

var router = require('express').Router();

var toolsCtrl = require('../../controllers/tools');

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

router.route('/')

//Get all the tools from the DB
    .get(function (req, res) {
        toolsCtrl.getTools(req, res);
    });

router.route('/info')

//Get info on all the tools (ids and names)
    .get(function (req, res) {
        toolsCtrl.getToolInfo(req, res);
    });

router.route('/names')

//Get all tool names
    .get(function (req, res) {
        toolsCtrl.getToolNames(req, res);
    });

router.route('/ids')

//Get all tool ids
    .get(function (req, res) {
        toolsCtrl.getToolIds(req, res);
    });

module.exports = router;