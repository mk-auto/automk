import { createServer } from "node:http";
import { readFile, readdir, stat } from "node:fs/promises";
import { join } from "node:path";

const DIR = "/Users/daodilyas/Desktop/automk/.superpowers/mockups";
const PORT = 4178;

async function newest() {
  const files = (await readdir(DIR)).filter((f) => f.endsWith(".html"));
  let best = null, bestM = -1;
  for (const f of files) {
    const m = (await stat(join(DIR, f))).mtimeMs;
    if (m > bestM) { bestM = m; best = f; }
  }
  return best;
}

const NOCACHE = { "Cache-Control": "no-store, must-revalidate", "Pragma": "no-cache" };

createServer(async (req, res) => {
  try {
    const url = new URL(req.url, "http://x");
    let name = decodeURIComponent(url.pathname).replace(/^\/+/, "");
    if (name === "" || name === "index.html") name = await newest();
    if (name === "list") {
      const files = (await readdir(DIR)).filter((f) => f.endsWith(".html"));
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", ...NOCACHE });
      return res.end(`<h2>Mockups</h2><ul>${files.map((f) => `<li><a href="/${f}">${f}</a></li>`).join("")}</ul>`);
    }
    const body = await readFile(join(DIR, name));
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", ...NOCACHE });
    res.end(body);
  } catch (e) {
    res.writeHead(404, { "Content-Type": "text/plain", ...NOCACHE });
    res.end("Not found: " + e.message);
  }
}).listen(PORT, () => console.log(`mockups on http://localhost:${PORT} (serves newest .html; /list for all)`));
