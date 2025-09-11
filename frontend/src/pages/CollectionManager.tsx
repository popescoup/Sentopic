/**
 * Collection Manager Page
 * CRUD interface for managing Reddit data collections
 */

import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ConfirmModal } from '@/components/ui/Modal';
import { useNavigate } from 'react-router-dom';
import { useCollections, useDeleteCollection } from '@/hooks/useApi';
import { useRedditStatus } from '@/hooks/useRedditStatus';
import { getErrorMessage } from '@/api/client';
import LoadingSpinner from '@/components/layout/LoadingSpinner';
import { DashboardHeader, ManagementControls, type SortOption } from '@/components/dashboard';
import { useDashboardSort } from '@/hooks/useDashboardSort';

const CollectionManager: React.FC = () => {
  const { data: collectionsData, isLoading, error, refetch } = useCollections();
  const { isRedditConfigured, isLoading: redditStatusLoading } = useRedditStatus();
  const deleteCollectionMutation = useDeleteCollection();
  const navigate = useNavigate();

  const collections = collectionsData?.collections || [];
  const totalCount = collectionsData?.total_count || 0;

  // Sort functionality - MUST be called before any conditional returns
  const { sortedItems: sortedCollections, handleSort, getCurrentSortValue } = useDashboardSort(
    collections,
    'date',
    'desc'
  );

  // Sort options for collections
  const collectionSortOptions: SortOption[] = [
    { value: 'subreddit-asc', label: 'NAME (A-Z)' },
    { value: 'subreddit-desc', label: 'NAME (Z-A)' },
    { value: 'date-desc', label: 'NEWEST FIRST' },
    { value: 'date-asc', label: 'OLDEST FIRST' },
    { value: 'posts-desc', label: 'MOST POSTS' },
    { value: 'posts-asc', label: 'LEAST POSTS' },
  ];

  // Calculate stats
  const totalPosts = collections.reduce((sum, collection) => sum + collection.posts_collected, 0);
  const totalComments = collections.reduce((sum, collection) => sum + collection.comments_collected, 0);

  const dashboardStats = [
    { value: collections.length, label: 'Total Collections' },
    { value: totalPosts.toLocaleString(), label: 'Total Posts' },
    { value: totalComments.toLocaleString(), label: 'Total Comments' },
  ];

  // State for delete confirmation modal
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    collection: any | null;
    collections?: any[] | null;
  }>({
    isOpen: false,
    collection: null,
    collections: null
  });

  // State for bulk selection
  const [selectedCollections, setSelectedCollections] = useState<Set<string>>(new Set());

  // Handle delete collection flow
  const handleDeleteCollection = (collection: any) => {
    setDeleteModal({
      isOpen: true,
      collection,
      collections: null
    });
  };

  const confirmDeleteCollection = async () => {
    if (!deleteModal.collection && !deleteModal.collections) return;

    try {
      if (deleteModal.collections) {
        // Bulk delete
        for (const collection of deleteModal.collections) {
          await deleteCollectionMutation.mutateAsync(collection.id);
        }
        setSelectedCollections(new Set()); // Clear selection
      } else if (deleteModal.collection) {
        // Single delete
        await deleteCollectionMutation.mutateAsync(deleteModal.collection.id);
      }
      
      setDeleteModal({ isOpen: false, collection: null, collections: null });
      refetch();
    } catch (error) {
      console.error('Failed to delete collection(s):', error);
    }
  };

  const closeDeleteModal = () => {
    setDeleteModal({ isOpen: false, collection: null, collections: null });
  };

  // Handle loading state
  if (isLoading || redditStatusLoading) {
    return (
      <MainLayout title="Collection Manager">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
          <LoadingSpinner size="lg" message="Loading Collections..." />
          </div>
        </div>
      </MainLayout>
    );
  }

  // Handle error state
  if (error) {
    return (
      <MainLayout title="Collection Manager">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <p className="font-body text-danger mb-4">Error loading collections: {getErrorMessage(error)}</p>
            <Button onClick={() => refetch()} variant="secondary">
              TRY AGAIN
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Handle bulk selection
  const handleSelectCollection = (collectionId: string, isSelected: boolean) => {
    const newSelected = new Set(selectedCollections);
    if (isSelected) {
      newSelected.add(collectionId);
    } else {
      newSelected.delete(collectionId);
    }
    setSelectedCollections(newSelected);
  };

  const handleSelectAll = (isSelected: boolean) => {
    if (isSelected) {
      const allIds = new Set(collections.map(c => c.id));
      setSelectedCollections(allIds);
    } else {
      setSelectedCollections(new Set());
    }
  };

  const handleBulkDelete = () => {
    if (selectedCollections.size === 0) return;
    
    const collectionsToDelete = collections.filter(c => selectedCollections.has(c.id));
    setDeleteModal({
      isOpen: true,
      collection: null,
      collections: collectionsToDelete
    });
  };

  return (
    <MainLayout title="Collection Manager" className="dashboard-spacing">
      {/* Level 1: Page Header */}
      <DashboardHeader 
        title="Collection Manager"
        subtitle="Reddit Data Collection Management Interface"
      />
  
      {/* Level 2: Management Controls with Stats */}
      {collections.length > 0 && (
        <ManagementControls
          title="Collection Management"
          selectedCount={selectedCollections.size}
          totalCount={collections.length}
          sortOptions={collectionSortOptions}
          currentSort={getCurrentSortValue()}
          onSelectAll={() => handleSelectAll(true)}
          onDeselectAll={() => handleSelectAll(false)}
          onSort={handleSort}
          onBulkDelete={handleBulkDelete}
          isAllSelected={selectedCollections.size === collections.length && collections.length > 0}
          stats={dashboardStats}
        />
      )}
  
      {/* Level 3: Collections Grid */}
      <div className="dashboard-level-4">
        <h4 className="font-large text-text-primary mb-4">
          Collection Repository
        </h4>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {/* New Collection Card - Terminal Style */}
        <div 
          className={`bg-content border-2 border-dashed transition-all duration-100 flex flex-col items-center justify-center font-terminal ${
            isRedditConfigured 
              ? 'border-border text-center cursor-pointer hover:border-border-dark hover:bg-panel' 
              : 'border-border-secondary text-center cursor-not-allowed opacity-60'
          }`}
          style={{ minHeight: '120px', padding: '20px' }}
          onClick={isRedditConfigured ? () => navigate('/collections/new') : undefined}
        >
          <div className="font-title text-text-tertiary mb-2">
            [+]
          </div>
          <div className="font-body text-text-primary mb-1 tracking-terminal-wide">
            NEW COLLECTION
          </div>
          <div className="font-caption text-text-secondary tracking-terminal-wide">
            {isRedditConfigured ? 'CREATE DATA SOURCE' : 'CONFIGURE API TO GET STARTED'}
          </div>
        </div>

        {collections.length === 0 ? (
          <div className="col-span-2 text-center py-8">
          <h3 className="font-subsection text-text-primary mb-2 tracking-terminal-wide">NO COLLECTIONS YET</h3>
          <p className="font-body text-text-secondary tracking-terminal-wide">
            CLICK THE NEW COLLECTION CARD TO START
          </p>
        </div>
        ) : (
          sortedCollections.map((collection) => {
            // Helper function to get status styling
            const getStatusStyling = (status: string) => {
              switch (status) {
                case 'completed':
                  return {
                    className: 'text-success bg-green-100',
                    label: 'COMPLETED'
                  };
                case 'running':
                  return {
                    className: 'text-accent bg-blue-100', 
                    label: 'RUNNING'
                  };
                case 'failed':
                  return {
                    className: 'text-danger bg-red-100',
                    label: 'FAILED'
                  };
                default:
                  return {
                    className: 'text-text-tertiary bg-gray-100',
                    label: 'UNKNOWN'
                  };
              }
            };

            // Helper function to format date
            const formatDate = (dateStr: string) => {
              const date = new Date(dateStr);
              const now = new Date();
              const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
              
              if (diffInHours < 1) {
                return 'Just now';
              } else if (diffInHours < 24) {
                return `${diffInHours} hour${diffInHours === 1 ? '' : 's'} ago`;
              } else {
                const diffInDays = Math.floor(diffInHours / 24);
                return `${diffInDays} day${diffInDays === 1 ? '' : 's'} ago`;
              }
            };

            // Helper function to create collection description
            const getCollectionDescription = (collection: any) => {
              const sortMethod = collection.sort_method.toUpperCase();
              const timePeriod = collection.time_period ? ` (${collection.time_period.toUpperCase()})` : '';
              const postsText = `${collection.posts_requested} POSTS`;
              const createdText = formatDate(collection.created_at).toUpperCase();
              
              return `${sortMethod}${timePeriod} • ${postsText} • CREATED ${createdText}`;
            };

            const statusStyling = getStatusStyling(collection.status);
            const isRunning = collection.status === 'running';
            
            return (
              <Card 
                key={collection.id} 
                hover 
                className={isRunning ? 'border-2 border-accent bg-blue-50' : ''}
              >
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                    <div 
                      className="h-4 w-4 border border-border-secondary bg-content cursor-pointer flex items-center justify-center"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectCollection(collection.id, !selectedCollections.has(collection.id));
                      }}
                    >
                      {selectedCollections.has(collection.id) && (
                        <div className="h-2 w-2 bg-accent"></div>
                      )}
                    </div>
                      <h3 className="font-subsection text-text-primary">
                        r/{collection.subreddit}
                      </h3>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteCollection(collection);
                      }}
                      className="text-text-secondary hover:text-danger -mr-0.3 -mt-1 font-terminal text-lg font-bold transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                      aria-label="Delete collection"
                      disabled={deleteCollectionMutation.isPending && deleteModal.collection?.id === collection.id}
                    >
                      ×
                    </button>
                  </div>
                  <p className="font-small text-text-tertiary">
                    {getCollectionDescription(collection)}
                  </p>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between font-body text-text-secondary">
                    <span>Posts collected:</span>
                    <span className="font-technical">
                      {collection.posts_collected}/{collection.posts_requested}
                    </span>
                  </div>
                  <div className="flex justify-between font-body text-text-secondary">
                    <span>Comments collected:</span>
                    <span className="font-technical">{collection.comments_collected}</span>
                  </div>
                </div>
                
                {isRunning && (
                  <div className="mb-4">
                    <div className="flex justify-between font-body text-text-secondary mb-2">
                      <span>Progress:</span>
                      <span className="font-technical">
                        {Math.round((collection.posts_collected / collection.posts_requested) * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-border-primary rounded-full h-2">
                      <div 
                        className="bg-accent h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${Math.round((collection.posts_collected / collection.posts_requested) * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                {/* Loading Overlay for Delete */}
                {deleteCollectionMutation.isPending && deleteModal.collection?.id === collection.id && (
                  <div className="absolute inset-0 bg-content bg-opacity-75 flex items-center justify-center rounded-default">
                    <div className="flex items-center space-x-2">
                      <svg className="animate-spin h-4 w-4 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span className="font-small text-text-secondary">Deleting...</span>
                    </div>
                  </div>
                )}
              </Card>
            );
          })
        )}
      </div>
      </div>

    {/* Delete Confirmation Modal */}
<ConfirmModal
  isOpen={deleteModal.isOpen}
  onClose={closeDeleteModal}
  onConfirm={confirmDeleteCollection}
  title="Delete Collection"
  message={
    deleteModal.collections
      ? `Are you sure you want to delete ${deleteModal.collections.length} collections from: ${deleteModal.collections.map(c => `r/${c.subreddit}`).join(', ')}? Deleting these collections may negatively effect projects by creating orphaned data and will permanently remove all collected posts and comments.`
      : deleteModal.collection
      ? `Are you sure you want to delete the collection from r/${deleteModal.collection.subreddit}? Deleting these collections may negatively effect projects by creating orphaned data and will permanently remove all collected posts and comments.`
      : ''
  }
  confirmText={deleteModal.collections ? `Delete ${deleteModal.collections.length} Collections` : "Delete Collection"}
  cancelText="Cancel"
  variant="danger"
/>
</MainLayout>
);
};

export default CollectionManager;