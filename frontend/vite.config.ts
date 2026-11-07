import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';

// Opt-in React 19 bundle. A release must build and test it before switching
// FRONTEND_MODE=modern on the API server. Legacy assets remain untouched.
export default defineConfig({
  root: fileURLToPath(new URL('./modern', import.meta.url)),
  base: '/assets/modern/',
  esbuild: { jsx: 'transform', jsxFactory: 'React.createElement', jsxFragment: 'React.Fragment' },
  build: {
    target: 'es2022',
    outDir: fileURLToPath(new URL('./public/modern', import.meta.url)),
    emptyOutDir: true,
    sourcemap: false,
    manifest: true,
  },
});
