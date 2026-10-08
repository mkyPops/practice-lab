/**
 * Playwright visual regression helper.
 *
 * Wraps page/element screenshot capture with pixel-level comparison against
 * a stored baseline image. Supports configurable pixel-match thresholds and,
 * on failure, writes an annotated diff image (mismatched pixels highlighted)
 * plus attaches actual/expected/diff images to the Playwright test report.
 */

import { Page, TestInfo } from "@playwright/test";
import { PNG } from "pngjs";
import pixelmatch from "pixelmatch";
import * as fs from "fs";
import * as path from "path";

export interface VisualDiffOptions {
  /** Per-pixel color sensitivity (0-1), passed to pixelmatch. Default 0.1 */
  threshold?: number;
  /** Max allowed ratio of differing pixels to total pixels before failing. Default 0.01 (1%) */
  maxDiffRatio?: number;
  /** Color used to highlight mismatched pixels in the diff image. */
  diffColor?: [number, number, number];
}

const BASELINE_DIR = "__visual_baselines__";

export async function expectScreenshotMatches(
  page: Page,
  name: string,
  testInfo: TestInfo,
  options: VisualDiffOptions = {}
): Promise<void> {
  const { threshold = 0.1, maxDiffRatio = 0.01, diffColor = [255, 0, 0] } = options;

  const baselineDir = path.join(testInfo.project.testDir, BASELINE_DIR);
  fs.mkdirSync(baselineDir, { recursive: true });
  const baselinePath = path.join(baselineDir, `${name}.png`);

  const actualBuffer = await page.screenshot();
  const actualPng = PNG.sync.read(actualBuffer);

  // First run for this test: establish the baseline and pass trivially.
  if (!fs.existsSync(baselinePath)) {
    fs.writeFileSync(baselinePath, actualBuffer);
    return;
  }

  const expectedPng = PNG.sync.read(fs.readFileSync(baselinePath));
  if (expectedPng.width !== actualPng.width || expectedPng.height !== actualPng.height) {
    throw new Error(
      `Screenshot "${name}" size mismatch: expected ${expectedPng.width}x${expectedPng.height}, ` +
        `got ${actualPng.width}x${actualPng.height}. Delete baseline to regenerate.`
    );
  }

  const { width, height } = actualPng;
  const diffPng = new PNG({ width, height });
