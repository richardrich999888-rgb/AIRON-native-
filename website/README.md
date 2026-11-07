# AIRON Native website

A standalone copy of the SYNTRIASS Labs Sites interface, prepared for static hosting on Netlify or Vercel. It uses the original logo, local bundled assets, and the existing synthetic demo workflow.

- `app/page.tsx`: the interface.
- `app/globals.css`: layout and styling.
- `lib/`: deterministic retrieval and local record integrity.
- `public/`: original logo and downloadable offline kit.
- `offline/`: local Python/Ollama demo gateway and its tests.
- `tests/`: existing retrieval, access, abstention and record checks.

Use Node.js 22.18+ (22.x recommended): `npm ci`, `npm test`, `npm run build`.
Run `npm run dev` for development. See [deployment instructions](../DEPLOYMENT.md).

The hosted version executes no model and contacts no external AI API. Browser role selection is a demonstration, not authentication; all included documents are synthetic. Records remain unsigned and locally editable. The separate loopback runtime uses a server-bound role and a pairing token; it is a scaffold, not production identity. Real-model behavior, physical air-gap isolation, hardware efficiency and AIP signing still require validation.

The original Sites publication is unchanged by this export. Changes to this copy do not automatically synchronize back to Sites.
