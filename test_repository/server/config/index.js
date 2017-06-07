/* Configuration file for the server */

var config = {};

config.db = {};
config.db.tools = {};

config.jira = {};
config.jira.api = {};
config.jira.toolSupport = {};

//Server Config
config.httpPort = 8081;
config.httpsPort = 8443;
config.secretKey = "38107824-cdc7-4769-8aa2-1eac80993245";

//MongoDB Config
config.db.username = "portalServer";
config.db.password = "T00lsTeam";
config.db.tools.path = "mongodb://localhost:27017/portal";

//JIRA Config
//URL to use for JIRA REST API calls (dev/prod)
//Prod = https://jiraemv.zebra.com
//Dev = https://dev-jiraemv.zebra.lan OR https://10.183.4.31
//config.jira.url = "10.183.4.31";
config.jira.url = "dev-jiraemv.zebra.lan";

//API endpoints
config.jira.api.user = "/rest/api/2/user";
config.jira.api.login = "/rest/auth/1/session";
config.jira.api.issue = "/rest/api/2/issue";

//Project/Issue
config.jira.toolSupport.projectId = 10300;
config.jira.toolSupport.requestId = 11200;
config.jira.toolSupport.changeId = 11201;

module.exports = config;
