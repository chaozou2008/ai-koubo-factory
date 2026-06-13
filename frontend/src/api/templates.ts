import client from "./client";

export function getTemplates(industry?: string) {
  return client.get("/api/templates", { params: { industry } });
}
