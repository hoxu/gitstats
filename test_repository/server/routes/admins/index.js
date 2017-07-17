//TODO: Modify this to use controllers/guards
/* API Routes for /api/admins/ (Unguarded Routes) */

var router = require('express').Router();
var Admin = require('../../models/Admin');

//Middleware to use for every request
router.use(function (req, res, next) {
    next();
});

router.route('/info')
//Gets all admin names/descriptions
    .get(function (req, res) {
        Admin.find({}, 'name description', function (err, admins) {
            if (err)
                res.send({errors: err});
            else
                res.status(200).send(admins);
        })
    });

module.exports = router;