const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  try {
    const filePath = path.join(__dirname, '../data-rj.js');

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'data-rj.js not found' });
    }

    const fileContent = fs.readFileSync(filePath, 'utf8');

    res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=86400');
    res.status(200).send(fileContent);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
