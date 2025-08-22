/**
 * Collection Manager Page
 * CRUD interface for managing Reddit data collections
 */

import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ConfirmModal } from '@/components/ui/Modal';
import { CollectionCreationModal } from '@/components/collections';
import { useCollections, useDeleteCollection } from '@/hooks/useApi';
import { getErrorMessage } from '@/api/client';

const CollectionManager: React.FC = () => {
  const { data: collectionsData, isLoading, error, refetch } = useCollections();
  const deleteCollectionMutation = useDeleteCollection();
  
  // State for collection creation modal
  const [showCreationModal, setShowCreationModal] = useState(false);
  
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
  if (isLoading) {
    return (
      <MainLayout title="Collection Manager">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto mb-4"></div>
            <p className="font-body text-text-secondary">Loading collections...</p>
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
            <Button onClick={() => refetch()} variant="outline">
              Try Again
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

  const collections = collectionsData?.collections || [];
  const totalCount = collectionsData?.total_count || 0;

  return (
    <MainLayout title="Collection Manager">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="font-page-title text-text-primary mb-3">
          Collection Manager
        </h1>
        <p className="font-body text-text-secondary max-w-2xl">
          Manage your Reddit data collections. Create new collections from subreddits, 
          monitor collection progress, and organize your data sources for analysis projects.
        </p>
      </div>

      {/* Action Bar */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button 
            variant="primary"
            onClick={() => setShowCreationModal(true)}
          >
            + New Collection
          </Button>
          {selectedCollections.size > 0 && (
            <Button 
              variant="danger" 
              onClick={handleBulkDelete}
              startIcon={
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              }
            >
              Delete Selected ({selectedCollections.size})
            </Button>
          )}
          {collections.length > 0 && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => handleSelectAll(selectedCollections.size !== collections.length)}
            >
              {selectedCollections.size === collections.length ? 'Deselect All' : 'Select All'}
            </Button>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="font-body text-text-secondary">
            {selectedCollections.size > 0 
              ? `${selectedCollections.size} selected • `
              : ''
            }
            {totalCount} {totalCount === 1 ? 'collection' : 'collections'}
          </span>
        </div>
      </div>

      {/* Collections Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {collections.length === 0 ? (
          <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
            <div className="mb-4 text-4xl">📊</div>
            <h3 className="font-subsection text-text-primary mb-2">No collections yet</h3>
            <p className="font-body text-text-secondary mb-4 max-w-md">
              Start by creating your first Reddit data collection to analyze discussions and sentiment.
            </p>
            <Button variant="primary">
              + Create Your First Collection
            </Button>
          </div>
        ) : (
          collections.map((collection) => {
            // Helper function to get status styling
            const getStatusStyling = (status: string) => {
              switch (status) {
                case 'completed':
                  return {
                    className: 'text-success bg-green-100',
                    label: 'Completed'
                  };
                case 'running':
                  return {
                    className: 'text-accent bg-blue-100', 
                    label: 'Running'
                  };
                case 'failed':
                  return {
                    className: 'text-danger bg-red-100',
                    label: 'Failed'
                  };
                default:
                  return {
                    className: 'text-text-tertiary bg-gray-100',
                    label: 'Unknown'
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
              const sortMethod = collection.sort_method.charAt(0).toUpperCase() + collection.sort_method.slice(1);
              const timePeriod = collection.time_period ? ` (${collection.time_period})` : '';
              const postsText = `${collection.posts_requested} posts`;
              const createdText = formatDate(collection.created_at);
              
              return `${sortMethod}${timePeriod} • ${postsText} • Created ${createdText}`;
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
                      <input
                        type="checkbox"
                        checked={selectedCollections.has(collection.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleSelectCollection(collection.id, e.target.checked);
                        }}
                        className="h-4 w-4 text-accent focus:ring-accent border-border-secondary rounded"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <h3 className="font-subsection text-text-primary">
                        r/{collection.subreddit}
                      </h3>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteCollection(collection);
                      }}
                      className="text-text-secondary hover:text-danger -mr-2 -mt-1"
                      aria-label="Delete collection"
                      disabled={deleteCollectionMutation.isPending && deleteModal.collection?.id === collection.id}
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
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

{/* Collection Creation Modal */}
<CollectionCreationModal
  isOpen={showCreationModal}
  onClose={() => setShowCreationModal(false)}
  onSuccess={() => {
    setShowCreationModal(false);
    refetch(); // Refresh the collections list
  }}
/>

{/* Delete Confirmation Modal */}
<ConfirmModal
  isOpen={deleteModal.isOpen}
  onClose={closeDeleteModal}
  onConfirm={confirmDeleteCollection}
  title="Delete Collection"
  message={
    deleteModal.collections
      ? `Are you sure you want to delete ${deleteModal.collections.length} collections from: ${deleteModal.collections.map(c => `r/${c.subreddit}`).join(', ')}? Deleting these collections may leave orphaned data in projects and will permanently remove all collected posts and comments.`
      : deleteModal.collection
      ? `Are you sure you want to delete the collection from r/${deleteModal.collection.subreddit}? Deleting this collection may leave orphaned data in projects and will permanently remove all collected posts and comments.`
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