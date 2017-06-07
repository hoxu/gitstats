# Zebra EMC TOOLS TEAM PORTAL

## Overview
The EMC Engineering Tools Portal is a PoC (Proof of Concept) to determine if it is possible to integrate the EMC Eng. Tools into a centralized location to increase development efficiency.

## Prerequisites
### MongoDB (NoSQL Database): https://www.mongodb.com/

### Express.js (Web Application Framework): http://expressjs.com/

### Polymer (Front-end Framework/Library): https://www.polymer-project.org/1.0/ 
### Node.js (Server): https://nodejs.org/en/

## Install
```bash
# Clone the project from:
http://ny21gitapp01.zebra.lan:8080/#/admin/projects/EMC_Engineering_Tools/Tools_Portal

# Install npm modules
$ cd Tools_Portal
$ npm install

# Install bower packages
$ cd app
$ bower install

# Run gulp default
$ gulp default

# Star the service
$ node server/server.js -p -t
```