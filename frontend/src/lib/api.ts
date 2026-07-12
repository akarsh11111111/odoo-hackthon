import axios, { AxiosError } from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const ACCESS_TOKEN_KEY = 'transops.access_token';
const REFRESH_TOKEN_KEY = 'transops.refresh_token';

type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  data: T | null;
  errors?: Array<{
    field: string;
    message: string;
    code: string;
  }> | null;
  timestamp: string;
};

type AuthUserRole = {
  id: string;
  role_name: string;
  permissions: string[];
  description: string | null;
};

type AuthUser = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  role: AuthUserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
};

type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_token_expires_in: number;
  refresh_token_expires_in: number;
};

type AuthSession = {
  user: AuthUser;
  tokens: AuthTokens;
};

type AuthMessage = {
  detail: string;
};

export type DashboardOverview = {
  total_vehicles: number;
  available_vehicles: number;
  on_trip_vehicles: number;
  vehicles_in_shop: number;
  retired_vehicles: number;
  total_drivers: number;
  available_drivers: number;
  drivers_on_trip: number;
  drivers_suspended: number;
  total_active_trips: number;
  completed_trips: number;
  cancelled_trips: number;
  pending_trips: number;
  fuel_cost: number;
  maintenance_cost: number;
  operational_cost: number;
  fleet_utilization_percent: number;
  average_fuel_efficiency: number | null;
  vehicle_roi: number | null;
};

export type DashboardKpi = {
  total_vehicles: number;
  available_vehicles: number;
  total_active_trips: number;
  total_drivers: number;
  fuel_cost: number;
  maintenance_cost: number;
  operational_cost: number;
  fleet_utilization_percent: number;
  average_fuel_efficiency: number | null;
  vehicle_roi: number | null;
};

export type VehicleListResult = {
  items: Array<Record<string, unknown>>;
  total: number;
  page: number;
  size: number;
};

export type DriverListResult = {
  items: Array<Record<string, unknown>>;
  total: number;
  page: number;
  size: number;
};

export type TripListResult = {
  items: Array<Record<string, unknown>>;
  total: number;
  page: number;
  size: number;
};

export type MaintenanceListResult = {
  items: Array<Record<string, unknown>>;
  total: number;
  page: number;
  size: number;
};

export type ExpenseListResult = {
  items: Array<Record<string, unknown>>;
  total: number;
  page: number;
  size: number;
};

const parseAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
const parseRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);

const persistAuthSession = (payload: AuthSession) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, payload.tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, payload.tokens.refresh_token);
};

export const clearAuthSession = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 15000
});

client.interceptors.request.use((config) => {
  const accessToken = parseAccessToken();

  if (accessToken && config.headers) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { __isRetry?: boolean });

    if (error.response?.status === 401 && originalRequest && !originalRequest.__isRetry) {
      const refreshToken = parseRefreshToken();

      if (!refreshToken) {
        clearAuthSession();
        return Promise.reject(error);
      }

      originalRequest.__isRetry = true;

      try {
        const response = await client.post<ApiEnvelope<AuthSession>>('/auth/refresh', {
          refresh_token: refreshToken
        });

        if (!response.data.data) {
          clearAuthSession();
          return Promise.reject(error);
        }

        persistAuthSession(response.data.data);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${response.data.data.tokens.access_token}`;
        }

        return await client.request(originalRequest);
      } catch (refreshError) {
        clearAuthSession();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

const unwrap = <T>(response: { data: ApiEnvelope<T> }) => response.data.data as T;

export const api = {
  register: async (payload: { first_name: string; last_name: string; email: string; phone?: string | null; password: string; role_name: string }) => {
    const response = await client.post<ApiEnvelope<AuthSession>>('/auth/register', payload);
    if (response.data.data) {
      persistAuthSession(response.data.data);
    }
    return response;
  },

  login: async (payload: { email: string; password: string; device?: string; ip_address?: string | null }) => {
    const response = await client.post<ApiEnvelope<AuthSession>>('/auth/login', payload);
    if (response.data.data) {
      persistAuthSession(response.data.data);
    }
    return response;
  },

  logout: async (refreshToken: string) => {
    const response = await client.post<ApiEnvelope<AuthMessage>>('/auth/logout', { refresh_token: refreshToken });
    clearAuthSession();
    return response;
  },

  getCurrentUser: async () => {
    const response = await client.get<ApiEnvelope<AuthUser>>('/auth/me');
    return unwrap<AuthUser>(response);
  },

  getVehicles: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<VehicleListResult>>('/vehicles', { params });
    return unwrap<VehicleListResult>(response);
  },

  getAvailableVehicles: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<VehicleListResult>>('/vehicles/available', { params });
    return unwrap<VehicleListResult>(response);
  },

  createVehicle: async (payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>('/vehicles', payload);
    return unwrap<Record<string, unknown>>(response);
  },

  updateVehicle: async (vehicleId: string, payload: Record<string, unknown>) => {
    const response = await client.put<ApiEnvelope<Record<string, unknown>>>(`/vehicles/${vehicleId}`, payload);
    return unwrap<Record<string, unknown>>(response);
  },

  deleteVehicle: async (vehicleId: string) => {
    const response = await client.delete<ApiEnvelope<Record<string, string>>>(`/vehicles/${vehicleId}`);
    return unwrap<Record<string, string>>(response);
  },

  getDrivers: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<DriverListResult>>('/drivers', { params });
    return unwrap<DriverListResult>(response);
  },

  getAvailableDrivers: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<DriverListResult>>('/drivers/available', { params });
    return unwrap<DriverListResult>(response);
  },

  createDriver: async (payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>('/drivers', payload);
    return unwrap<Record<string, unknown>>(response);
  },

  updateDriver: async (driverId: string, payload: Record<string, unknown>) => {
    const response = await client.put<ApiEnvelope<Record<string, unknown>>>(`/drivers/${driverId}`, payload);
    return unwrap<Record<string, unknown>>(response);
  },

  deleteDriver: async (driverId: string) => {
    const response = await client.delete<ApiEnvelope<Record<string, string>>>(`/drivers/${driverId}`);
    return unwrap<Record<string, string>>(response);
  },

  getTrips: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<TripListResult>>('/trips', { params });
    return unwrap<TripListResult>(response);
  },

  getActiveTrips: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<TripListResult>>('/trips/active', { params });
    return unwrap<TripListResult>(response);
  },

  createTrip: async (payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>('/trips', payload);
    return unwrap<Record<string, unknown>>(response);
  },

  dispatchTrip: async (tripId: string, payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>(`/trips/${tripId}/dispatch`, payload);
    return unwrap<Record<string, unknown>>(response);
  },

  completeTrip: async (tripId: string, payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>(`/trips/${tripId}/complete`, payload);
    return unwrap<Record<string, unknown>>(response);
  },

  getMaintenance: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<MaintenanceListResult>>('/maintenance', { params });
    return unwrap<MaintenanceListResult>(response);
  },

  getActiveMaintenance: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<MaintenanceListResult>>('/maintenance/active', { params });
    return unwrap<MaintenanceListResult>(response);
  },

  createMaintenance: async (payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>('/maintenance', payload);
    return unwrap<Record<string, unknown>>(response);
  },

  getFuelLogs: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<ExpenseListResult>>('/fuel-logs', { params });
    return unwrap<ExpenseListResult>(response);
  },

  getExpenses: async (params?: Record<string, unknown>) => {
    const response = await client.get<ApiEnvelope<ExpenseListResult>>('/expenses', { params });
    return unwrap<ExpenseListResult>(response);
  },

  createExpense: async (payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>('/expenses', payload);
    return unwrap<Record<string, unknown>>(response);
  },

  createFuelLog: async (payload: Record<string, unknown>) => {
    const response = await client.post<ApiEnvelope<Record<string, unknown>>>('/fuel-logs', payload);
    return unwrap<Record<string, unknown>>(response);
  },

  getDashboardOverview: async () => {
    const response = await client.get<ApiEnvelope<DashboardOverview>>('/dashboard/overview');
    return unwrap<DashboardOverview>(response);
  },

  getDashboardKpis: async () => {
    const response = await client.get<ApiEnvelope<DashboardKpi>>('/dashboard/kpis');
    return unwrap<DashboardKpi>(response);
  }
};

export const getStoredAccessToken = () => parseAccessToken();
export const getStoredRefreshToken = () => parseRefreshToken();
