import client from "./client";

export function publishVideo(taskId: string, platform: string, title?: string, description?: string) {
  return client.post("/api/publish", {
    task_id: taskId,
    platform,
    title: title || "",
    description: description || "",
  });
}
