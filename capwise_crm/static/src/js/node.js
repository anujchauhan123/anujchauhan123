const crypto = require("crypto");

// const args = process.argv;
// console.log("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",args);




const encryption_key = "capewise0$02encryptionkey@23450$";
let iv_length = "16";
let text = JSON.stringify({
  errorString: null,
  stgOneHitId: "309214964",
  stgTwoHitId: "303673093",
});
function decrypt(encrypted_text) {
  let textParts = encrypted_text.includes(":") ? encrypted_text.split(":") : [];
  let iv = Buffer.from(textParts.shift() || "", "binary");
  let encryptedText = Buffer.from(textParts.join(":"), "hex");
  let decipher = crypto.createDecipheriv(
    "aes-256-cbc",
    Buffer.from(encryption_key),
    iv
  );
  let decrypted = decipher.update(encryptedText);

  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return decrypted.toString();
}

function encrypt(plain_text) {
  iv_length = Number(iv_length);
  let iv = Buffer.from(crypto.randomBytes(iv_length))
    .toString("hex")
    .slice(0, iv_length);
  let cipher = crypto.createCipheriv(
    "aes-256-cbc",
    Buffer.from(encryption_key),
    iv
  );
  let encrypted = cipher.update(plain_text);

  encrypted = Buffer.concat([encrypted, cipher.final()]);
  return iv + ":" + encrypted.toString("hex");
}
// const a = encrypt(text);
// const b = decrypt(a);

process.argv.forEach(function (val, index, array) {
  if (index == 2){
    const a = decrypt(val)
    console.log(a)
  }
});
// console.log(a);
// console.log(b);

