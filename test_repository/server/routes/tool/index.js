/* API Routes for /api/tool/... (Guarded/Unguarded Routes) */

var router = require('express').Router();

router.use('/', require('./unguarded'));
router.use('/guarded', require('./guarded'));

module.exports = router;