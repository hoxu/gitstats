/* API Routes for /api/admin/ (Unguarded Routes) */

var router = require('express').Router();

var adminCtrl = require('../../controllers/admin');

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

router.route('/login')

//Authenticates admin
    .post(function (req, res) {
        adminCtrl.login(req, res);
    });

module.exports = router;