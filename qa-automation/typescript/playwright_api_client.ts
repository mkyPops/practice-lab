// A typed wrapper around Playwright's APIRequestContext that provides
// convenient REST helpers (get/post/put/patch/delete) with generic JSON
// typing and built-in response validation utilities for API testing.

import { APIRequestContext, APIResponse, expect } from '@playwright/test';

export interface ApiOptions {
  headers?: Record<string, string>;
  params?: Record<string, string | number | boolean>;
  data?: unknown;
}

export interface ApiResult<T> {
  response: APIResponse;
  status: number;
  body: T;
}

export class ApiClient {
  constructor(
    private readonly request: APIRequestContext,
    private readonly baseHeaders: Record<string, string> = { 'Content-Type': 'application/json' },
  ) {}

  async get<T = unknown>(url: string, options: ApiOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('GET', url, options);
  }

  async post<T = unknown>(url: string, options: ApiOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('POST', url, options);
  }

  async put<T = unknown>(url: string, options: ApiOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('PUT', url, options);
  }

  async patch<T = unknown>(url: string, options: ApiOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('PATCH', url, options);
  }

  async delete<T = unknown>(url: string, options: ApiOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('DELETE', url, options);
  }

  private async send<T>(
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    url: string,
    options: ApiOptions,
  ): Promise<ApiResult<T>> {
    const response = await this.request.fetch(url, {
      method,
      headers: { ...this.baseHeaders, ...options.headers },
      params: options.params,
      data: options.data,
    });

    // Gracefully fall back to raw text if the body isn't valid JSON.
    let body: T;
    try {
      body = (await response.json()) as T;
    } catch {
      body = (await response.text()) as unknown as T;
    }

    return { response, status: response.status(), body };
  }

  /** Asserts the response status equals the expected code. */
  expectStatus<T>(result: ApiResult<T>, expected: number): void {
    expect(result.status, `Expected status ${expected} but got ${result.status}`).toBe(expected);
  }

  /** Asserts that every provided key exists on the response body (shallow shape check). */
  expectBodyToContainKeys<T extends object>(result: ApiResult<T>, keys: Array<keyof T>): void {
    for (const key of keys) {
      expect(result.body, `Missing key "${String(key)}" in response body`).toHaveProperty(String(key));
    }
  }

  /** Asserts a response header matches the expected value. */
  expectHeader<T>(result: ApiResult<T>, name: string, value: string): void {
    const actual = result.response.headers()[name.toLowerCase()];
    expect(actual, `Expected header "${name}" to be "${value}" but got "${actual}"`).toBe(value);
  }
}
