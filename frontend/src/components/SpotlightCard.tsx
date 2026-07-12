import React, { useRef, useState } from 'react';

interface SpotlightCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  glowColor?: string;
}

export const SpotlightCard: React.FC<SpotlightCardProps> = ({
  children,
  className = '',
  glowColor = 'rgba(216, 138, 29, 0.15)', // Default gold accent
  ...props
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setCoords({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative overflow-hidden rounded-xl border border-[rgba(255,255,255,0.06)] bg-[#161A22] p-6 transition-all duration-300 ${className}`}
      {...props}
    >
      {isHovered && (
        <div
          className="pointer-events-none absolute inset-0 transition-opacity duration-300"
          style={{
            background: `radial-gradient(400px circle at ${coords.x}px ${coords.y}px, ${glowColor}, transparent 80%)`,
          }}
        />
      )}
      <div className="relative z-10">{children}</div>
    </div>
  );
};
