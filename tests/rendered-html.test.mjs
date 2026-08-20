import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

test("exports the SignalOps portfolio", async () => {
  const html = await readFile(new URL("site/index.html", root), "utf8");
  assert.match(html, /<title>SignalOps \| AIOps Log Intelligence<\/title>/i);
  assert.match(html, /Turn noisy logs into/);
  assert.match(html, /Operational overview/);
  assert.match(html, /Explainable by design/);
  assert.match(html, /De Huo/);
});

test("ships generated operational data and social metadata", async () => {
  const [report, layout] = await Promise.all([
    readFile(new URL("public/data/report.json", root), "utf8"),
    readFile(new URL("app/layout.tsx", root), "utf8"),
  ]);
  assert.match(report, /"incidents_opened": 1/);
  assert.match(report, /"error_rate_spike"/);
  assert.match(layout, /\/og\.png/);
  assert.match(layout, /summary_large_image/);
});
