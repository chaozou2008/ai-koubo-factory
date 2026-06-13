import client from "./client";
export function getCreditLog() { return client.get("/api/credits/log"); }
