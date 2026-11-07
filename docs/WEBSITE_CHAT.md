# Website Chat - first-party messaging channel (v0.3)

This feature is real code, not a mock adapter. A business can use it to handle visitor conversations without permission from Meta or Avito. It is available in both local demo and registered workspaces. A demo workspace labels all messages as test traffic.

## Set up

1. Sign in as an owner or administrator, open **Sites / Web Chat**, and create a widget with a descriptive name.
2. Add exact website origins such as `https://shop.example.com` and `https://www.shop.example.com`. The protocol and subdomain matter. Up to 15 origins are accepted. HTTP is accepted only for `localhost` and `127.0.0.1` development sites.
3. Copy the installation snippet displayed in the UI. It looks like this, with a **real generated public key**, not the sample key below:

```html
<script async src="https://chat.example.com/assets/embed.js" data-omnichat-key="YOUR_PUBLIC_WIDGET_KEY"></script>
```

4. Place the script near `</body>` on an allowed website. If your site enforces Content Security Policy, authorize the chat domain in `script-src`, `style-src`, and `frame-src`. The launcher CSS is served as an external stylesheet: no unsafe-inline permission is required.
5. Open your website and start a test conversation. The visitor messages appear in the unified Inbox with the **Website** source badge. An agent replies in the same conversation. The visitor sees the reply on the website.

## Trust boundaries

- `public_key`: **public routing identifier**, safe to embed. Not an authorization credential.
- `visitor_token`: randomly generated secret bearer token, held by the browser in tab-scoped `sessionStorage`. Only SHA-256 is stored in the database. No third-party cookie is needed.
- A visitor can only read the conversation linked to their own token; reading without a token returns HTTP 401. Browser session expiration: 30 days from creation, or earlier if the widget is disabled or organization deleted.
- Rotating the public widget key invalidates old embed URLs, but existing visitor sessions are still bound to the widget and work with the new key. If immediate revocation of all visitors is required, disable the widget or explicitly delete sessions.
- Website iframe rendering uses `frame-ancestors 'self' <allowed-origins>` on **widget HTML responses only**. Other application pages reject embedding.
- Visitors cannot read agent notes, CRM contacts, other visitors' messages, other organizations, or API credentials.
- Incoming message nonces are unique within the generated visitor ID; a network retry with the same nonce does not duplicate the message.
- In-memory throttling is best-effort for single-node demos. Deploy a shared production rate limiter and abuse controls before opening the public endpoint to the internet.

## API shape

Admin (session cookie, CSRF, RBAC):

- `GET /api/website-widgets`
- `POST /api/website-widgets`: `{name, allowed_origins: [...], greeting, accent}`
- `PATCH /api/website-widgets/{widget_id}`: same fields plus `enabled`
- `POST /api/website-widgets/{widget_id}/rotate-key`

Public widget (no organizational session cookie):

- `GET /api/public/widget/{key}/bootstrap`
- `POST /api/public/widget/{key}/session`: `{name}`; returns an opaque `visitor_token`
- `GET /api/public/widget/{key}/messages` with `X-Widget-Session: {visitor_token}`
- `POST /api/public/widget/{key}/messages` with that header: `{body, client_nonce}`

Only server-approved website origins may **embed** the iframe. The public API remains accessible to non-browser HTTP clients because no browser-only origin restriction is equivalent to authentication; token checks and throttling still apply.

## Limitations and next gates

- Text messages only: attachments, typing indicators and attachments scanning are not implemented for first-party chat.
- Browser polling every three seconds is adequate for small pilots, but not an optimized high-volume infrastructure.
- Chat content retention follows the organization policy; visitor session expiry runs in the dedicated worker.
- No end-to-end encryption claim is made. HTTPS protects data in transit, and ordinary database controls protect stored messages.
- The embed includes a separate external `embed.css`. Merchant CSP must explicitly permit this stylesheet and the chat iframe. Production rollout must include a CSP compatibility test on the merchant's actual website.
