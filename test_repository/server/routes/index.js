//Top-Level Router
//Mounts all the individual routes on a single router that the app can then use

var router = require('express').Router();

//NOTE: Each 'sub-router' should go below and use the following convention:
//router.use(<PATH>, require(<MODULE>));
//where PATH = sub-path of main router
//where MODULE = the module containing the exported sub-router

//Mount the 'admin' router onto the API Router
//URL will look like this: '.../api/admin/...'
router.use('/admin', require('./admin'));

//Mount the 'admins' router onto the API Router
//URL will look like this: '.../api/admins/...'
router.use('/admins', require('./admins'));

//Mount the 'news' router onto the API Router
//URL will look like this: '.../api/news/...'
router.use('/news', require('./news'));

//Mount the 'tool' router onto the API Router
//URL will look like this: '.../api/tool/...'
router.use('/tool', require('./tool'));

//Mount the 'tools' router onto the API Router
//URL will look like this: '.../api/tools/...'
router.use('/tools', require('./tools'));

//Mount the 'jira' router on the API Router
//URL will look like this: '.../api/jira/...'
router.use('/jira', require('./jira'));


//!IMPORTANT! We need to export the router so our app can use the router
module.exports = router;