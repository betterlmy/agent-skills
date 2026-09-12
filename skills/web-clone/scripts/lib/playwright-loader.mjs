import path from "node:path";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import { systemChromium } from "./system-browser.mjs";

// Reuse an already-installed Playwright runtime when one happens to be
// resolvable, and otherwise fall back to the zero-dependency CDP adapter below.
// This skill never installs Playwright and never downloads a browser: it only
// uses a runtime or a browser that already exists on the machine.
export function loadPlaywright() {
  const requireFromScript = createRequire(import.meta.url);
  const requireFromCwd = createRequire(path.join(process.cwd(), "noop.js"));
  const attempts = [
    () => requireFromScript("playwright"),
    () => requireFromScript("playwright-core"),
    () => requireFromCwd("playwright"),
    () => requireFromCwd("playwright-core"),
  ];
  for (const attempt of attempts) {
    try {
      return attempt();
    } catch {
      // Try next candidate.
    }
  }
  return { chromium: systemChromium };
}

function firstExisting(candidates) {
  return candidates.find((candidate) => candidate && fs.existsSync(candidate)) || null;
}

function executableFromPath(names, env = process.env, platform = process.platform) {
  const pathValue = env.PATH || env.Path || "";
  const extensions = platform === "win32"
    ? (env.PATHEXT || ".EXE;.CMD;.BAT").split(";")
    : [""];
  for (const directory of pathValue.split(path.delimiter).filter(Boolean)) {
    for (const name of names) {
      for (const extension of extensions) {
        const candidate = path.join(directory, `${name}${extension}`);
        if (fs.existsSync(candidate)) return candidate;
      }
    }
  }
  return null;
}

export function findSystemChromiumExecutable({
  platform = process.platform,
  env = process.env,
  homeDir = os.homedir(),
} = {}) {
  const configured = env.WEB_CLONE_BROWSER_PATH;
  if (configured) {
    if (fs.existsSync(configured)) return configured;
    throw new Error(`WEB_CLONE_BROWSER_PATH does not exist: ${configured}`);
  }

  if (platform === "darwin") {
    return firstExisting([
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
      "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
      "/Applications/Chromium.app/Contents/MacOS/Chromium",
      path.join(homeDir, "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
      path.join(homeDir, "Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]);
  }

  if (platform === "win32") {
    const roots = [env.PROGRAMFILES, env["PROGRAMFILES(X86)"], env.LOCALAPPDATA].filter(Boolean);
    return firstExisting(roots.flatMap((root) => [
      path.join(root, "Google/Chrome/Application/chrome.exe"),
      path.join(root, "Microsoft/Edge/Application/msedge.exe"),
      path.join(root, "Chromium/Application/chrome.exe"),
    ]));
  }

  return executableFromPath([
    "google-chrome-stable",
    "google-chrome",
    "microsoft-edge-stable",
    "microsoft-edge",
    "chromium",
    "chromium-browser",
  ], env, platform);
}

export async function launchChromium(chromium, options = {}) {
  const executablePath = findSystemChromiumExecutable(options.discovery);
  let systemBrowserError = null;
  if (executablePath) {
    try {
      return await chromium.launch({ headless: true, executablePath });
    } catch (error) {
      systemBrowserError = error;
    }
  }

  // Source checkouts may already have a Playwright-managed browser. Trying it
  // is safe: launch never downloads a browser; it only uses an existing one.
  try {
    return await chromium.launch({ headless: true });
  } catch (error) {
    throw new Error(
      "No compatible Chrome, Edge, or Chromium executable is available. " +
        "web-clone never downloads a browser. " +
        "Install a system browser or set WEB_CLONE_BROWSER_PATH to its executable. " +
        `Browser launch detail: ${systemBrowserError?.message || error.message}`,
    );
  }
}
