/**
 * Management Controls Component
 * Level 3: Selection, sort, bulk actions, and stats combined
 */

import React, { useState, useRef, useEffect } from 'react';
import Button from '@/components/ui/Button';

export type SortOption = {
  value: string;
  label: string;
};

interface StatItem {
  value: string | number;
  label: string;
}

interface ManagementControlsProps {
  title: string;
  selectedCount: number;
  totalCount: number;
  sortOptions: SortOption[];
  currentSort: string;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onSort: (sortValue: string) => void;
  onBulkDelete: () => void;
  isAllSelected: boolean;
  stats: StatItem[];
}

export const ManagementControls: React.FC<ManagementControlsProps> = ({
  title,
  selectedCount,
  totalCount,
  sortOptions,
  currentSort,
  onSelectAll,
  onDeselectAll,
  onSort,
  onBulkDelete,
  isAllSelected,
  stats
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSortSelect = (sortValue: string) => {
    onSort(sortValue);
    setIsDropdownOpen(false);
  };

  const currentSortLabel = sortOptions.find(opt => opt.value === currentSort)?.label || 'SORT';

  return (
    <div className="management-controls-with-stats">
      {/* Stats and Controls Row */}
      <div className="stats-controls-row">
        {/* Stats Section - Left Side */}
        <div className="stats-section-inline">
          {stats.map((stat, index) => (
            <div key={index} className="inline-stat-item">
              <span className="inline-stat-value">{stat.value}</span>
              <span className="inline-stat-label">{stat.label}</span>
            </div>
          ))}
        </div>
        
        {/* Controls Section - Right Side */}
        <div className="controls-section-inline">
          <Button
            variant="secondary"
            onClick={isAllSelected ? onDeselectAll : onSelectAll}
          >
            {isAllSelected ? 'DESELECT ALL' : 'SELECT ALL'}
          </Button>
          
          {/* Delete button (shown when items are selected) */}
          {selectedCount > 0 && (
            <Button
              variant="danger"
              onClick={onBulkDelete}
            >
              X DELETE SELECTED ({selectedCount})
            </Button>
          )}
          
          {/* Sort Dropdown */}
          <div className="sort-dropdown" ref={dropdownRef}>
            <Button
              variant="secondary"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="sort-button"
            >
              {currentSortLabel} ▼
            </Button>
            
            {isDropdownOpen && (
              <div className="dropdown-menu">
                {sortOptions.map((option) => (
                  <button
                    key={option.value}
                    className={`dropdown-item ${currentSort === option.value ? 'active' : ''}`}
                    onClick={() => handleSortSelect(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManagementControls;