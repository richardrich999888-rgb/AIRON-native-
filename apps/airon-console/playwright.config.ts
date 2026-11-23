import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/ui",
  timeout: 90000,
  workers: 1,
  expect: {
    toHaveScreenshot: {
      pathTemplate: "{testDir}/visual-baselines/{testFileName}/{arg}{ext}",
      maxDiffPixelRatio: 0.007,
    },
  },
  retries: 0,
  reporter: "line",
  outputDir: ".sites-runtime/ui-results",
  use: {
    browserName: "chromium",
    viewport: { width: 1440, height: 900 },
    headless: true,
    launchOptions: process.env.VANIAN_CHROMIUM
      ? { executablePath: process.env.VANIAN_CHROMIUM }
      : {},
  },
  fullyParallel: false,
});
