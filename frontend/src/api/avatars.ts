import client from "./client";

export function createAvatar(name: string, photoUrls: Record<string, string>) {
  return client.post("/api/avatars", { name, photo_urls: photoUrls });
}

export async function uploadPhoto(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  const resp = await client.post("/api/avatars/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data.url;
}

export function getAvatars() {
  return client.get("/api/avatars");
}

export function deleteAvatar(id: string) {
  return client.delete(`/api/avatars/${id}`);
}
