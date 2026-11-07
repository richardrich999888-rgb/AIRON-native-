# Host the AIRON Native website

The complete website lives in `website/`. Both hosts serve the same static build; no runtime secrets, database, cloud inference or Sites login dependency is required.

## Vercel

1. Import `richardrich999888-rgb/AIRON-native-` from GitHub.
2. Select branch `main`. Keep **Root Directory** at the repository root (`.`).
3. The root `vercel.json` sets **Framework Preset: Other**, install command `npm --prefix website ci`, build command `npm --prefix website run build`, and output directory `website/dist`.
4. Use Node.js 22.x, as declared in the root `package.json`. Deploy.

Do not set the Vercel root to `website/` with this configuration: the commands intentionally include that prefix. Future commits to the linked production branch trigger deployments once the Git integration is enabled.

## Netlify

1. Import the same GitHub repository and select branch `main`.
2. Let the root `netlify.toml` configure the site: **Base directory** `website`, **Build command** `npm run build`, **Publish directory** `dist` (relative to the base).
3. Node.js 22 is set in that file. Deploy.

No environment variables are required on either host. Review the provider's access settings when sharing a customer-specific demonstration; the hosted version contains only public synthetic fixtures. The ChatGPT Sites private sign-in gate does not transfer to these hosts.

## Verify the deployment

- Open the home page and select **Try AIRON**.
- Run the three examples: sourced answer, restricted access, and insufficient evidence.
- Inspect a source and an execution record, then run the checks under **Project details → Tests**.
- Download the local kit and verify the logo and static assets load.

This public web demonstration does not claim to be an air-gapped deployment. For local inference, extract the kit and follow its README. Keep the Python gateway bound to loopback; never deploy it as a public serverless function. Models and Ollama must be provisioned separately.

## Rebuild locally

```sh
cd website
npm ci
npm test
npm run build
npm run preview
```

The output is `website/dist/`. For a manual static upload, upload its contents, including `assets/`, the original logo and the offline kit.

## Update the offline kit

After editing shared UI, retrieval code or the local gateway, rebuild the kit before the website:

```sh
cd website
npm ci
npm run package:offline
npm run build
```

Kit generation needs Python 3.10+ at development time. Hosting builds use the checked-in kit and do not require Python. The Python gateway has no third-party Python dependencies. Commit the updated `public/airon-offline-kit.zip` and `offline/documents.json` with the source change.

Configuration references: [Vercel](https://vercel.com/docs/project-configuration) · [Netlify](https://docs.netlify.com/build/configure-builds/file-based-configuration/).
