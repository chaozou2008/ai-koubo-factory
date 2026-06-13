import client from "./client";
export function getPlans() { return client.get("/api/plans"); }
