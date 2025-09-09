/**
 * Dashboard Header Component
 * Level 1: Page title and subtitle section (standalone)
 */

import React from 'react';

interface DashboardHeaderProps {
  title: string;
  subtitle: string;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  title,
  subtitle
}) => {
  return (
    <div className="dashboard-header-standalone">
      <h1 className="font-header text-text-primary mb-2">
        {title}
      </h1>
      <div className="font-small text-text-secondary">
        {subtitle}
      </div>
    </div>
  );
};

export default DashboardHeader;