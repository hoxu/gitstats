/* API Routes for /api/news/guarded (Guarded Routes) */

var router = require('express').Router();

var newsCtrl = require('../../controllers/news');
var adminGuard = require('../../guards/adminGuard');

//Middleware to use for every request
router.use(function (req, res, next) {
    //Use the admin guard
    adminGuard.adminGuard(req, res, next);
});

router.route('/')

//Creates a new news item
    .post(function (req, res) {
        newsCtrl.createNewsItem(req, res)
    });

module.exports = router;