import client from "./client";

export function createAvatar(name: string, photoUrls: Record<string, string>) {
  return client.post("/api/avatars", { name, photo_urls: photoUrls });
}

export function getAvatars() {
  return client.get("/api/avatars");
}

export function deleteAvatar(id: string) {
  return client.delete(`/api/avatars/${id}`);
}
