import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import Home from "../app/page";


const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const destination = resolve(root, "site");
const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL ?? "").replace(/\/$/, "");
const ogImage = siteUrl ? `${siteUrl}/og.png` : "./og.png";

await rm(destination, { recursive: true, force: true });
await mkdir(resolve(destination, "data"), { recursive: true });

const body = renderToStaticMarkup(React.createElement(Home));
const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="A small learning demo for structured log analysis, baseline comparison, and rule-based alerts." />
    <meta property="og:title" content="SignalOps | AIOps Log Intelligence" />
    <meta property="og:description" content="A learning demo using synthetic logs, static baselines, and readable detection rules." />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="${ogImage}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="SignalOps | AIOps Log Intelligence" />
    <meta name="twitter:description" content="A learning demo using synthetic logs, static baselines, and readable detection rules." />
    <meta name="twitter:image" content="${ogImage}" />
    <title>SignalOps | AIOps Log Intelligence</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>${body}</body>
</html>
`;

await writeFile(resolve(destination, "index.html"), html, "utf8");
await writeFile(resolve(destination, ".nojekyll"), "", "utf8");
await writeFile(
  resolve(destination, "styles.css"),
  await readFile(resolve(root, "app/globals.css"), "utf8"),
  "utf8",
);
await cp(resolve(root, "public/og.png"), resolve(destination, "og.png"));
await cp(
  resolve(root, "public/data/report.json"),
  resolve(destination, "data/report.json"),
);

console.log(`GitHub Pages artifact created at ${destination}`);
