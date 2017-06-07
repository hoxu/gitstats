/* Admin password encryption */

var minimist = require('minimist')(process.argv.slice(2));
var bcrypt = require('bcryptjs');

var rounds = 10;

if (minimist.r || minimist.rounds)
    rounds = parseInt(minimist.r);

if (minimist.i || minimist.in)
    generateHash(rounds, minimist.i);

else {
    console.error("NO INPUT SUPPLIED!");
}

function generateHash(rounds, text) {
    console.log("Hashing with " + rounds + " rounds");

    var salt = bcrypt.genSaltSync(rounds);
    var hash = bcrypt.hashSync(text, salt);

    console.log("HASH: " + hash);
}