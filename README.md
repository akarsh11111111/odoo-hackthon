# TransitOps — Smart Transport Operations Platform

TransitOps is a centralized, high-fidelity transport operations command center designed for fleet managers, drivers, safety compliance officers, and financial analysts. It serves as a digital twin for commercial vehicle fleets, managing the complete lifecycle of logistics operations from vehicle registration and driver logs to active dispatches, maintenance windows, and fuel expenses.

---

## 🛠️ Technology Stack

### 🚀 Frontend
- **Framework**: React 19, Vite, TypeScript
- **Styling**: Tailwind CSS v4 (configured via CSS variables in `@tailwindcss/vite`)
- **State Management**: Zustand (in-memory client state store supporting role-based access configurations and local transactions)
- **Animations**: Framer Motion (used for page entry transitions, dashboard telemetry updates, and drawer animations)
- **Data Visualization**: Recharts (for weekly dispatch volumes, expense categories, and monthly budget logs)
- **UI Components**: Radix UI (Primitives for Avatars, Dialogs, Dropdowns, and Tabs), Lucide React (Industrial transport iconography), Sonner (Tactical action alerts)

### ⚙️ Backend
- **Framework**: Python 3.12+, FastAPI
- **Database**: MongoDB (via Motor async driver)
- **Database Object-Document Mapper (ODM)**: Beanie ODM
- **Validation**: Pydantic v2 (for models, schemas, and configurations)
- **ASGI Server**: Uvicorn
- **Authentication**: JWT Bearer Tokens, Bcrypt password hashing

---

## 🔒 Security & Access Validation

### 1. One-Time Password (OTP) Verification
- **Dual-Mode OTP Gate**: Before establishing user sessions, the platform presents a secure 6-digit OTP verification panel.
- **Email Delivery Integration**: Dispatches a dynamic 6-digit verification pin directly to the user's real email address using the `FormSubmit` AJAX delivery network.
- **Developer Test Override**: During offline test sessions or while using mock email accounts, developers can view the generated OTP directly in the browser's developer console (`F12`) for instant bypass.

### 2. Authorized Email Whitelisting
- **Domain Restriction**: Only corporate addresses ending with **`@transops.com`** are authorized to register user profiles. Registration attempts with non-corporate domains are rejected (returns HTTP 403 Forbidden).

### 3. Lockdown Credentials Validation
- Bypassing with random emails or passwords is blocked. Logins are strictly authenticated against:
  - Pre-configured role profiles (`manager@transops.com`, `driver@transops.com`, etc.)
  - Registered user accounts stored in the backend MongoDB server (or client-side localStorage fallback when running in offline mode).

---

## 📁 Repository Structure

### 💻 Frontend Architecture (`/frontend`)
- **`src/context/useStore.ts`**: The central application state container (Zustand). It defines standard mock data schemas representing:
  - **Vehicles**: Max load limits, odometers, acquisition costs, and status parameters (`Available`, `On Trip`, `In Shop`, `Retired`).
  - **Drivers**: License types (Class A/B), expiry dates, safety compliance metrics, and safe hours tracked.
  - **Trips**: Live routes, priority thresholds, payloads, cargo types, and live ETA trackers.
  - **Alerts**: Sensor malfunction alerts.
  - **Role configurations**: Access control settings matching PDF spec target users:
    - **`Fleet Manager`** (formerly Admin; full write control of assets)
    - **`Driver`** (formerly Dispatcher; handles trip planning and dispatch runs)
    - **`Safety Officer`** (tracks license compliance and service intervals)
    - **`Financial Analyst`** (reviews fuel logs and budgets)
- **`src/components/`**:
  - `Header.tsx`: Integrated digital ticker clock (CST), voice-recognition speech triggers, and notification feeds categorized chronologically.
  - `Sidebar.tsx`: Multi-layered collapsible workspace shortcuts.
  - `MapCanvas.tsx`: Vector-based logistics grid simulation rendering live data packets, animated coordinate arcs, and target HUD vehicle indicators.
  - `SpotlightCard.tsx`: Multi-directional hover illumination effects.
- **`src/pages/`**:
  - `Auth.tsx`: Two-column role selection gateway, register operator switcher, password integrity checker, and the secure OTP modal dialog overlay.
  - `Dashboard.tsx`: Interactive control panel featuring count-up telemetry metrics, weekly charts, route bottleneck advisories, and active task checklists.
  - `Fleet.tsx`: Master asset registry grids with CSV/Excel exports and details slide drawers containing visual chassis diagnostics.
  - `Drivers.tsx`: Drivers compliance hub showing CDL licenses, safe hours ratings, and safety recommendation logs.
  - `Dispatcher.tsx`: Live dispatches dashboard including weather map overlays and waypoint timelines.
  - `Maintenance.tsx`: Mechanical operations center managing active workshop bays and downtime analytics.
  - `FuelExpense.tsx`: Fleet billing registries displaying category expenses (Fuel vs Repairs vs Tolls) and budget limits.
  - `Analytics.tsx`: High-density reports filtering operational costs and vehicle return-on-investment (ROI) values.
  - `Settings.tsx`: Security access panel adjusting RBAC privileges, audit trails, and API integrations (e.g. SAP Fiori, Stripe).

### ⚙️ Backend Architecture (`/backend`)
- **`src/main.py`**: ASGI web service constructor configuring CORS middlewares, exception handlers, and database lifecycle.
- **`src/core/`**: Configuration loaders (Pydantic settings reading `.env`), logging formatters, database client connects, and exceptions.
- **`src/models/`**: Beanie ODM database document schemas mapping collections:
  - `Vehicle`, `Driver`, `Trip`, `Maintenance`, `Fuel`, `Expense`, `Audit`, `Auth`, `Notification`.
- **`src/repositories/`**: Repository patterns abstraction database interactions (read/write/queries) for each collection.
- **`src/api/`**: Endpoint routes:
  - `/auth`: Access checks and user authorization.
  - `/vehicle`, `/driver`, `/trip`: Asset CRUD registries and dispatch status switches.
  - `/maintenance`, `/fuel`, `/expense`: Service bay updates and financial invoices logs.
  - `/dashboard`, `/reports`: Multi-metric analytics aggregations.
- **`src/middleware/`**: Request context bindings and authentication token validators.

---

## ⚡ Setup & Launch Instructions

### 🛰️ Running the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Start local development server:
   ```bash
   npm run dev
   ```
4. Verify production compilation:
   ```bash
   npm run build
   ```

### 🗄️ Running the Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and configure your environment variables:
   ```bash
   cp .env.example .env
   # Update MongoDB URI and JWT configurations in .env
   ```
3. Install package in editable mode with development dependencies:
   ```bash
   pip install -e .[dev]
   ```
4. Launch the local FastAPI service:
   ```bash
   uvicorn src.main:app --reload
   ```
