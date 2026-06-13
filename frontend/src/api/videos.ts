import client from "./client";

export function createVideo(avatarId: string, templateId: string, scriptText: string) {
  return client.post("/api/videos", { avatar_id: avatarId, template_id: templateId, script_text: scriptText });
}

export function getVideos() {
  return client.get("/api/videos");
}

export function getVideo(id: string) {
  return client.get(`/api/videos/${id}`);
}

export function deleteVideo(id: string) {
  return client.delete(`/api/videos/${id}`);
}
