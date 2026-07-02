import client from "./client";

export function createVideo(avatarId: string, templateId: string, scriptText: string, prompt?: string, refVideoUrl?: string, duration?: number, sceneImageUrl?: string) {
  return client.post("/api/videos", {
    avatar_id: avatarId || null,
    template_id: templateId,
    script_text: scriptText,
    prompt: prompt || null,
    reference_video_url: refVideoUrl || null,
    duration: duration || 5,
    scene_image_url: sceneImageUrl || null,
  });
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
