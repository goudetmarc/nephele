// @ts-check
/**
 * Génère un PNG en mémoire, sans dépendance (zlib du cœur de Node).
 *
 * On ne peut pas piloter un vrai choix de fichier dans un test ; on fabrique
 * donc une image porteuse de structure (blocs, diagonales, disque) pour que
 * la binarisation en planches produise de vrais contours plutôt qu'un aplat.
 */
const zlib = require('zlib');

function crc32(buf) {
  let c = ~0;
  for (let i = 0; i < buf.length; i++) {
    c ^= buf[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xEDB88320 & -(c & 1));
  }
  return (~c) >>> 0;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const typeBuf = Buffer.from(type, 'ascii');
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([len, typeBuf, data, crc]);
}

/**
 * @param {number} width
 * @param {number} height
 * @returns {Buffer} un PNG niveaux de gris 8 bits avec un motif contrasté
 */
function pngBuffer(width = 128, height = 128) {
  // Scanlines : chaque ligne préfixée d'un octet de filtre (0 = aucun).
  const raw = Buffer.alloc((width + 1) * height);
  let o = 0;
  const cx = width / 2, cy = height / 2, r = Math.min(width, height) * 0.28;
  for (let y = 0; y < height; y++) {
    raw[o++] = 0; // filtre
    for (let x = 0; x < width; x++) {
      let v = 200;
      // damier grossier
      if (((x >> 4) + (y >> 4)) & 1) v = 90;
      // bande diagonale sombre
      if (Math.abs(((x + y) % 48) - 24) < 6) v = 40;
      // disque clair excentré
      const dx = x - cx * 0.7, dy = y - cy * 1.2;
      if (dx * dx + dy * dy < r * r) v = 235;
      raw[o++] = v;
    }
  }
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;   // profondeur
  ihdr[9] = 0;   // type couleur : niveaux de gris
  ihdr[10] = 0;  // compression
  ihdr[11] = 0;  // filtre
  ihdr[12] = 0;  // entrelacement
  const idat = zlib.deflateSync(raw);
  return Buffer.concat([
    sig,
    chunk('IHDR', ihdr),
    chunk('IDAT', idat),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

module.exports = { pngBuffer };
