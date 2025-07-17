/**
 * ProjectCardSkeleton Component
 * Professional loading skeleton for project cards
 * 
 * Maintains layout stability during loading with animated skeleton elements
 */

import React from 'react';
import Card from '@/components/ui/Card';

interface ProjectCardSkeletonProps {
  /** Number of skeleton cards to display */
  count?: number;
}

export const ProjectCardSkeleton: React.FC<ProjectCardSkeletonProps> = ({ count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} className="animate-pulse">
          {/* Project Header Skeleton */}
          <div className="mb-4">
            <div className="flex items-start justify-between mb-2">
              {/* Project name skeleton */}
              <div className="h-5 bg-panel rounded w-3/4"></div>
              {/* Status badge skeleton */}
              <div className="h-6 bg-panel rounded-input w-16"></div>
            </div>
            {/* Created date and collections skeleton */}
            <div className="h-3 bg-panel rounded w-2/3"></div>
          </div>
          
          {/* AI Summary Skeleton */}
          <div className="mb-4 space-y-2">
            <div className="h-4 bg-panel rounded w-full"></div>
            <div className="h-4 bg-panel rounded w-4/5"></div>
          </div>
          
          {/* Project Stats Skeleton */}
          <div className="flex items-center justify-between text-small mb-4">
            <div className="flex space-x-4">
              <div className="h-3 bg-panel rounded w-16"></div>
              <div className="h-3 bg-panel rounded w-20"></div>
            </div>
          </div>

          {/* Keywords Skeleton */}
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              <div className="h-6 bg-panel rounded-input w-16"></div>
              <div className="h-6 bg-panel rounded-input w-20"></div>
              <div className="h-6 bg-panel rounded-input w-12"></div>
            </div>
          </div>

          {/* Action Buttons Skeleton */}
          <div className="flex space-x-2">
            <div className="h-8 bg-panel rounded-input flex-1"></div>
            <div className="h-8 bg-panel rounded-input w-8"></div>
          </div>
        </Card>
      ))}
    </>
  );
};

export default ProjectCardSkeleton;