import React, { useEffect, useRef, useState } from 'react';
import { useStore } from '../context/useStore';
import type { Trip } from '../context/useStore';

interface CityNode {
  name: string;
  x: number;
  y: number;
  lat: number;
  lng: number;
}

const CITIES: Record<string, CityNode> = {
  'Houston, TX': { name: 'Houston', x: 500, y: 380, lat: 29.7604, lng: -95.3698 },
  'Dallas, TX': { name: 'Dallas', x: 480, y: 310, lat: 32.7767, lng: -96.7970 },
  'Los Angeles, CA': { name: 'Los Angeles', x: 120, y: 250, lat: 34.0522, lng: -118.2437 },
  'Phoenix, AZ': { name: 'Phoenix', x: 230, y: 270, lat: 33.4484, lng: -112.0740 },
  'New York, NY': { name: 'New York', x: 850, y: 150, lat: 40.7128, lng: -74.0060 },
  'Boston, MA': { name: 'Boston', x: 910, y: 120, lat: 42.3601, lng: -71.0589 },
  'Chicago, IL': { name: 'Chicago', x: 620, y: 180, lat: 41.8781, lng: -87.6298 },
  'Indianapolis, IN': { name: 'Indianapolis', x: 650, y: 210, lat: 39.7684, lng: -86.1581 },
  'Denver, CO': { name: 'Denver', x: 380, y: 220, lat: 39.7392, lng: -104.9903 },
  'Atlanta, GA': { name: 'Atlanta', x: 720, y: 300, lat: 33.7490, lng: -84.3880 }
};

export const MapCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const trips = useStore((state) => state.trips);
  const vehicles = useStore((state) => state.vehicles);
  const drivers = useStore((state) => state.drivers);
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
  const [animationTick, setAnimationTick] = useState(0);

  // Simulation loop for animations
  useEffect(() => {
    const handle = setInterval(() => {
      setAnimationTick((t) => t + 1);
    }, 50);
    return () => clearInterval(handle);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas with very dark slate backfill
    ctx.fillStyle = '#08090C';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw cyber tactical coordinate grid
    ctx.strokeStyle = 'rgba(0, 245, 255, 0.025)';
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw outer boundary crop ticks
    ctx.strokeStyle = 'rgba(0, 245, 255, 0.15)';
    ctx.lineWidth = 1;
    const margin = 20;
    // Top-Left corner ticks
    ctx.beginPath(); ctx.moveTo(margin, margin + 15); ctx.lineTo(margin, margin); ctx.lineTo(margin + 15, margin); ctx.stroke();
    // Top-Right corner ticks
    ctx.beginPath(); ctx.moveTo(canvas.width - margin, margin + 15); ctx.lineTo(canvas.width - margin, margin); ctx.lineTo(canvas.width - margin - 15, margin); ctx.stroke();
    // Bottom-Left corner ticks
    ctx.beginPath(); ctx.moveTo(margin, canvas.height - margin - 15); ctx.lineTo(margin, canvas.height - margin); ctx.lineTo(margin + 15, canvas.height - margin); ctx.stroke();
    // Bottom-Right corner ticks
    ctx.beginPath(); ctx.moveTo(canvas.width - margin, canvas.height - margin - 15); ctx.lineTo(canvas.width - margin, canvas.height - margin); ctx.lineTo(canvas.width - margin - 15, canvas.height - margin); ctx.stroke();

    // Draw sweeping radar wave
    const scanRadius = (animationTick * 3) % (canvas.width * 0.7);
    const gradScan = ctx.createRadialGradient(canvas.width / 2, canvas.height / 2, 0, canvas.width / 2, canvas.height / 2, scanRadius + 20);
    gradScan.addColorStop(0, 'rgba(0, 245, 255, 0)');
    gradScan.addColorStop(Math.max(0, (scanRadius - 10) / (scanRadius + 20)), 'rgba(0, 245, 255, 0)');
    gradScan.addColorStop(1, 'rgba(0, 245, 255, 0.025)');
    ctx.fillStyle = gradScan;
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, scanRadius + 20, 0, Math.PI * 2);
    ctx.fill();

    // Draw background routes (static vectors)
    ctx.strokeStyle = 'rgba(0, 245, 255, 0.05)';
    ctx.lineWidth = 1;
    const routePairs = [
      [CITIES['Los Angeles, CA'], CITIES['Phoenix, AZ']],
      [CITIES['Phoenix, AZ'], CITIES['Denver, CO']],
      [CITIES['Denver, CO'], CITIES['Dallas, TX']],
      [CITIES['Dallas, TX'], CITIES['Houston, TX']],
      [CITIES['Houston, TX'], CITIES['Atlanta, GA']],
      [CITIES['Dallas, TX'], CITIES['Chicago, IL']],
      [CITIES['Chicago, IL'], CITIES['Indianapolis, IN']],
      [CITIES['Indianapolis, IN'], CITIES['Atlanta, GA']],
      [CITIES['Chicago, IL'], CITIES['New York, NY']],
      [CITIES['New York, NY'], CITIES['Boston, MA']]
    ];

    routePairs.forEach(([c1, c2]) => {
      ctx.beginPath();
      ctx.moveTo(c1.x, c1.y);
      ctx.lineTo(c2.x, c2.y);
      ctx.stroke();
    });

    // Draw active trip routes (data flows - animated dotted vectors)
    trips.forEach((trip) => {
      if (trip.status !== 'In-Transit') return;
      const start = CITIES[trip.routeFrom];
      const end = CITIES[trip.routeTo];
      if (!start || !end) return;

      // Glow route line
      ctx.strokeStyle = 'rgba(0, 245, 255, 0.15)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();

      // Data packets flow animation
      ctx.strokeStyle = '#00F5FF';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 12]);
      ctx.lineDashOffset = -animationTick * 1.5;
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
      ctx.setLineDash([]); // reset
    });

    // Draw city nodes (HUD style brackets)
    Object.values(CITIES).forEach((city) => {
      // Outer HUD target brackets
      ctx.strokeStyle = 'rgba(0, 245, 255, 0.2)';
      ctx.lineWidth = 1;
      const size = 6;
      ctx.beginPath();
      // top-left
      ctx.moveTo(city.x - size, city.y - size + 2); ctx.lineTo(city.x - size, city.y - size); ctx.lineTo(city.x - size + 2, city.y - size);
      // top-right
      ctx.moveTo(city.x + size, city.y - size + 2); ctx.lineTo(city.x + size, city.y - size); ctx.lineTo(city.x + size - 2, city.y - size);
      // bottom-left
      ctx.moveTo(city.x - size, city.y + size - 2); ctx.lineTo(city.x - size, city.y + size); ctx.lineTo(city.x - size + 2, city.y + size);
      // bottom-right
      ctx.moveTo(city.x + size, city.y + size - 2); ctx.lineTo(city.x + size, city.y + size); ctx.lineTo(city.x + size - 2, city.y + size);
      ctx.stroke();

      // Core dot
      ctx.fillStyle = '#00F5FF';
      ctx.beginPath();
      ctx.arc(city.x, city.y, 2, 0, Math.PI * 2);
      ctx.fill();

      // City Label
      ctx.fillStyle = 'rgba(0, 245, 255, 0.4)';
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(city.name.toUpperCase(), city.x, city.y - 10);
    });

    // Draw moving vehicles
    trips.forEach((trip) => {
      if (trip.status !== 'In-Transit') return;
      const start = CITIES[trip.routeFrom];
      const end = CITIES[trip.routeTo];
      if (!start || !end) return;

      const baseProgress = trip.progress / 100;
      const simProgress = Math.min(1, Math.max(0, baseProgress + Math.sin(animationTick * 0.05) * 0.003));

      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const x = start.x + dx * simProgress;
      const y = start.y + dy * simProgress;

      const isSelected = selectedTrip?.id === trip.id;

      // Rotating target crosshair for selected vehicle
      if (isSelected) {
        ctx.strokeStyle = '#D88A1D';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(x, y, 14, 0, Math.PI * 2);
        ctx.stroke();

        ctx.setLineDash([2, 4]);
        ctx.strokeStyle = 'rgba(216, 138, 29, 0.4)';
        ctx.beginPath();
        ctx.arc(x, y, 18, (animationTick * 0.03), (animationTick * 0.03) + Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // Vehicle dot core
      ctx.fillStyle = isSelected ? '#D88A1D' : '#00F5FF';
      ctx.shadowBlur = 10;
      ctx.shadowColor = isSelected ? 'rgba(216, 138, 29, 0.6)' : 'rgba(0, 245, 255, 0.6)';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0; // reset glow

      // Label index tag
      ctx.fillStyle = isSelected ? '#D88A1D' : '#e2e8f0';
      ctx.font = 'bold 8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(trip.vehicleId.replace('VEH-', 'TRK-'), x, y + 14);
    });

  }, [trips, animationTick, selectedTrip]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = ((e.clientX - rect.left) / rect.width) * canvas.width;
    const clickY = ((e.clientY - rect.top) / rect.height) * canvas.height;

    let foundTrip: Trip | null = null;
    trips.forEach((trip) => {
      if (trip.status !== 'In-Transit') return;
      const start = CITIES[trip.routeFrom];
      const end = CITIES[trip.routeTo];
      if (!start || !end) return;

      const baseProgress = trip.progress / 100;
      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const x = start.x + dx * baseProgress;
      const y = start.y + dy * baseProgress;

      const dist = Math.hypot(clickX - x, clickY - y);
      if (dist < 20) {
        foundTrip = trip;
      }
    });

    setSelectedTrip(foundTrip);
  };

  const activeTripDetails = selectedTrip ? {
    trip: selectedTrip,
    vehicle: vehicles.find((v) => v.id === selectedTrip.vehicleId),
    driver: drivers.find((d) => d.id === selectedTrip.driverId)
  } : null;

  // Calculate live latitude & longitude simulation based on progress
  const getLiveCoordinates = () => {
    if (!activeTripDetails) return { lat: 0, lng: 0 };
    const start = CITIES[activeTripDetails.trip.routeFrom];
    const end = CITIES[activeTripDetails.trip.routeTo];
    if (!start || !end) return { lat: 0, lng: 0 };
    
    const progressFactor = activeTripDetails.trip.progress / 100;
    const lat = start.lat + (end.lat - start.lat) * progressFactor;
    const lng = start.lng + (end.lng - start.lng) * progressFactor;
    return { lat: Number(lat.toFixed(4)), lng: Number(lng.toFixed(4)) };
  };

  const coords = getLiveCoordinates();

  return (
    <div className="relative w-full rounded-xl bg-[#08090C] border border-[rgba(0,245,255,0.08)] overflow-hidden shadow-2xl">
      <div className="absolute top-4 left-4 z-10 glass px-3 py-1.5 rounded-lg text-[10px] flex items-center gap-2 font-mono uppercase tracking-wider text-gray-400">
        <span className="h-1.5 w-1.5 rounded-full bg-[#00F5FF] animate-ping"></span>
        <span>Grid Scan: ACTIVE</span>
      </div>

      {activeTripDetails && (
        <div className="absolute bottom-4 right-4 z-10 glass p-4 rounded-xl w-80 text-xs font-mono text-gray-300 border border-[#D88A1D]/20 shadow-2xl animate-in fade-in slide-in-from-bottom-2 duration-300">
          <div className="flex justify-between items-start mb-3 border-b border-[rgba(255,255,255,0.06)] pb-2">
            <div>
              <span className="font-bold text-[#D88A1D]">{activeTripDetails.trip.id}</span>
              <span className="mx-2 text-gray-700">/</span>
              <span className="text-[#00F5FF] font-bold">{activeTripDetails.trip.vehicleId}</span>
            </div>
            <button 
              onClick={() => setSelectedTrip(null)}
              className="text-gray-500 hover:text-white"
            >
              ✕
            </button>
          </div>
          
          <div className="space-y-1.5">
            <div className="flex justify-between">
              <span className="text-gray-500">LAT/LNG:</span>
              <span className="text-white font-bold">{coords.lat}° N, {coords.lng}° W</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">HDG/SPD:</span>
              <span className="text-white font-bold">284° heading / 62 mph</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Route Node:</span>
              <span className="text-white truncate max-w-[150px]">
                {activeTripDetails.trip.routeFrom.split(',')[0]} to {activeTripDetails.trip.routeTo.split(',')[0]}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Cargo Load:</span>
              <span className="text-white truncate max-w-[150px]">{activeTripDetails.trip.cargoType}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Payload:</span>
              <span className="text-white">{activeTripDetails.trip.weight.toLocaleString()} kg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">ETA Vector:</span>
              <span className="text-[#D88A1D] font-bold">{activeTripDetails.trip.eta}</span>
            </div>
          </div>

          <div className="mt-3 pt-2.5 border-t border-[rgba(255,255,255,0.04)]">
            <div className="flex justify-between text-[10px] text-gray-500 mb-1">
              <span>Transit Completeness</span>
              <span>{activeTripDetails.trip.progress}%</span>
            </div>
            <div className="w-full bg-gray-900 h-1 rounded-full overflow-hidden">
              <div 
                className="bg-gradient-to-r from-[#00F5FF] to-[#D88A1D] h-full rounded-full transition-all duration-500"
                style={{ width: `${activeTripDetails.trip.progress}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}

      <canvas
        ref={canvasRef}
        width={1000}
        height={500}
        onClick={handleCanvasClick}
        className="w-full h-auto max-h-[500px] cursor-pointer block"
      />
    </div>
  );
};
