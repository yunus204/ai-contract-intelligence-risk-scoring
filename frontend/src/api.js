import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadContract = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/api/contracts/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(
    `/api/contracts/tasks/${taskId}`
  );

  return response.data;
};

export const searchContract = async ({
  contractId,
  query,
  topK = 5,
}) => {
  const response = await api.post(
    "/api/search",
    {
      contract_id: contractId,
      query,
      top_k: topK,
    }
  );

  return response.data;
};

export default api;