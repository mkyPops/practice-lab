/**
 * Generic async retry utility with configurable attempts, exponential backoff,
 * jitter, and an abort condition to stop retrying early on certain errors.
 */

export interface RetryOptions {
  /** Maximum number of attempts (including the first), default 3. */
  attempts?: number;
  /** Base delay in milliseconds before the first retry, default 100. */
  baseDelayMs?: number;
  /** Maximum delay cap in milliseconds, default 10000. */
  maxDelayMs?: number;
  /** Multiplier applied to the delay after each attempt, default 2. */
  factor?: number;
  /** Jitter ratio (0-1) applied randomly to the computed delay, default 0.5. */
  jitter?: number;
  /** Return true to abort retrying immediately (e.g. non-retryable errors). */
  shouldAbort?: (error: unknown) => boolean;
  /** Called after each failed attempt, useful for logging/metrics. */
  onRetry?: (error: unknown, attempt: number, delayMs: number) => void;
}

const sleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Executes `fn` and retries on failure using exponential backoff with jitter.
 * Rejects with the last error if all attempts are exhausted or `shouldAbort`
 * signals that retrying should stop.
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<T> {
  const {
    attempts = 3,
    baseDelayMs = 100,
    maxDelayMs = 10_000,
    factor = 2,
    jitter = 0.5,
    shouldAbort,
    onRetry,
  } = options;

  let lastError: unknown;

  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;

      const isLastAttempt = attempt === attempts;
      if (isLastAttempt || shouldAbort?.(err)) {
        throw err;
      }

      // Exponential backoff: baseDelay * factor^(attempt-1), capped at maxDelayMs.
      const exponential = baseDelayMs * factor ** (attempt - 1);
      const capped = Math.min(exponential, maxDelayMs);

      // Full jitter: randomize within [capped * (1 - jitter), capped].
      const jitterFloor = capped * (1 - jitter);
      const delayMs = jitterFloor + Math.random() * (capped - jitterFloor);

      onRetry?.(err, attempt, delayMs);
      await sleep(delayMs);
    }
  }

  // Unreachable, but keeps TypeScript's control-flow analysis satisfied.
  throw lastError;
}
