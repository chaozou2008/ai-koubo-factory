import client from "./client";

export function login(phone: string, password: string) {
  return client.post("/api/auth/login", { phone, password });
}

export function register(phone: string, password: string, company_name?: string) {
  return client.post("/api/auth/register", { phone, password, company_name });
}
