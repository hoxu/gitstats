/* API Routes for /api/admin/guarded (Guarded Routes) */

var router = require('express').Router();

var adminCtrl = require('../../controllers/admin');
var adminGuard = require('../../guards/adminGuard');

//Middleware to use for every request
router.use(function (req, res, next) {
    //Use the admin guard
    adminGuard.adminGuard(req, res, next);
});

router.route('/')
//Creates a new admin
    .post(function (req, res) {
        adminCtrl.createAdmin(req, res)
    });

module.exports = router;