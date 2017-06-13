/* Encryption helper functions */

var bcrypt = require('bcryptjs');

const ROUNDS = 10;

//Generate the salted hash given a String and a work factor (constant)
var generateHash = function generateHash(text) {
    var salt = bcrypt.genSaltSync(ROUNDS);
    return bcrypt.hashSync(text, salt);
};

//If the password in the DB (HASHED PWD) = password passed in (HASHED PWD), it is a valid pass
var checkPass = function checkPass(plainPass, hashedPass) {
    return bcrypt.compareSync(plainPass, hashedPass);
};

exports.generateHash = generateHash;
exports.checkPass = checkPass;