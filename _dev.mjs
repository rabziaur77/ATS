/* Launch Vite dev server for local verification. */
import { createServer } from "vite";

const server = await createServer({
  server: { port: 5173, host: "127.0.0.1", strictPort: true },
});
await server.listen();
console.log("vite listening on http://127.0.0.1:5173");
