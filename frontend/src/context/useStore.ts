import { create } from 'zustand';

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

  // Fleet
  vehicles: Vehicle[];
  addVehicle: (vehicle: Omit<Vehicle, 'id'>) => void;
  updateVehicle: (id: string, updates: Partial<Vehicle>) => void;
  deleteVehicle: (id: string) => void;

  // Drivers
  drivers: Driver[];
  addDriver: (driver: Omit<Driver, 'id'>) => void;
  updateDriver: (id: string, updates: Partial<Driver>) => void;
  deleteDriver: (id: string) => void;

  // Trips
  trips: Trip[];
  addTrip: (trip: Omit<Trip, 'id' | 'progress'>) => void;
  updateTrip: (id: string, updates: Partial<Trip>) => void;
  completeTrip: (id: string) => void;

  // Maintenance
  maintenanceLogs: MaintenanceLog[];
  addMaintenanceLog: (log: Omit<MaintenanceLog, 'id'>) => void;
  updateMaintenanceLog: (id: string, updates: Partial<MaintenanceLog>) => void;

  // Expenses
  expenses: FuelExpense[];
  addExpense: (expense: Omit<FuelExpense, 'id'>) => void;

  // Global Alerts (from Screen 1 & Screen 3 dashboard rules)
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
  Admin: {
    name: 'Admin',
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
  Dispatcher: {
    name: 'Dispatcher',
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

export const useStore = create<AppState>((set) => ({
  currentUser: null, // Start with null for Auth role selection
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

  // Vehicles
  vehicles: initialVehicles,
  addVehicle: (v) => set((state) => ({
    vehicles: [...state.vehicles, { ...v, id: `VEH-${Math.floor(1000 + Math.random() * 9000)}` }]
  })),
  updateVehicle: (id, updates) => set((state) => ({
    vehicles: state.vehicles.map((v) => (v.id === id ? { ...v, ...updates } : v))
  })),
  deleteVehicle: (id) => set((state) => ({
    vehicles: state.vehicles.filter((v) => v.id !== id)
  })),

  // Drivers
  drivers: initialDrivers,
  addDriver: (d) => set((state) => ({
    drivers: [...state.drivers, { ...d, id: `DRV-${Math.floor(100 + Math.random() * 900)}` }]
  })),
  updateDriver: (id, updates) => set((state) => ({
    drivers: state.drivers.map((d) => (d.id === id ? { ...d, ...updates } : d))
  })),
  deleteDriver: (id) => set((state) => ({
    drivers: state.drivers.filter((d) => d.id !== id)
  })),

  // Trips
  trips: initialTrips,
  addTrip: (t) => set((state) => ({
    trips: [...state.trips, { ...t, id: `TRP-${Math.floor(100 + Math.random() * 900)}`, progress: 0 }]
  })),
  updateTrip: (id, updates) => set((state) => ({
    trips: state.trips.map((t) => (t.id === id ? { ...t, ...updates } : t))
  })),
  completeTrip: (id) => set((state) => ({
    trips: state.trips.map((t) => (t.id === id ? { ...t, status: 'Completed', progress: 100 } : t))
  })),

  // Maintenance
  maintenanceLogs: initialMaintenance,
  addMaintenanceLog: (m) => set((state) => ({
    maintenanceLogs: [...state.maintenanceLogs, { ...m, id: `MTN-${Math.floor(100 + Math.random() * 900)}` }]
  })),
  updateMaintenanceLog: (id, updates) => set((state) => ({
    maintenanceLogs: state.maintenanceLogs.map((m) => (m.id === id ? { ...m, ...updates } : m))
  })),

  // Expenses
  expenses: initialExpenses,
  addExpense: (e) => set((state) => ({
    expenses: [...state.expenses, { ...e, id: `EXP-${Math.floor(100 + Math.random() * 900)}` }]
  })),

  // Alerts
  alerts: initialAlerts,
  resolveAlert: (id) => set((state) => ({
    alerts: state.alerts.filter((a) => a.id !== id)
  }))
}));
