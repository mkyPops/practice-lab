/**
 * Generic async retry utility with exponential backoff, optional jitter,
 * and a configurable abort condition. Useful for retrying flaky I/O
 * operations (network calls, DB queries, etc.) without hammering the
 * downstream service.
 */

export interface RetryOptions {
  /** Maximum number of attempts (including the first one). */
  attempts: number;
  /** Base delay in milliseconds for the first retry. */
  baseDelayMs: number;
  /** Upper bound on the computed delay, regardless of attempt count. */
  maxDelayMs: number;
  /** Apply "full jitter" to the computed delay (default: true). */
  jitter?: boolean;
  /** If this returns true for a given error, retrying stops immediately. */
  shouldAbort?: (error: unknown) => boolean;
  /** Optional hook invoked before each retry, useful for logging/metrics. */
  onRetry?: (error: unknown, attempt: number, delayMs: number) => void;
}

const sleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Runs `fn`, retrying on failure according to `options`. `fn` receives the
 * current attempt number (1-based) in case it wants to adjust behavior.
 * Rethrows the last error once attempts are exhausted or abort is triggered.
 */
export async function retry<T>(
  fn: (attempt: number) => Promise<T>,
  options: RetryOptions,
): Promise<T> {
  const { attempts, baseDelayMs, maxDelayMs, jitter = true, shouldAbort, onRetry } = options;

  if (attempts < 1) {
    throw new RangeError("attempts must be at least 1");
  }

  let lastError: unknown;

  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      return await fn(attempt);
    } catch (error) {
      lastError = error;

      const isLastAttempt = attempt === attempts;
      if (isLastAttempt || shouldAbort?.(error)) {
        throw error;
      }

      // Exponential backoff, capped at maxDelayMs.
      const exponentialDelay = Math.min(maxDelayMs, baseDelayMs * 2 ** (attempt - 1));
      // Full jitter: uniformly random delay between 0 and exponentialDelay.
      const delayMs = jitter ? Math.random() * exponentialDelay : exponentialDelay;

      onRetry?.(error, attempt, delayMs);
      await sleep(delayMs);
    }
  }

  // Unreachable, but keeps TypeScript happy about the return type.
  throw lastError;
}
