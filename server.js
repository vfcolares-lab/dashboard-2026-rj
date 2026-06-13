const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 8000;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.csv': 'text/csv'
};

const server = http.createServer((req, res) => {
  // Parse URL
  const parsedUrl = url.parse(req.url, true);
  let filePath = path.join(__dirname, parsedUrl.pathname);

  // Default to index.html
  if (filePath.endsWith('/') || parsedUrl.pathname === '/') {
    filePath = path.join(__dirname, 'index.html');
  }

  // Security: prevent directory traversal
  const realPath = fs.realpathSync(__dirname);
  if (!fs.realpathSync(filePath).startsWith(realPath)) {
    res.writeHead(403, { 'Content-Type': 'text/html' });
    res.end('<h1>403 - Forbidden</h1>', 'utf-8');
    return;
  }

  // Read and serve file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      // If file not found and it's not index.html, try index.html
      if (err.code === 'ENOENT' && filePath !== path.join(__dirname, 'index.html')) {
        fs.readFile(path.join(__dirname, 'index.html'), (err2, data2) => {
          if (err2) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 - Not Found</h1>', 'utf-8');
            return;
          }
          res.writeHead(200, { 'Content-Type': MIME_TYPES['.html'] });
          res.end(data2);
        });
      } else {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 - Not Found</h1>', 'utf-8');
      }
      return;
    }

    // Serve file
    const ext = path.extname(filePath).toLowerCase();
    const mimeType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, {
      'Content-Type': mimeType,
      'Cache-Control': 'public, max-age=3600'
    });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log(`✅ Dashboard RJ rodando em http://localhost:${PORT}`);
});
