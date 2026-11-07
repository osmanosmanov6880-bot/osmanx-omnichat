/** Transitional React 19 entry: preserve the single reviewed app component.
 *
 * The existing app.tsx uses the classic global JSX runtime. Rather than fork
 * the entire Inbox during the migration, provide only the legacy mount bridge.
 * No React 16 scripts are loaded in this mode.
 */
import * as React from 'react';
import { createRoot } from 'react-dom/client';

(globalThis as any).React = React;
const roots = new WeakMap<Element, ReturnType<typeof createRoot>>();
(globalThis as any).ReactDOM = {
  render(element: any, container: Element | null) {
    if (!container) throw new Error('Root element not found');
    let root = roots.get(container);
    if (!root) {
      root = createRoot(container);
      roots.set(container, root);
    }
    root.render(element);
  },
};

// A dynamic import is important: its module body runs after global React and
// the createRoot bridge are installed. ES static imports run before this code.
// @ts-ignore TS2306: app.tsx is intentionally a legacy script; Vite imports it for side effects.
void import('./app');
