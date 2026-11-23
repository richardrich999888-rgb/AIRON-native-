import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
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
  const service = start();
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
    if (/^0[2-8]-/.test(name) || name === "12-mobile-vault") {
      await expect(p.locator(".intel-strip")).toContainText(
        "Local knowledge workspace",
      );
      await expect(p.locator("body")).not.toContainText(/\bCIIC\b/i);
    }
    if (
      name.includes("login") ||
      /^0[2-8]-/.test(name) ||
      name === "12-mobile-vault"
    ) {
      const scan = await new AxeBuilder({ page: p })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .analyze();
      expect
        .soft(
          scan.violations
            .filter((v) => v.impact === "serious" || v.impact === "critical")
            .map((v) => [v.id, v.nodes.map((n) => n.target)]),
          name,
        )
        .toEqual([]);
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
    await p.getByLabel("Sample workspace profile").selectOption(actor);
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
    await expect(
      page.getByRole("link", { name: "Sign in to workspace" }),
    ).toHaveAttribute("href", "/signin-with-chatgpt?return_to=%2F");
    await expect(page.locator(".welcome-art img")).toBeVisible();
    await expect(page.locator('link[rel="manifest"]')).toHaveAttribute(
      "href",
      "/manifest.webmanifest",
    );
    await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute(
      "href",
      "/brand/icon-180.png",
    );
    const manifest = await (
      await page.request.get(ui + "/manifest.webmanifest")
    ).json();
    expect(manifest.icons.map((icon: { sizes: string }) => icon.sizes)).toEqual(
      ["192x192", "512x512"],
    );
    for (const icon of manifest.icons) {
      const dimensions = await page.evaluate(async (src: string) => {
        const image = new Image();
        image.src = src;
        await image.decode();
        return [image.naturalWidth, image.naturalHeight].join("x");
      }, icon.src);
      expect(dimensions).toBe(icon.sizes);
    }
    await shot(page, "00-login");
    await expect(page.locator(".welcome-frame")).toHaveScreenshot(
      "login-desktop.png",
    );
    await page.setViewportSize({ width: 390, height: 844 });
    await shot(page, "11-mobile-login");
    await expect(page.locator(".welcome-frame")).toHaveScreenshot(
      "login-mobile.png",
    );
    await page.setViewportSize({ width: 1440, height: 960 });
    await page.goto(ui);
    await expect(
      page.getByText("AI activity over time", { exact: true }),
    ).toBeVisible();
    await expect(page).toHaveTitle(/AIRON Native/);
    const brand = page
      .getByRole("img", { name: "SYNTRIASS Labs · AIRON Native" })
      .first();
    await expect(brand).toBeVisible();
    await expect
      .poll(() =>
        brand
          .locator("img")
          .evaluateAll(
            (images) =>
              images.every(
                (img) => (img as HTMLImageElement).naturalWidth > 0,
              ) && images.length === 2,
          ),
      )
      .toBe(true);
    await expect(
      page.locator(".nav-children [aria-current]").first(),
    ).toHaveCSS("background-image", /linear-gradient/);
    await shot(page, "01-dashboard");
    await page
      .getByRole("link", { name: "Knowledge Vault", exact: true })
      .click();
    await pair(page, "Mira");
    await page
      .getByRole("button", { name: "Import sample maintenance document" })
      .click();
    await expect(
      page.getByText("Maintenance document imported."),
    ).toBeVisible();
    await page.getByLabel("TXT, Markdown or PDF file").setInputFiles({
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
      page.locator(".intelligence-card p").filter({
        hasText: /Inspect the cooling assembly every 200 operating hours/,
      }),
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
    await route(page, "sovereign-runtime", "Sovereign Runtime");
    await pair(page, "Mira");
    await page
      .getByRole("button", { name: "Restart local repository" })
      .click();
    await expect(
      page.getByText(
        "Repository restarted. Open the workspace to inspect persisted records.",
      ),
    ).toBeVisible({ timeout: 20000 });
    const second = await browser.newContext({
      viewport: { width: 1440, height: 960 },
    });
    try {
      const p = await second.newPage();
      await route(p, "private-ai-workspace", "Private AI Workspace");
      await pair(p, "Nila");
      await ask(p, "Handover register");
      await expect(
        p.locator(".intelligence-card p").filter({
          hasText:
            "Record the cooling assembly handover in the fictional shift register MH-04.",
        }),
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
    await expect(lineage.getByRole("listitem")).toHaveText([
      "Imported byMira",
      "Approved versions1",
      "Answers using those versions1",
    ]);
    await expect(page.locator(".intelligence-heading")).toHaveScreenshot(
      "intelligence-masthead.png",
    );
    await expect(lineage).toHaveScreenshot("source-lineage.png");
    await page
      .getByLabel("Trace a source document")
      .selectOption({ label: "fixture.md" });
    await expect(lineage.getByRole("listitem")).toHaveText([
      "Imported byMira",
      "Approved versions0",
      "Answers using those versions0",
    ]);
    await page
      .getByLabel("Trace a source document")
      .selectOption({ label: "Equipment inspection protocol" });
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
    // A real, two-page PDF has no registered question. Retrieval must find page two.
    await route(page, "knowledge-vault", "Knowledge Vault");
    const overview = await context.newPage();
    await route(overview, "intelligence-overview", "Intelligence Overview");
    await pair(overview, "Mira");
    const sourceCount = overview.getByRole("button", {
      name: /Source documents/,
    });
    await expect(sourceCount).toContainText("2");
    await page
      .getByLabel("TXT, Markdown or PDF file")
      .setInputFiles("tests/fixtures/workshop-note.pdf");
    await page.getByRole("button", { name: "Save document" }).click();
    await expect(page.getByText("Document stored locally.")).toBeVisible();
    await expect(sourceCount).toContainText("3");
    await overview.close();
    await page.getByText("workshop-note.pdf", { exact: true }).click();
    await expect(page.getByText(/Indexed · PDF · 2 chunk/)).toBeVisible();
    await shot(page, "14-pdf-ingestion");
    await route(page, "private-ai-workspace", "Private AI Workspace");
    await page
      .getByLabel("Technical question")
      .fill("What is the amber spindle interval?");
    await page.getByRole("button", { name: "Ask workspace" }).click();
    await expect(page.getByText("Page 2 · Chunk 2")).toBeVisible();
    await page.getByText("Inspect cited passage").click();
    await expect(page.locator("blockquote")).toHaveText(
      "The amber spindle interval is 72 hours.",
    );
    await shot(page, "15-pdf-citation");
    if (process.env.AIRON_TEST_MODEL) {
      const model = process.env.AIRON_TEST_MODEL;
      await page.getByLabel("Answer engine").selectOption("ollama");
      await page
        .getByLabel("Installed local model")
        .selectOption(model, { timeout: 30000 });
      const response = page.waitForResponse(
        (r) =>
          r.url().endsWith("/knowledge/ask") && r.request().method() === "POST",
        { timeout: 100000 },
      );
      await page.getByRole("button", { name: "Ask workspace" }).click();
      const payload = await (await response).json();
      expect(payload.outcome).toBe("Answered");
      expect(payload.model).toBe(model);
      expect(payload.usage.inputTokens).toBeGreaterThan(0);
      expect(payload.usage.outputTokens).toBeGreaterThan(0);
      expect(payload.usage.durationMs).toBeGreaterThan(0);
      await expect(
        page.getByText(/Ollama · source-constrained generation/),
      ).toBeVisible();
      await shot(page, "16-ollama-answer");
      if (output)
        await writeFile(
          join(output, "measured-inference.json"),
          JSON.stringify(payload, null, 2),
        );
    }
    // Rehearse the presenter's PDF through every knowledge ownership stage.
    const handover = "Which register records the spindle handover?";
    const procedure = "Record the spindle handover in register MH-04.";
    const askTyped = async (question: string) => {
      await page.getByLabel("Technical question").fill(question);
      await page.getByRole("button", { name: "Ask workspace" }).click();
    };
    await pair(page, "Dev");
    await askTyped(handover);
    await expect(
      page.getByRole("heading", { name: "Abstained" }),
    ).toBeVisible();
    await route(page, "expert-teach", "Expert Teach");
    await pair(page, "Leela");
    await page.getByLabel("Supported question", { exact: true }).fill(handover);
    await page.getByLabel("Proposed procedure").fill(procedure);
    await page
      .getByLabel("Related vault document")
      .selectOption({ label: "workshop-note.pdf" });
    await page
      .getByLabel("Supporting evidence or reference")
      .fill("Workshop shift addendum, section 2, supplied by the shift lead.");
    await page.getByRole("button", { name: "Submit for review" }).click();
    await expect(
      page.getByText("Submitted for independent review."),
    ).toBeVisible();
    await pair(page, "Ravi");
    await page.getByRole("button", { name: "Approve and activate" }).click();
    await expect(page.getByText("Approved procedure activated.")).toBeVisible();
    await route(page, "private-ai-workspace", "Private AI Workspace");
    await pair(page, "Nila");
    await askTyped(handover);
    await expect(
      page.locator(".intelligence-card p").filter({ hasText: procedure }),
    ).toBeVisible();
    await route(page, "institutional-memory", "Institutional Memory");
    await pair(page, "Mira");
    const version = page.locator("details").filter({ hasText: handover });
    await expect(version).toContainText("approved by Ravi");
    await expect(version).toContainText("1 reuse");
    const exportFile = page.waitForEvent("download");
    await page
      .getByRole("button", { name: "Export approved knowledge" })
      .click();
    const exportedFile = await exportFile;
    const fileStream = await exportedFile.createReadStream();
    const pieces = [];
    for await (const piece of fileStream!) pieces.push(piece);
    const records = JSON.parse(Buffer.concat(pieces).toString());
    const savedVersion = records.approved.find(
      (item: { question: string }) => item.question === handover,
    );
    expect(savedVersion).toMatchObject({
      actor: "Leela",
      reviewer: "Ravi",
      source: "workshop-note.pdf",
      version: 1,
      reuse: 1,
    });
    await route(page, "trust-evidence", "Trust & Evidence");
    const approval = page
      .locator("details")
      .filter({ hasText: "Correction approved · Ravi" })
      .first();
    await approval.locator("summary").click();
    await expect(approval.locator("code")).toContainText(
      '"teaching": ' + savedVersion.id,
    );
    await shot(page, "21-pdf-approval");
    await route(page, "verification", "Verification");
    await page
      .getByRole("button", { name: "Local Runtime", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Run archive verification" })
      .click();
    await expect(
      page.getByText("CannotProve · ActionEvidenceUnavailable"),
    ).toBeVisible();
    await shot(page, "17-tool-verification");
    for (const [slug, title] of [
      ["ai-agents", "AI Agents"],
      ["agent-lineage", "Agent Lineage"],
      ["agent-inventory", "Agent Inventory"],
      ["evidence-audit", "Execution Evidence"],
    ]) {
      await route(page, slug, title);
      await page
        .getByRole("button", { name: "Local Runtime", exact: true })
        .click();
      await expect(
        page.getByText("CannotProve · ActionEvidenceUnavailable"),
      ).toBeVisible();
    }
    for (const [slug, title] of [
      ["runtime-activity", "Runtime Activity"],
      ["conversations", "Conversation Explorer"],
      ["token-usage", "Token Usage"],
      ["ai-finops", "Spending"],
    ]) {
      await route(page, slug, title);
      await page
        .getByRole("button", { name: "Local Runtime", exact: true })
        .click();
      const panel = page.getByRole("region", {
        name: "Local Runtime measurements",
      });
      await expect(panel.getByText(/Local Runtime · Workspace/)).toBeVisible();
      if (slug === "runtime-activity") {
        await expect(
          panel.getByText(/tool.verify_archive · Completed/),
        ).toBeVisible();
        await shot(page, "18-local-runtime");
      } else if (slug === "conversations") {
        await expect(
          panel.getByText(/workspace.ask · Answered/).first(),
        ).toBeVisible();
      } else if (process.env.AIRON_TEST_MODEL) {
        await expect(
          panel.getByText(/model.inference · Completed/),
        ).toBeVisible();
        await shot(
          page,
          slug === "ai-finops" ? "20-local-spending" : "19-local-tokens",
        );
      } else {
        await expect(
          panel.getByText("No matching local activity yet."),
        ).toBeVisible();
      }
    }
    await route(page, "sovereign-runtime", "Sovereign Runtime");
    await page
      .getByRole("button", { name: "Restart local repository" })
      .click();
    await expect(
      page.getByText(
        "Repository restarted. Open the workspace to inspect persisted records.",
      ),
    ).toBeVisible({ timeout: 20000 });
    await pair(page, "Mira");
    await route(page, "institutional-memory", "Institutional Memory");
    await expect(
      page.locator("details").filter({ hasText: handover }),
    ).toContainText(procedure);
    await shot(page, "22-pdf-memory-after-restart");
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
