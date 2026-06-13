import axios from "axios";
import { ElMessage } from "element-plus";

const client = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 30000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || "请求失败";
    if (error.response?.status === 402) {
      ElMessage.error("算粒不足，请充值后再试");
    } else if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    } else {
      ElMessage.error(msg);
    }
    return Promise.reject(error);
  }
);

export default client;
