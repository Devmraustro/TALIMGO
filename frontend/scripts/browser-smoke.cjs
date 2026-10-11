"use strict";

const assert = require("node:assert/strict");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || "playwright");

const baseURL = process.env.TALIMGO_BROWSER_BASE_URL || "http://127.0.0.1:5173";
const origin = new URL(baseURL);

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
  const pageErrors = [];
  const externalRequests = [];
  const serverErrors = [];

  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.hostname !== origin.hostname || url.port !== origin.port) {
      externalRequests.push(url.href);
    }
  });
  page.on("response", (response) => {
    const url = new URL(response.url());
    if (url.pathname.startsWith("/api/") && response.status() >= 500) {
      serverErrors.push(`${response.status()} ${url.pathname}`);
    }
  });

  try {
    await page.goto(baseURL, { waitUntil: "networkidle" });
    await page.getByRole("heading", { name: "Create your account", exact: true }).waitFor();

    const email = `talimgo-browser-${Date.now()}@example.com`;
    const password = "TALIMGO-Browser-smoke-2026!";
    await page.getByLabel("Email", { exact: true }).fill(email);
    await page.getByLabel("Password", { exact: true }).fill(password);
    await page.getByLabel("What should we call you?", { exact: true }).fill("Browser Smoke");
    await page.getByLabel("I accept the terms of use and the privacy notice.", { exact: true }).check();

    await page.getByRole("button", { name: "Create account", exact: true }).click();
    await page.getByRole("heading", { name: "What do you want to be able to do?", exact: true }).waitFor();

    await page.getByLabel("Your goal, in your own words", { exact: true }).fill(
      "Learn Python programming and build practical projects",
    );
    await page.getByRole("button", { name: "Set this goal", exact: true }).click();
    await page.getByRole("heading", { name: "Starting check", exact: true }).waitFor();

    const radios = page.getByRole("radio");
    if ((await radios.count()) > 0) {
      await radios.first().check();
    } else {
      await page.getByLabel("Your answer", { exact: true }).fill("I am still learning");
    }

    const answerResponsePromise = page.waitForResponse((response) => {
      const url = new URL(response.url());
      return (
        response.request().method() === "POST" &&
        url.pathname.startsWith("/api/diagnostic/") &&
        url.pathname.endsWith("/answers")
      );
    });
    await page.getByRole("button", { name: "Check my answer", exact: true }).click();
    const answerResponse = await answerResponsePromise;
    assert.equal(answerResponse.status(), 200, "first diagnostic answer should be accepted by the API");

    await page.getByRole("button", { name: "Settings", exact: true }).click();
    await page.getByRole("heading", { name: "Settings and your data", exact: true }).waitFor();
    await page.getByLabel("Interface language", { exact: true }).selectOption("ar");
    await page.waitForFunction(
      () => document.documentElement.lang === "ar" && document.documentElement.dir === "rtl",
    );
    await page.getByRole("heading", { name: "الإعدادات وبياناتك", exact: true }).waitFor();

    await page.setViewportSize({ width: 390, height: 844 });
    const horizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    assert.equal(horizontalOverflow, false, "Arabic mobile layout must not overflow horizontally");

    await page.getByLabel("كلمة المرور", { exact: true }).fill(password);
    await page.getByRole("button", { name: "احذف حسابي", exact: true }).click();
    await page.getByRole("heading", { name: "أنشئ حسابك", exact: true }).waitFor();
    const postDeleteSessionStatus = await page.evaluate(async () => {
      const response = await fetch("/api/auth/me", { credentials: "same-origin" });
      return response.status;
    });
    assert.equal(postDeleteSessionStatus, 401, "deleted account session must no longer authenticate");

    assert.deepEqual(pageErrors, [], "the browser page must not throw uncaught JavaScript errors");
    assert.deepEqual(serverErrors, [], "the real API must not return 5xx errors during the journey");
    assert.deepEqual(
      externalRequests,
      [],
      "browser network requests must stay on the local TALIMGO origin",
    );

    console.log(
      "Browser smoke passed: registration, goal, real diagnostic answer, Arabic RTL, mobile reflow, deletion, " +
        "and same-origin requests.",
    );
  } catch (error) {
    try {
      await page.screenshot({ path: "/tmp/talimgo-browser-smoke-failure.png", fullPage: true });
    } catch {
      // A screenshot is diagnostic only; preserve the original failure.
    }
    throw error;
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
