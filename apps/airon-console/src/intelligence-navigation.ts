import type { PageDef } from "./types";

export const intelligenceGroup = "Enterprise Intelligence";
const entries = [
  [
    "intelligence-overview",
    "Intelligence Overview",
    "boxes",
    "Review the knowledge, people and approved procedures in your local workspace.",
  ],
  [
    "knowledge-vault",
    "Knowledge Vault",
    "database",
    "Import maintenance records and search the documents under your control.",
  ],
  [
    "private-ai-workspace",
    "Private AI Workspace",
    "message",
    "Ask a question and inspect the exact source behind the answer.",
  ],
  [
    "expert-teach",
    "Expert Teach",
    "guide",
    "Submit a documented correction or review a pending procedure.",
  ],
  [
    "institutional-memory",
    "Institutional Memory",
    "bookmarked",
    "Inspect approved versions, their authors and how often they have been reused.",
  ],
  [
    "sovereign-runtime",
    "Sovereign Runtime",
    "cpu",
    "Inspect the local repository and probe the configured inference runtime.",
  ],
  [
    "trust-evidence",
    "Trust & Evidence",
    "signed",
    "Trace a decision to its source, author and reviewer.",
  ],
];
export const intelligencePages: PageDef[] = entries.map(
  ([slug, title, icon, description]) => ({
    section: intelligenceGroup,
    slug,
    title,
    icon,
    description,
    api: "knowledge/" + slug,
    columns: [],
    filters: [],
  }),
);
