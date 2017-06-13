/* Model for a News item in the DB */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var NewsItemSchema = new Schema(
    {
        title: String,

        contents: String,

        date: {
            type: Date,
            default: Date.now
        }
    },
    {
        collection: 'news'
    }
);

module.exports = mongoose.model('NewsItem', NewsItemSchema);