/**
 * Dashboard Sort Hook
 * Reusable sorting logic for dashboard items
 */

import { useState, useMemo } from 'react';

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  key: string;
  direction: SortDirection;
}

export function useDashboardSort<T>(
    items: T[],
    defaultSortKey: string = 'name',
    defaultDirection: SortDirection = 'asc'
  ) {
    const [sortConfig, setSortConfig] = useState<SortConfig>({
      key: defaultSortKey,
      direction: defaultDirection
    });

  const sortedItems = useMemo(() => {
    if (!items || items.length === 0) return [];

    const sortableItems = [...items];
    
    sortableItems.sort((a: any, b: any) => {
      const aValue = getSortValue(a, sortConfig.key);
      const bValue = getSortValue(b, sortConfig.key);
      
      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sortableItems;
  }, [items, sortConfig]);

  const handleSort = (sortValue: string) => {
    // Parse sort value (e.g., "name-asc", "date-desc")
    const [key, direction] = sortValue.split('-') as [string, SortDirection];
    
    setSortConfig({ key, direction });
  };

  const getCurrentSortValue = () => {
    return `${sortConfig.key}-${sortConfig.direction}`;
  };

  return {
    sortedItems,
    handleSort,
    getCurrentSortValue,
    sortConfig
  };
}

// Helper function to get sortable value from object
function getSortValue(item: any, key: string): any {
    switch (key) {
      case 'name':
        return item.name?.toLowerCase() || '';
      case 'date':
        return new Date(item.created_at || 0).getTime();
      case 'mentions':
        return item.stats?.total_mentions || 0;
      case 'sentiment':
        return item.stats?.avg_sentiment || 0;
      case 'posts':
        return item.posts_collected || 0;
      case 'subreddit':
        return item.subreddit?.toLowerCase() || '';
      default:
        return item[key] || '';
    }
  }