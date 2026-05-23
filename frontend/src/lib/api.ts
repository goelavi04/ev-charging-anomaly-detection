import axios from 'axios';
import type { PredictionResponse, AnomaliesResponse, StatsResponse, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function predictAnomalies(file: File): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post<PredictionResponse>(`${API_BASE_URL}/predict`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function fetchAnomalies(limit: number): Promise<AnomaliesResponse> {
  const response = await axios.get<AnomaliesResponse>(`${API_BASE_URL}/anomalies?limit=${limit}`);
  return response.data;
}

export async function fetchStats(): Promise<StatsResponse> {
  const response = await axios.get<StatsResponse>(`${API_BASE_URL}/stats`);
  return response.data;
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await axios.get<HealthResponse>(`${API_BASE_URL}/health`);
  return response.data;
}
