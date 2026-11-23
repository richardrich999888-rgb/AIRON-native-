import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { mkdtemp, mkdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { testSite } from "../support/site.mjs";

test("operator imports, teaches, approves, retrieves after restart and exports on the production UI", async ({
  browser,
}) => {
  test.setTimeout(300000);
  const root = await mkdtemp(join(tmpdir(), "airon-ciic-"));
  const site = await testSite({ port: 8787 });
  const ui = "http://127.0.0.1:8787";
  const start = () =>
    spawn(
      "python3",
      ["intelligence/local_api.py", "--demo-personas", "--directory", root],
      { stdio: "ignore" },
    );
  let service = start();
  const ready = () =>
    expect
      .poll(async () => {
        try {
          return (
            await fetch("http://127.0.0.1:8766/knowledge/info", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: "{}",
            })
          ).status;
        } catch {
          return 0;
        }
      })
      .toBe(200);
  const stop = async () => {
    if (service.exitCode === null && service.signalCode === null) {
      const exited = once(service, "exit");
      service.kill();
      await exited;
    }
  };
  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 },
  });
  const page = await context.newPage();
  const output = process.env.CIIC_CAPTURE_DIR;
  const shot = async (p: Page, name: string) => {
    await p.evaluate(() => document.fonts.ready);
    if (name.includes("login") || /^0[2-8]-/.test(name) || name === "12-mobile-vault") {
      const scan = await new AxeBuilder({ page: p }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
      expect(scan.violations.filter((v) => v.impact === "serious" || v.impact === "critical")
        .map((v) => [v.id, v.nodes.map((n) => n.target)]), name).toEqual([]);
    }
    if (output) {
      await mkdir(output, { recursive: true });
      await p.screenshot({
        path: join(output, name + ".png"),
        animations: "disabled",
      });
    }
  };
  const route = async (p: Page, slug: string, title: string) => {
    await p.goto(ui + "/" + slug);
    await expect(
      p.getByRole("heading", { name: title, exact: true, level: 1 }),
    ).toBeVisible();
  };
  const pair = async (p: Page, actor: string) => {
    if (await p.getByRole("button", { name: "Switch identity" }).isVisible())
      await p.getByRole("button", { name: "Switch identity" }).click();
    await p.getByLabel("Demonstration identity").selectOption(actor);
    await p
      .getByRole("button", { name: "Open workspace", exact: true })
      .click();
    await expect(
      p.getByRole("button", { name: "Switch identity" }),
    ).toBeVisible();
  };
  try {
    await ready();
    await page.goto(ui + "/login");
    await expect(page.getByRole("link", { name: "Sign in to workspace" })).toHaveAttribute("href", "/signin-with-chatgpt?return_to=%2F");
    await expect(page.locator(".welcome-art img")).toBeVisible();
    await shot(page, "00-login");
    if (output) await page.locator(".welcome-frame").screenshot({ path: join(output, "reference-login-desktop.png") });
    await page.setViewportSize({ width: 390, height: 844 });
    await shot(page, "11-mobile-login");
    if (output) await page.locator(".welcome-frame").screenshot({ path: join(output, "reference-login-mobile.png") });
    await page.setViewportSize({ width: 1440, height: 960 });
    await page.goto(ui);
    await expect(
      page.getByText("AI activity over time", { exact: true }),
    ).toBeVisible();
    await expect(page).toHaveTitle(/AIRON Native/);
    const brand = page.getByRole("img", { name: "SYNTRIASS Labs · AIRON Native" }).first();
    await expect(brand).toBeVisible();
    await expect.poll(() => brand.locator("img").evaluateAll((images) =>
      images.every((img) => (img as HTMLImageElement).naturalWidth > 0) && images.length === 2,
    )).toBe(true);
    await expect(page.locator(".nav-children [aria-current]").first()).toHaveCSS(
      "background-image", /linear-gradient/,
    );
    await shot(page, "01-dashboard");
    await page
      .getByRole("link", { name: "Knowledge Vault", exact: true })
      .click();
    await pair(page, "Mira");
    await page
      .getByRole("button", { name: "Import fictional maintenance document" })
      .click();
    await expect(
      page.getByText("Maintenance document imported."),
    ).toBeVisible();
    await page
      .getByLabel("Text or Markdown file")
      .setInputFiles({
        name: "fixture.md",
        mimeType: "text/markdown",
        buffer: Buffer.from("North bay uses the fictional register NB-3."),
      });
    await page
      .getByLabel("Question supported by this excerpt")
      .fill("Which north bay register?");
    await page.getByRole("button", { name: "Save document" }).click();
    await expect(page.getByText("Document stored locally.")).toBeVisible();
    await page.getByLabel("Search vault").fill("equipment");
    await page.getByRole("button", { name: "Search documents" }).click();
    await page
      .getByText("Equipment inspection protocol", { exact: true })
      .click();
    await shot(page, "03-knowledge-vault");
    await route(page, "private-ai-workspace", "Private AI Workspace");
    await expect(
      page.getByRole("button", { name: "Switch identity" }),
    ).toBeVisible();
    await pair(page, "Dev");
    const ask = async (p: Page, name: string) => {
      await p.getByRole("button", { name, exact: true }).click();
      await p.getByRole("button", { name: "Ask workspace" }).click();
    };
    await ask(page, "Inspection interval");
    await expect(
      page.getByText(/Inspect the cooling assembly every 200 operating hours/),
    ).toBeVisible();
    await shot(page, "04-private-workspace");
    await ask(page, "Handover register");
    await expect(
      page.getByRole("heading", { name: "Abstained" }),
    ).toBeVisible();
    await route(page, "expert-teach", "Expert Teach");
    await expect(
      page.getByRole("button", { name: "Switch identity" }),
    ).toBeVisible();
    await pair(page, "Leela");
    await page
      .getByLabel("Supported question", { exact: true })
      .fill("Which register records the cooling assembly handover?");
    await page
      .getByLabel("Proposed procedure")
      .fill(
        "Record the cooling assembly handover in the fictional shift register MH-04.",
      );
    await page
      .getByLabel("Related vault document")
      .selectOption({ label: "Equipment inspection protocol" });
    await page
      .getByLabel("Supporting evidence or reference")
      .fill(
        "Fictional maintenance addendum MH-04, section 2; witnessed by the shift lead.",
      );
    await page.getByRole("button", { name: "Submit for review" }).click();
    await expect(
      page.getByText("Submitted for independent review."),
    ).toBeVisible();
    await pair(page, "Ravi");
    await expect(
      page.getByRole("button", { name: "Approve and activate" }),
    ).toBeVisible();
    await shot(page, "05-expert-teach");
    await page.getByRole("button", { name: "Approve and activate" }).click();
    await expect(page.getByText("Approved procedure activated.")).toBeVisible();
    await stop();
    service = start();
    await ready();
    const second = await browser.newContext({
      viewport: { width: 1440, height: 960 },
    });
    try {
      const p = await second.newPage();
      await route(p, "private-ai-workspace", "Private AI Workspace");
      await pair(p, "Nila");
      await ask(p, "Handover register");
      await expect(
        p.getByText(
          "Record the cooling assembly handover in the fictional shift register MH-04.",
          { exact: true },
        ),
      ).toBeVisible();
    } finally {
      await second.close();
    }
    await route(page, "institutional-memory", "Institutional Memory");
    await pair(page, "Mira");
    await expect(page.getByText(/approved by Ravi.*1 reuse/)).toBeVisible();
    await shot(page, "06-institutional-memory");
    const download = page.waitForEvent("download");
    await page
      .getByRole("button", { name: "Export approved knowledge" })
      .click();
    const artifact = await download;
    const stream = await artifact.createReadStream();
    const chunks = [];
    for await (const chunk of stream!) chunks.push(chunk);
    const exported = JSON.parse(Buffer.concat(chunks).toString());
    expect(exported.approved[0].reviewer).toBe("Ravi");
    expect(exported.documents).toHaveLength(2);
    await route(page, "sovereign-runtime", "Sovereign Runtime");
    await page.getByRole("button", { name: "Probe local runtime" }).click();
    await expect(page.getByText("SQLite allocated size")).toBeVisible();
    await shot(page, "07-sovereign-runtime");
    await route(page, "trust-evidence", "Trust & Evidence");
    await expect(page.getByText("Knowledge exported · Mira")).toBeVisible();
    await shot(page, "08-trust-evidence");
    await route(page, "intelligence-overview", "Intelligence Overview");
    await expect(
      page.getByRole("heading", { name: "Ownership boundary" }),
    ).toBeVisible();
    const lineage = page.getByRole("list", { name: "Selected source lineage" });
    await expect(lineage.getByRole("listitem")).toHaveText(["Imported byMira", "Approved versions1", "Answers using those versions1"]);
    if (output) await page.locator(".intelligence-heading").screenshot({ path: join(output, "reference-intelligence-masthead.png") });
    if (output) await lineage.screenshot({ path: join(output, "reference-source-lineage.png") });
    await page.getByLabel("Trace a source document").selectOption({ label: "fixture.md" });
    await expect(lineage.getByRole("listitem")).toHaveText(["Imported byMira", "Approved versions0", "Answers using those versions0"]);
    await page.getByLabel("Trace a source document").selectOption({ label: "Equipment inspection protocol" });
    await shot(page, "02-intelligence-overview");
    await route(page, "agent-lineage", "Agent Lineage");
    await expect(page.locator(".vgraph-node").first()).toBeVisible();
    await shot(page, "09-agent-lineage");
    await route(page, "ai-finops", "Spending");
    await expect(
      page.getByRole("heading", { name: /^Cost allocation records/ }),
    ).toBeVisible();
    await expect(page.getByLabel("Cost dimension")).toHaveValue("Model");
    await expect(page.locator(".costchart svg")).toBeVisible();
    await shot(page, "10-ai-finops");
    await page.setViewportSize({ width: 390, height: 844 });
    await route(page, "knowledge-vault", "Knowledge Vault");
    await expect(
      page.getByText("Source documents", { exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await expect(page.locator(".crumb-mark")).toBeVisible();
    await shot(page, "12-mobile-vault");
    await page.getByRole("button", { name: "Open navigation" }).click();
    await expect(
      page.getByRole("link", { name: "Private AI Workspace", exact: true }),
    ).toBeVisible();
    await shot(page, "13-mobile-navigation");
  } finally {
    await context.close();
    await stop();
    await site.mf.dispose();
    await rm(root, { recursive: true, force: true });
  }
});
