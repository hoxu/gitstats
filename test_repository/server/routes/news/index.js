/* API Routes for /api/news/... (Guarded/Unguarded Routes) */

var router = require('express').Router();

router.use('/', require('./unguarded'));
router.use('/guarded', require('./guarded'));

module.exports = router;