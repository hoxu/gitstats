/* API Routes for /api/tool/ (Unguarded Routes) */

var router = require('express').Router();
var toolCtrl = require('../../controllers/tool');

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

router.route('/:toolId')

//Get a particular tool
    .get(function (req, res) {
        toolCtrl.getTool(req, res);
    });

router.route('/:toolId/:sectionName')

//Get a particular tool's section
    .get(function (req, res) {
        toolCtrl.getToolSection(req, res);
    });

router.route('/:toolId/:sectionName/count')

//Get the count of items in a tool's section
    .get(function (req, res) {
        toolCtrl.getToolSectionItemCount(req, res);
    });

router.route('/:toolId/:sectionName/:itemNum')

//Get a particular item for a tool's section
    .get(function (req, res) {
        toolCtrl.getToolSectionItem(req, res);
    });

module.exports = router;