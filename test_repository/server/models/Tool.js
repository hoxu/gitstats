/* Model for an Tool in the DB */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var ToolSchema = new Schema(
    {
        _id: Number,
        id: Number,
        name: String,

        about: Array,
        training: Array,
        links: Array
    },
    {
        collection: 'tools'
    }
);

module.exports = mongoose.model('Tool', ToolSchema);