/**
 * A typed wrapper around Playwright's APIRequestContext for REST API testing.
 * Provides generic request helpers that return parsed JSON bodies and a set
 * of assertion helpers for validating HTTP responses concisely in tests.
 */

import { APIRequestContext, APIResponse, expect } from '@playwright/test';

export interface ApiResult<T> {
  status: number;
  headers: Record<string, string>;
  body: T;
  raw: APIResponse;
}

export interface RequestOptions {
  headers?: Record<string, string>;
  params?: Record<string, string | number | boolean>;
  data?: unknown;
}

export class ApiClient {
  constructor(
    private readonly request: APIRequestContext,
    private readonly baseUrl: string = '',
  ) {}

  async get<T = unknown>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('GET', path, options);
  }

  async post<T = unknown>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('POST', path, options);
  }

  async put<T = unknown>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('PUT', path, options);
  }

  async patch<T = unknown>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('PATCH', path, options);
  }

  async delete<T = unknown>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    return this.send<T>('DELETE', path, options);
  }

  private async send<T>(
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    path: string,
    options: RequestOptions,
  ): Promise<ApiResult<T>> {
    const url = `${this.baseUrl}${path}`;
    const raw = await this.request.fetch(url, {
      method,
      headers: options.headers,
      params: options.params,
      data: options.data,
    });

    // Attempt JSON parsing but fall back to text for non-JSON payloads.
    let body: T;
    try {
      body = (await raw.json()) as T;
    } catch {
      body = (await raw.text()) as unknown as T;
    }

    return { status: raw.status(), headers: raw.headers(), body, raw };
  }

  // --- Validation helpers -------------------------------------------------

  expectStatus<T>(result: ApiResult<T>, expected: number): ApiResult<T> {
    expect(result.status, `Expected status ${expected} but got ${result.status}`).toBe(expected);
    return result;
  }

  expectOk<T>(result: ApiResult<T>): ApiResult<T> {
    expect(result.raw.ok(), `Expected OK response but got ${result.status}`).toBeTruthy();
    return result;
  }

  expectHeader<T>(result: ApiResult<T>, name: string, value: string): ApiResult<T> {
    expect(result.headers[name.toLowerCase()]).toBe(value);
    return result;
  }

  expectBodyContains<T extends Record<string, unknown>>(
    result: ApiResult<T>,
    subset: Partial<T>,
  ): ApiResult<T> {
    expect(result.body).toMatchObject(subset);
    return result;
  }
}
