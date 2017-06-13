/* API Routes for /api/news/ (Unguarded Routes) */

var router = require('express').Router();

var newsCtrl = require('../../controllers/news');

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

router.route('/')

//Get all news items
    .get(function (req, res) {
        newsCtrl.getAll(req, res);
    });

module.exports = router;