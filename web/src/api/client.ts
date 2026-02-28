export class HttpException extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "HttpException";
    this.status = status;
  }
}

import { getServerBaseUrl } from "@/env";

const BASE_URL = getServerBaseUrl();

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const text = await response.text().catch(() => "Unknown error");
    throw new HttpException(response.status, text);
  }
  return response.json() as Promise<T>;
};

export const get = async <T>(path: string, params?: Record<string, string>): Promise<T> => {
  const url = new URL(`${BASE_URL}${path}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  }
  const response = await fetch(url.toString());
  return handleResponse<T>(response);
};

export const post = async <T>(path: string, body?: unknown): Promise<T> => {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body != null ? JSON.stringify(body) : undefined,
  });
  return handleResponse<T>(response);
};

export const put = async <T>(path: string, body: unknown): Promise<T> => {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(response);
};

export const del = async <T>(path: string): Promise<T> => {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "DELETE",
  });
  return handleResponse<T>(response);
};

export const postBlob = async (path: string, body?: unknown): Promise<Blob> => {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body != null ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const text = await response.text().catch(() => "Unknown error");
    throw new HttpException(response.status, text);
  }
  return response.blob();
};

export const postFormData = async <T>(path: string, formData: FormData): Promise<T> => {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<T>(response);
};
