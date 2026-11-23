import { readFile } from "node:fs/promises";
import { test } from "node:test";
import assert from "node:assert/strict";
import { tsImport } from "tsx/esm/api";
const { pages, sections } = await tsImport(
  "../src/navigation.ts",
  import.meta.url,
);
const baseline = JSON.parse(
  await readFile(
    new URL("../../../docs/CIIC_NAVIGATION_BASELINE.json", import.meta.url),
    "utf8",
  ),
);
const shell = await readFile(
  new URL("../src/ui/Console.tsx", import.meta.url),
  "utf8",
);
test("preserve all 46 baseline routes, section order, icons and contracts", () => {
  assert.deepEqual(
    sections.slice(1),
    baseline.groups.map((g) => g.section),
  );
  for (const { section, icon, routes } of baseline.groups) {
    assert.ok(
      shell.includes(section + ': "' + icon + '"') ||
        shell.includes('"' + section + '": "' + icon + '"'),
    );
    assert.deepEqual(
      pages
        .filter((p) => p.section === section)
        .map(({ slug, title, icon, api }) => ({
          slug,
          title,
          icon,
          api,
          path: "/" + slug,
        })),
      routes,
    );
  }
});
test("exactly seven ordered, unique enterprise intelligence destinations", () => {
  assert.equal(sections[0], "Enterprise Intelligence");
  assert.deepEqual(
    pages.filter((p) => p.section === sections[0]).map((p) => p.title),
    [
      "Intelligence Overview",
      "Knowledge Vault",
      "Private AI Workspace",
      "Expert Teach",
      "Institutional Memory",
      "Sovereign Runtime",
      "Trust & Evidence",
    ],
  );
  assert.equal(new Set(pages.map((p) => p.slug)).size, 53);
});
