/**
 * Collection Selector Component
 * Multi-select interface for choosing Reddit data collections
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCollections } from '@/hooks/useApi';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import LoadingSpinner from '@/components/layout/LoadingSpinner';
import type { CollectionResponse } from '@/types/api';

export interface CollectionSelectorProps {
  /** Currently selected collection IDs */
  selectedCollections: string[];
  /** Callback when selection changes */
  onSelectionChange: (collectionIds: string[]) => void;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Error message to display */
  error?: string;
  /** Additional CSS classes */
  className?: string;
  /** Custom handler for manage collections button */
  onManageCollectionsClick?: () => void;
}

export const CollectionSelector: React.FC<CollectionSelectorProps> = ({
  selectedCollections,
  onSelectionChange,
  disabled = false,
  error,
  className = '',
  onManageCollectionsClick
}) => {
  const { data: collectionsData, isLoading, error: fetchError } = useCollections();

  const collections = collectionsData?.collections || [];
  const availableCollections = collections.filter(c => c.status === 'completed');

  // Compute selectAll state based on actual selection
  const selectAll = availableCollections.length > 0 && 
                   selectedCollections.length === availableCollections.length &&
                   availableCollections.every(c => selectedCollections.includes(c.id));

  // Handle individual collection selection
  const handleCollectionToggle = (collectionId: string) => {
    console.log('Toggling collection:', collectionId); // Debug log
    
    if (selectedCollections.includes(collectionId)) {
      const newSelection = selectedCollections.filter(id => id !== collectionId);
      console.log('Removing collection. New selection:', newSelection); // Debug log
      onSelectionChange(newSelection);
    } else {
      const newSelection = [...selectedCollections, collectionId];
      console.log('Adding collection. New selection:', newSelection); // Debug log
      onSelectionChange(newSelection);
    }
  };

  // Handle select all toggle
  const handleSelectAllToggle = () => {
    if (selectAll) {
      console.log('Deselecting all collections'); // Debug log
      onSelectionChange([]);
    } else {
      console.log('Selecting all collections'); // Debug log
      onSelectionChange(availableCollections.map(c => c.id));
    }
  };

  // Format collection metadata
  const formatCollectionMeta = (collection: CollectionResponse) => {
    const date = new Date(collection.created_at).toLocaleDateString();
    const postsText = `${collection.posts_collected.toLocaleString()} posts`;
    const commentsText = `${collection.comments_collected.toLocaleString()} comments`;
    
    return {
      date,
      postsText,
      commentsText,
      totalItems: collection.posts_collected + collection.comments_collected
    };
  };

  // Get status styling
  const getStatusStyling = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-success border-success';
      case 'running':
        return 'bg-blue-100 text-accent border-accent';
      case 'failed':
        return 'bg-red-100 text-danger border-danger';
      default:
        return 'bg-gray-100 text-text-tertiary border-border-secondary';
    }
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <LoadingSpinner size="lg" />
        <span className="ml-3 font-body text-text-secondary">
          Loading collections...
        </span>
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className={className}>
        <Card className="border-danger bg-red-50 text-center py-8">
          <div className="text-danger mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-subsection text-danger mb-2">
            Failed to Load Collections
          </h3>
          <p className="font-body text-text-secondary mb-4">
            Unable to fetch available collections. Please try again.
          </p>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  if (availableCollections.length === 0) {
    return (
      <div className={className}>
        <Card className="text-center py-8">
          <div className="text-text-tertiary mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="font-subsection text-text-primary mb-2">
            No Collections Available
          </h3>
          <p className="font-body text-text-secondary mb-4">
            You need to create data collections before setting up a project.
          </p>
          {onManageCollectionsClick ? (
            <Button 
              variant="secondary" 
              size="sm"
              onClick={onManageCollectionsClick}
            >
              MANAGE COLLECTIONS
            </Button>
          ) : (
            <Link to="/collections">
              <Button variant="secondary" size="sm">
                MANAGE COLLECTIONS
              </Button>
            </Link>
          )}
        </Card>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header with Select All */}
      <div className="flex items-center justify-between mb-4">
      <div>
          <h3 className="font-subsection text-text-primary">
            {availableCollections.length} Available
          </h3>
        </div>
        
        <div className="flex items-center space-x-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={handleSelectAllToggle}
          disabled={disabled}
        >
          {selectAll ? 'DESELECT ALL' : 'SELECT ALL'}
        </Button>
          
          {onManageCollectionsClick ? (
            <Button 
            variant="secondary" 
            size="sm"
            onClick={onManageCollectionsClick}
          >
            MANAGE COLLECTIONS
          </Button>
          ) : (
            <Link to="/collections">
              <Button variant="secondary" size="sm">
                MANAGE COLLECTIONS
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Selection Summary */}
      {selectedCollections.length > 0 && (
        <div className="mb-4 p-3 bg-hover-blue rounded-input border border-accent">
          <div className="flex items-center justify-between">
            <span className="font-body text-text-primary">
              {selectedCollections.length} collection{selectedCollections.length !== 1 ? 's' : ''} selected
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onSelectionChange([])}
              disabled={disabled}
              className="text-text-tertiary hover:text-danger"
            >
              CLEAR SELECTION
            </Button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-danger rounded-input">
          <p className="font-body text-danger">{error}</p>
        </div>
      )}

      {/* Collections Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {availableCollections.map((collection) => {
          const isSelected = selectedCollections.includes(collection.id);
          const meta = formatCollectionMeta(collection);
          
          return (
            <Card
              key={collection.id}
              clickable={!disabled}
              hover={!disabled}
              className={`
                transition-all duration-150
                ${isSelected 
                  ? 'border-accent bg-hover-blue shadow-card-hover' 
                  : 'border-border-primary hover:border-border-emphasis'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Card clicked:', collection.id, 'disabled:', disabled); // Debug log
                if (!disabled) {
                  handleCollectionToggle(collection.id);
                }
              }}
            >
              {/* Collection Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h4 className="font-subsection text-text-primary truncate">
                    r/{collection.subreddit}
                  </h4>
                  <p className="font-body text-text-secondary capitalize">
                    {collection.sort_method}
                    {collection.time_period && ` • ${collection.time_period}`}
                  </p>
                </div>
                
                {/* Selection Checkbox */}
                <div className={`
                  w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-150
                  ${isSelected 
                    ? 'bg-accent border-accent' 
                    : 'border-border-secondary hover:border-accent'
                  }
                `}>
                  {isSelected && (
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </div>

              {/* Collection Stats */}
              <div className="space-y-2 mb-3">
                <div className="flex justify-between items-center">
                  <span className="font-body text-text-secondary">Posts:</span>
                  <span className="font-technical text-text-primary">{meta.postsText}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-body text-text-secondary">Comments:</span>
                  <span className="font-technical text-text-primary">{meta.commentsText}</span>
                </div>
              </div>

              {/* Collection Footer */}
              <div className="flex items-center justify-end pt-3 border-t border-border-primary">
                <span className="font-body text-text-tertiary text-sm">
                  {meta.date}
                </span>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default CollectionSelector;