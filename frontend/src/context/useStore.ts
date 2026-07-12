import { create } from 'zustand';
import { api } from '../lib/api';

// Types definition
export interface Vehicle {
  id: string;
  type: string;
  plate: string;
  model: string;
  status: 'Active' | 'Maintenance' | 'Inactive';
  lastMaintenance: string;
  nextMaintenance: string;
  mileage: number;
}

export interface Driver {
  id: string;
  name: string;
  licenseNo: string;
  licenseType: string;
  expiryDate: string;
  status: 'Active' | 'On Leave' | 'Suspended';
  safetyScore: number;
  safeHours: number;
}

export interface Trip {
  id: string;
  vehicleId: string;
  driverId: string;
  cargoType: string;
  weight: number;
  routeFrom: string;
  routeTo: string;
  dispatchTime: string;
  eta: string;
  priority: 'High' | 'Medium' | 'Low';
  status: 'Scheduled' | 'In-Transit' | 'Delayed' | 'Completed';
  progress: number; // 0 to 100
}

export interface MaintenanceLog {
  id: string;
  vehicleId: string;
  serviceType: string;
  provider: string;
  date: string;
  cost: number;
  status: 'Scheduled' | 'In Progress' | 'Completed';
}

export interface FuelExpense {
  id: string;
  date: string;
  vehicleId: string;
  liters: number;
  cost: number;
  odometer: number;
  location: string;
  type: 'Fuel' | 'Repair' | 'Toll' | 'Other';
}

export interface RolePermissions {
  fleet: { read: boolean; write: boolean };
  drivers: { read: boolean; write: boolean };
  trips: { read: boolean; write: boolean };
  maintenance: { read: boolean; write: boolean };
  finance: { read: boolean; write: boolean };
  settings: { read: boolean; write: boolean };
}

export interface RoleConfig {
  name: string;
  description: string;
  permissions: RolePermissions;
}

interface AppState {
  // Authentication / Role
  currentUser: { email: string; role: string } | null;
  rolesConfig: Record<string, RoleConfig>;
  setCurrentUser: (user: { email: string; role: string } | null) => void;
  updateRolePermissions: (roleName: string, category: keyof RolePermissions, type: 'read' | 'write', value: boolean) => void;

  // Real Database Sync Actions
  fetchVehicles: () => Promise<void>;
  fetchDrivers: () => Promise<void>;
  fetchTrips: () => Promise<void>;
  fetchMaintenanceLogs: () => Promise<void>;
  fetchExpenses: () => Promise<void>;

  // Fleet
  vehicles: Vehicle[];
  addVehicle: (vehicle: Omit<Vehicle, 'id'>) => Promise<void>;
  updateVehicle: (id: string, updates: Partial<Vehicle>) => Promise<void>;
  deleteVehicle: (id: string) => Promise<void>;

  // Drivers
  drivers: Driver[];
  addDriver: (driver: Omit<Driver, 'id'>) => Promise<void>;
  updateDriver: (id: string, updates: Partial<Driver>) => Promise<void>;
  deleteDriver: (id: string) => Promise<void>;

  // Trips
  trips: Trip[];
  addTrip: (trip: Omit<Trip, 'id' | 'progress'>) => Promise<void>;
  updateTrip: (id: string, updates: Partial<Trip>) => Promise<void>;
  completeTrip: (id: string) => Promise<void>;

  // Maintenance
  maintenanceLogs: MaintenanceLog[];
  addMaintenanceLog: (log: Omit<MaintenanceLog, 'id'>) => Promise<void>;
  updateMaintenanceLog: (id: string, updates: Partial<MaintenanceLog>) => Promise<void>;

  // Expenses
  expenses: FuelExpense[];
  addExpense: (expense: Omit<FuelExpense, 'id'>) => Promise<void>;

  // Alerts
  alerts: {
    id: string;
    vehicleId: string;
    status: 'Warning' | 'Critical' | 'Success' | 'Info';
    driver: string;
    description: string;
    time: string;
  }[];
  resolveAlert: (id: string) => void;
}

// Fallback Mock Data definition
const initialVehicles: Vehicle[] = [
  { id: 'VEH-0987', type: 'Flatbed', plate: 'TX-7890', model: 'Peterbilt 579', status: 'Active', lastMaintenance: '2023-12-04', nextMaintenance: '2024-06-04', mileage: 120400 },
  { id: 'VEH-1243', type: 'Dry Van', plate: 'CA-4321', model: 'Freightliner Cascadia', status: 'Maintenance', lastMaintenance: '2024-01-10', nextMaintenance: '2024-04-10', mileage: 94800 },
  { id: 'VEH-8831', type: 'Reefer', plate: 'NY-8831', model: 'Volvo VNL 860', status: 'Active', lastMaintenance: '2023-10-11', nextMaintenance: '2024-04-11', mileage: 145200 },
  { id: 'VEH-2099', type: 'Tanker', plate: 'IL-2099', model: 'Kenworth T680', status: 'Inactive', lastMaintenance: '2023-08-02', nextMaintenance: '2024-02-02', mileage: 210000 },
  { id: 'VEH-3351', type: 'Box Truck', plate: 'FL-3351', model: 'Hino 268', status: 'Active', lastMaintenance: '2024-02-14', nextMaintenance: '2024-08-14', mileage: 48900 }
];

const initialDrivers: Driver[] = [
  { id: 'DRV-001', name: 'John Doe', licenseNo: 'DL-987654', licenseType: 'CDL-A', expiryDate: '2028-12-15', status: 'Active', safetyScore: 98, safeHours: 2400 },
  { id: 'DRV-002', name: 'Jane Smith', licenseNo: 'DL-432109', licenseType: 'CDL-A', expiryDate: '2027-08-22', status: 'Active', safetyScore: 95, safeHours: 1850 },
  { id: 'DRV-003', name: 'Bob Johnson', licenseNo: 'DL-883144', licenseType: 'CDL-B', expiryDate: '2026-05-10', status: 'Active', safetyScore: 92, safeHours: 3100 },
  { id: 'DRV-004', name: 'Alice Brown', licenseNo: 'DL-209911', licenseType: 'CDL-A', expiryDate: '2029-11-04', status: 'On Leave', safetyScore: 88, safeHours: 1200 },
  { id: 'DRV-005', name: 'Charlie Davis', licenseNo: 'DL-554433', licenseType: 'CDL-A', expiryDate: '2025-02-28', status: 'Suspended', safetyScore: 76, safeHours: 850 }
];

const initialTrips: Trip[] = [
  { id: 'TRP-101', vehicleId: 'VEH-0987', driverId: 'DRV-001', cargoType: 'Electronics', weight: 18000, routeFrom: 'Houston, TX', routeTo: 'Dallas, TX', dispatchTime: '08:00', eta: '12:30', priority: 'High', status: 'In-Transit', progress: 65 },
  { id: 'TRP-102', vehicleId: 'VEH-8831', driverId: 'DRV-003', cargoType: 'Frozen Foods', weight: 22000, routeFrom: 'Los Angeles, CA', routeTo: 'Phoenix, AZ', dispatchTime: '06:00', eta: '14:00', priority: 'Medium', status: 'In-Transit', progress: 40 },
  { id: 'TRP-103', vehicleId: 'VEH-3351', driverId: 'DRV-002', cargoType: 'Retail Goods', weight: 8000, routeFrom: 'New York, NY', routeTo: 'Boston, MA', dispatchTime: '09:30', eta: '13:45', priority: 'Low', status: 'Scheduled', progress: 0 }
];

const initialMaintenance: MaintenanceLog[] = [
  { id: 'MTN-501', vehicleId: 'VEH-1243', serviceType: 'Brake Wear Replacement & Inspection', provider: 'Speedy Fleet Services', date: '2024-01-10', cost: 1250, status: 'Completed' },
  { id: 'MTN-502', vehicleId: 'VEH-2099', serviceType: 'Engine Tuning & Filter Replacement', provider: 'Kenworth Authorized Center', date: '2024-02-15', cost: 890, status: 'Scheduled' },
  { id: 'MTN-503', vehicleId: 'VEH-0987', serviceType: 'Tire Rotation & Wheel Alignment', provider: 'Pilot Service Center', date: '2024-03-01', cost: 420, status: 'Scheduled' }
];

const initialExpenses: FuelExpense[] = [
  { id: 'EXP-901', date: '2024-02-10', vehicleId: 'VEH-0987', liters: 450, cost: 630.00, odometer: 119800, location: 'Love\'s Travel Stop, TX', type: 'Fuel' },
  { id: 'EXP-902', date: '2024-02-12', vehicleId: 'VEH-8831', liters: 600, cost: 840.00, odometer: 144600, location: 'Pilot Flying J, NM', type: 'Fuel' },
  { id: 'EXP-903', date: '2024-02-13', vehicleId: 'VEH-1243', liters: 0, cost: 1250.00, odometer: 94800, location: 'Speedy Fleet Services, CA', type: 'Repair' },
  { id: 'EXP-904', date: '2024-02-14', vehicleId: 'VEH-3351', liters: 120, cost: 168.00, odometer: 48900, location: 'Shell Station, NY', type: 'Fuel' }
];

const initialAlerts = [
  { id: 'ALT-01', vehicleId: 'VEH-0987', status: 'Warning' as const, driver: 'John Doe', description: 'Low Oil Pressure warning detected', time: '10 min ago' },
  { id: 'ALT-02', vehicleId: 'VEH-1243', status: 'Critical' as const, driver: 'Jane Smith', description: 'Brake wear threshold warning', time: '1 hr ago' },
  { id: 'ALT-03', vehicleId: 'VEH-8831', status: 'Warning' as const, driver: 'Bob Johnson', description: 'High Coolant Temperature detected', time: '3 hrs ago' }
];

const defaultRoles: Record<string, RoleConfig> = {
  'Fleet Manager': {
    name: 'Fleet Manager',
    description: 'Full administrative access to logistics command configuration, RBAC settings, registries and dispatching.',
    permissions: {
      fleet: { read: true, write: true },
      drivers: { read: true, write: true },
      trips: { read: true, write: true },
      maintenance: { read: true, write: true },
      finance: { read: true, write: true },
      settings: { read: true, write: true }
    }
  },
  Driver: {
    name: 'Driver',
    description: 'Manage active runs, assign vehicles/drivers, log routes and watch live telemetry.',
    permissions: {
      fleet: { read: true, write: false },
      drivers: { read: true, write: false },
      trips: { read: true, write: true },
      maintenance: { read: true, write: false },
      finance: { read: true, write: false },
      settings: { read: true, write: false }
    }
  },
  'Safety Officer': {
    name: 'Safety Officer',
    description: 'Monitor driver performance, licensing logs, safe operations thresholds and safety logs.',
    permissions: {
      fleet: { read: true, write: false },
      drivers: { read: true, write: true },
      trips: { read: true, write: false },
      maintenance: { read: true, write: true },
      finance: { read: false, write: false },
      settings: { read: true, write: false }
    }
  },
  'Financial Analyst': {
    name: 'Financial Analyst',
    description: 'Full accounting control of fuel consumption, repair budgets and operational cost reports.',
    permissions: {
      fleet: { read: true, write: false },
      drivers: { read: false, write: false },
      trips: { read: true, write: false },
      maintenance: { read: true, write: false },
      finance: { read: true, write: true },
      settings: { read: true, write: false }
    }
  }
};

// Data mapper helpers
const mapBackendVehicleToFrontend = (v: any): Vehicle => ({
  id: v.id || v._id,
  type: v.vehicle_type,
  plate: v.registration_number,
  model: v.vehicle_name + ' ' + v.vehicle_model,
  status: v.status === 'Available' ? 'Active' : v.status === 'In Shop' ? 'Maintenance' : 'Inactive',
  lastMaintenance: v.created_at?.slice(0, 10) || '',
  nextMaintenance: '',
  mileage: v.current_odometer
});

const mapBackendDriverToFrontend = (d: any): Driver => ({
  id: d.id || d._id,
  name: `${d.first_name} ${d.last_name}`,
  licenseNo: d.license_number,
  licenseType: 'CDL-A',
  expiryDate: d.license_expiry?.slice(0, 10) || '',
  status: d.driver_status === 'Available' ? 'Active' : d.driver_status === 'Off Duty' ? 'On Leave' : 'Suspended',
  safetyScore: d.safety_score,
  safeHours: 1500
});

const mapBackendTripToFrontend = (t: any): Trip => ({
  id: t.trip_number || t.id || t._id,
  vehicleId: String(t.vehicle_id),
  driverId: String(t.driver_id),
  cargoType: t.cargo_description,
  weight: t.cargo_weight,
  routeFrom: t.source,
  routeTo: t.destination,
  dispatchTime: t.dispatch_time ? t.dispatch_time.slice(11, 16) : '08:00',
  eta: t.expected_arrival ? t.expected_arrival.slice(11, 16) : '12:00',
  priority: t.priority === 'High' || t.priority === 'Urgent' ? 'High' : t.priority === 'Normal' ? 'Medium' : 'Low',
  status: t.status === 'Dispatched' ? 'In-Transit' : t.status === 'Completed' ? 'Completed' : t.status === 'Cancelled' ? 'Delayed' : 'Scheduled',
  progress: t.status === 'Completed' ? 100 : t.status === 'Dispatched' ? 50 : 0
});

const mapBackendMaintenanceToFrontend = (m: any): MaintenanceLog => ({
  id: m.maintenance_id || m.id || m._id,
  vehicleId: String(m.vehicle_id),
  serviceType: m.title || m.maintenance_type,
  provider: m.vendor_name,
  date: m.scheduled_date ? String(m.scheduled_date) : m.created_at?.slice(0, 10) || '',
  cost: m.actual_cost ?? m.estimated_cost ?? 0,
  status: m.status === 'Completed' ? 'Completed' : m.status === 'In Progress' ? 'In Progress' : 'Scheduled'
});

const mapBackendExpenseToFrontend = (e: any): FuelExpense => ({
  id: e.expense_id || e.id || e._id,
  date: e.expense_date ? String(e.expense_date) : e.created_at?.slice(0, 10) || '',
  vehicleId: String(e.vehicle_id),
  liters: 0,
  cost: e.amount,
  odometer: 0,
  location: e.vendor,
  type: e.expense_type === 'Fuel' ? 'Fuel' : e.expense_type === 'Repair' ? 'Repair' : e.expense_type === 'Toll' ? 'Toll' : 'Other'
});

export const useStore = create<AppState>((set, get) => ({
  currentUser: null,
  rolesConfig: defaultRoles,
  
  setCurrentUser: (user) => set({ currentUser: user }),
  
  updateRolePermissions: (roleName, category, type, value) => set((state) => {
    const role = state.rolesConfig[roleName];
    if (!role) return {};
    
    return {
      rolesConfig: {
        ...state.rolesConfig,
        [roleName]: {
          ...role,
          permissions: {
            ...role.permissions,
            [category]: {
              ...role.permissions[category],
              [type]: value
            }
          }
        }
      }
    };
  }),

  // Database Sync routines with dual fallback
  fetchVehicles: async () => {
    try {
      const res = await api.getVehicles();
      if (res && Array.isArray(res.items)) {
        set({ vehicles: res.items.map(mapBackendVehicleToFrontend) });
      }
    } catch (e) {
      console.warn("Backend connection unavailable; using offline vehicles cache.", e);
    }
  },

  fetchDrivers: async () => {
    try {
      const res = await api.getDrivers();
      if (res && Array.isArray(res.items)) {
        set({ drivers: res.items.map(mapBackendDriverToFrontend) });
      }
    } catch (e) {
      console.warn("Backend connection unavailable; using offline drivers cache.", e);
    }
  },

  fetchTrips: async () => {
    try {
      const res = await api.getTrips();
      if (res && Array.isArray(res.items)) {
        set({ trips: res.items.map(mapBackendTripToFrontend) });
      }
    } catch (e) {
      console.warn("Backend connection unavailable; using offline dispatches cache.", e);
    }
  },

  fetchMaintenanceLogs: async () => {
    try {
      const res = await api.getMaintenance();
      if (res && Array.isArray(res.items)) {
        set({ maintenanceLogs: res.items.map(mapBackendMaintenanceToFrontend) });
      }
    } catch (e) {
      console.warn("Backend connection unavailable; using offline maintenance cache.", e);
    }
  },

  fetchExpenses: async () => {
    try {
      const res = await api.getExpenses();
      if (res && Array.isArray(res.items)) {
        set({ expenses: res.items.map(mapBackendExpenseToFrontend) });
      }
    } catch (e) {
      console.warn("Backend connection unavailable; using offline expenses cache.", e);
    }
  },

  // Vehicles
  vehicles: initialVehicles,
  addVehicle: async (v) => {
    try {
      const payload = {
        registration_number: v.plate,
        vehicle_name: v.model.split(' ')[0] || 'Truck',
        vehicle_model: v.model.split(' ').slice(1).join(' ') || 'Standard',
        vehicle_type: v.type === 'Box Truck' ? 'Truck' : v.type === 'Van' ? 'Van' : 'Other',
        maximum_load_capacity: 18000,
        current_odometer: v.mileage,
        acquisition_cost: 85000,
        purchase_date: new Date().toISOString().split('T')[0],
        status: v.status === 'Active' ? 'Available' : v.status === 'Maintenance' ? 'In Shop' : 'Retired',
        region: 'Texas'
      };
      await api.createVehicle(payload);
      await get().fetchVehicles();
    } catch (e) {
      console.warn("API write failed, mutating local store.", e);
      set((state) => ({
        vehicles: [...state.vehicles, { ...v, id: `VEH-${Math.floor(1000 + Math.random() * 9000)}` }]
      }));
    }
  },

  updateVehicle: async (id, updates) => {
    try {
      const payload: Record<string, any> = {};
      if (updates.plate) payload.registration_number = updates.plate;
      if (updates.mileage) payload.current_odometer = updates.mileage;
      if (updates.status) {
        payload.status = updates.status === 'Active' ? 'Available' : updates.status === 'Maintenance' ? 'In Shop' : 'Retired';
      }
      await api.updateVehicle(id, payload);
      await get().fetchVehicles();
    } catch (e) {
      console.warn("API update failed, mutating local store.", e);
      set((state) => ({
        vehicles: state.vehicles.map((v) => (v.id === id ? { ...v, ...updates } : v))
      }));
    }
  },

  deleteVehicle: async (id) => {
    try {
      await api.deleteVehicle(id);
      await get().fetchVehicles();
    } catch (e) {
      console.warn("API delete failed, mutating local store.", e);
      set((state) => ({
        vehicles: state.vehicles.filter((v) => v.id !== id)
      }));
    }
  },

  // Drivers
  drivers: initialDrivers,
  addDriver: async (d) => {
    try {
      const payload = {
        license_number: d.licenseNo,
        first_name: d.name.split(' ')[0] || 'Operator',
        last_name: d.name.split(' ').slice(1).join(' ') || 'Core',
        license_expiry: d.expiryDate,
        safety_score: d.safetyScore,
        driver_status: d.status === 'Active' ? 'Available' : d.status === 'On Leave' ? 'Off Duty' : 'Suspended',
        region: 'Texas'
      };
      await api.createDriver(payload);
      await get().fetchDrivers();
    } catch (e) {
      console.warn("API write failed, mutating local store.", e);
      set((state) => ({
        drivers: [...state.drivers, { ...d, id: `DRV-${Math.floor(100 + Math.random() * 900)}` }]
      }));
    }
  },

  updateDriver: async (id, updates) => {
    try {
      const payload: Record<string, any> = {};
      if (updates.name) {
        payload.first_name = updates.name.split(' ')[0] || '';
        payload.last_name = updates.name.split(' ').slice(1).join(' ') || '';
      }
      if (updates.expiryDate) payload.license_expiry = updates.expiryDate;
      if (updates.status) {
        payload.driver_status = updates.status === 'Active' ? 'Available' : updates.status === 'On Leave' ? 'Off Duty' : 'Suspended';
      }
      await api.updateDriver(id, payload);
      await get().fetchDrivers();
    } catch (e) {
      console.warn("API update failed, mutating local store.", e);
      set((state) => ({
        drivers: state.drivers.map((d) => (d.id === id ? { ...d, ...updates } : d))
      }));
    }
  },

  deleteDriver: async (id) => {
    try {
      await api.deleteDriver(id);
      await get().fetchDrivers();
    } catch (e) {
      console.warn("API delete failed, mutating local store.", e);
      set((state) => ({
        drivers: state.drivers.filter((d) => d.id !== id)
      }));
    }
  },

  // Trips
  trips: initialTrips,
  addTrip: async (t) => {
    try {
      const payload = {
        trip_number: `TRP-${Math.floor(100 + Math.random() * 900)}`,
        vehicle_id: t.vehicleId,
        driver_id: t.driverId,
        source: t.routeFrom,
        destination: t.routeTo,
        cargo_description: t.cargoType,
        cargo_weight: t.weight,
        estimated_distance: 350.0,
        estimated_duration: 300,
        priority: t.priority === 'High' ? 'High' : 'Normal',
        status: 'Dispatched'
      };
      await api.createTrip(payload);
      await get().fetchTrips();
    } catch (e) {
      console.warn("API write failed, mutating local store.", e);
      set((state) => ({
        trips: [...state.trips, { ...t, id: `TRP-${Math.floor(100 + Math.random() * 900)}`, progress: 0 }]
      }));
    }
  },

  updateTrip: async (id, updates) => {
    try {
      // Backend does not have single partial update, fallback or reload
      await get().fetchTrips();
    } catch (e) {
      set((state) => ({
        trips: state.trips.map((t) => (t.id === id ? { ...t, ...updates } : t))
      }));
    }
  },

  completeTrip: async (id) => {
    try {
      await api.completeTrip(id, { actual_distance: 350.0, fuel_consumed: 45.0, final_odometer: 120000 });
      await get().fetchTrips();
    } catch (e) {
      console.warn("API complete failed, mutating local store.", e);
      set((state) => ({
        trips: state.trips.map((t) => (t.id === id ? { ...t, status: 'Completed', progress: 100 } : t))
      }));
    }
  },

  // Maintenance
  maintenanceLogs: initialMaintenance,
  addMaintenanceLog: async (m) => {
    try {
      const payload = {
        maintenance_id: `MTN-${Math.floor(100 + Math.random() * 900)}`,
        vehicle_id: m.vehicleId,
        maintenance_type: 'Service',
        title: m.serviceType,
        description: 'Scheduled maintenance checkup',
        priority: 'Normal',
        vendor_name: m.provider,
        estimated_cost: m.cost,
        scheduled_date: m.date,
        status: 'Pending'
      };
      await api.createMaintenance(payload);
      await get().fetchMaintenanceLogs();
    } catch (e) {
      console.warn("API write failed, mutating local store.", e);
      set((state) => ({
        maintenanceLogs: [...state.maintenanceLogs, { ...m, id: `MTN-${Math.floor(100 + Math.random() * 900)}` }]
      }));
    }
  },

  updateMaintenanceLog: async (id, updates) => {
    set((state) => ({
      maintenanceLogs: state.maintenanceLogs.map((m) => (m.id === id ? { ...m, ...updates } : m))
    }));
  },

  // Expenses
  expenses: initialExpenses,
  addExpense: async (e) => {
    try {
      const payload = {
        expense_id: `EXP-${Math.floor(100 + Math.random() * 900)}`,
        vehicle_id: e.vehicleId,
        expense_type: e.type === 'Fuel' ? 'Fuel' : e.type === 'Repair' ? 'Repair' : e.type === 'Toll' ? 'Toll' : 'Miscellaneous',
        amount: e.cost,
        vendor: e.location,
        invoice_number: `INV-${Date.now()}`,
        expense_date: e.date,
        description: `Odometer reading logged: ${e.odometer}`
      };
      await api.createExpense(payload);
      await get().fetchExpenses();
    } catch (err) {
      console.warn("API write failed, mutating local store.", err);
      set((state) => ({
        expenses: [...state.expenses, { ...e, id: `EXP-${Math.floor(100 + Math.random() * 900)}` }]
      }));
    }
  },

  // Alerts
  alerts: initialAlerts,
  resolveAlert: (id) => set((state) => ({
    alerts: state.alerts.filter((a) => a.id !== id)
  }))
}));
