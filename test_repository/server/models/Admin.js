/* Model for an Admin in the DB */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var AdminSchema = new Schema(
    {
        _id: String,

        username: {
            type: String,
            required: true
        },

        password: {
            type: String,
            required: true
        },

        name: String,
        description: String
    },
    {
        collection: 'admins'
    }
);

module.exports = mongoose.model('Admin', AdminSchema);