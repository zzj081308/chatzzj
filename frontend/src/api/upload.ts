import apiClient from "./client";

export async function uploadImage(file: File): Promise<{ image_url: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return apiClient
    .post("/upload/image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
}

export async function uploadFile(
  file: File
): Promise<{ file_url: string; file_name: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return apiClient
    .post("/upload/file", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
}

export async function uploadAvatar(
  file: File
): Promise<{ avatar_url: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return apiClient
    .post("/upload/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
}
