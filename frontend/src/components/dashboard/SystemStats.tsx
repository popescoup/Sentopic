/**
 * System Stats Component
 * Level 2: Individual statistics display containers
 */

import React from 'react';

interface StatItem {
  value: string | number;
  label: string;
}

interface SystemStatsProps {
  stats: StatItem[];
}

export const SystemStats: React.FC<SystemStatsProps> = ({
  stats
}) => {
  return (
    <div className="system-stats-grid">
      {stats.map((stat, index) => (
        <div key={index} className="individual-stat-container">
          <div className="stat-value">{stat.value}</div>
          <div className="stat-label">{stat.label}</div>
        </div>
      ))}
    </div>
  );
};

export default SystemStats;