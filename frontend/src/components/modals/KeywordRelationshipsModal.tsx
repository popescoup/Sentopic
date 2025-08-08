/**
 * Keyword Relationships Modal
 * Advanced visualization and exploration of keyword co-occurrences
 * Features network visualization above sortable relationships table
 */

import React, { useState, useMemo } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import type { ProjectResponse, KeywordCooccurrence } from '@/types/api';

interface KeywordRelationshipsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Project data containing co-occurrence information */
  project: ProjectResponse;
  /** Function to call when user wants to explore specific keyword pair */
  onExploreRelationship: (keyword1: string, keyword2: string) => void;
}

type SortOption = 'frequency' | 'alphabetical' | 'posts' | 'comments';

const KeywordRelationshipsModal: React.FC<KeywordRelationshipsModalProps> = ({
  isOpen,
  onClose,
  project,
  onExploreRelationship
}) => {
  // Sorting state
  const [sortBy, setSortBy] = useState<SortOption>('frequency');

  // Sort co-occurrences for table display
  const sortedCooccurrences = useMemo(() => {
    if (!project.cooccurrences) return [];

    const sorted = [...project.cooccurrences];
    
    switch (sortBy) {
      case 'frequency':
        return sorted.sort((a, b) => b.cooccurrence_count - a.cooccurrence_count);
      case 'alphabetical':
        return sorted.sort((a, b) => {
          const nameA = `${a.keyword1} + ${a.keyword2}`;
          const nameB = `${b.keyword1} + ${b.keyword2}`;
          return nameA.localeCompare(nameB);
        });
      case 'posts':
        return sorted.sort((a, b) => b.in_posts - a.in_posts);
      case 'comments':
        return sorted.sort((a, b) => b.in_comments - a.in_comments);
      default:
        return sorted;
    }
  }, [project.cooccurrences, sortBy]);

  // Handle link click in network
  const handleLinkClick = (link: any) => {
    const source = typeof link.source === 'string' ? link.source : link.source?.id || '';
    const target = typeof link.target === 'string' ? link.target : link.target?.id || '';
    onExploreRelationship(source, target);
  };

  // Handle table row click
  const handleTableRowClick = (cooc: KeywordCooccurrence) => {
    onExploreRelationship(cooc.keyword1, cooc.keyword2);
  };

  // Sort options for dropdown
  const sortOptions = [
    { value: 'frequency', label: 'Most Frequent First' },
    { value: 'alphabetical', label: 'Alphabetical' },
    { value: 'posts', label: 'Most in Posts First' },
    { value: 'comments', label: 'Most in Comments First' }
  ];

  // Calculate summary statistics
  const totalPairs = project.cooccurrences?.length || 0;
  const totalCooccurrences = project.cooccurrences?.reduce((sum, cooc) => sum + cooc.cooccurrence_count, 0) || 0;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Keyword Relationships"
      size="xl"
      className="max-h-[90vh]"
    >
      <div className="max-h-[75vh] overflow-y-auto pr-1">
        {/* Enhanced Summary Statistics */}
        <div className="mb-6 p-6 bg-panel rounded-default border border-border-primary">
          <h3 className="font-subsection text-text-primary mb-4">Relationship Overview</h3>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {/* Total Pairs */}
            <div className="text-center">
              <div className="text-2xl font-semibold text-text-primary">{totalPairs}</div>
              <div className="text-text-secondary text-sm">Unique Keyword Pairs</div>
            </div>
            
            {/* Total Co-occurrences */}
            <div className="text-center">
              <div className="text-2xl font-semibold text-text-primary">{totalCooccurrences.toLocaleString()}</div>
              <div className="text-text-secondary text-sm">Total Co-occurrences</div>
            </div>
            
            {/* Average Frequency */}
            <div className="text-center">
              <div className="text-2xl font-semibold text-text-primary">
                {totalPairs > 0 ? Math.round(totalCooccurrences / totalPairs) : 0}
              </div>
              <div className="text-text-secondary text-sm">Average Frequency</div>
            </div>
            
            {/* Posts vs Comments Split */}
            <div className="text-center">
              <div className="text-2xl font-semibold text-text-primary">
                {(() => {
                  const totalInPosts = sortedCooccurrences.reduce((sum, cooc) => sum + cooc.in_posts, 0);
                  const totalInComments = sortedCooccurrences.reduce((sum, cooc) => sum + cooc.in_comments, 0);
                  const total = totalInPosts + totalInComments;
                  if (total === 0) return '0% / 0%';
                  const postsPercent = Math.round((totalInPosts / total) * 100);
                  const commentsPercent = Math.round((totalInComments / total) * 100);
                  return `${postsPercent}% / ${commentsPercent}%`;
                })()}
              </div>
              <div className="text-text-secondary text-sm">Posts / Comments</div>
            </div>
          </div>
          
          {/* Most/Least Connected Keywords */}
          {sortedCooccurrences.length > 0 && (
            <div className="mt-6 pt-4 border-t border-border-secondary">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Most Connected</h4>
                  <div className="flex items-center space-x-2">
                    {(() => {
                      // Count connections for each keyword
                      const keywordConnections = new Map<string, number>();
                      
                      sortedCooccurrences.forEach(cooc => {
                        keywordConnections.set(cooc.keyword1, (keywordConnections.get(cooc.keyword1) || 0) + 1);
                        keywordConnections.set(cooc.keyword2, (keywordConnections.get(cooc.keyword2) || 0) + 1);
                      });
                      
                      // Find most connected keyword
                      let mostConnected = { keyword: '', connections: 0 };
                      keywordConnections.forEach((connections, keyword) => {
                        if (connections > mostConnected.connections) {
                          mostConnected = { keyword, connections };
                        }
                      });
                      
                      return (
                        <>
                          <span className="px-2 py-1 bg-accent text-white rounded text-sm font-medium">
                            {mostConnected.keyword}
                          </span>
                          <span className="text-text-secondary text-sm">
                            {mostConnected.connections} connections
                          </span>
                        </>
                      );
                    })()}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Least Connected</h4>
                  <div className="flex items-center space-x-2">
                    {(() => {
                      // Count connections for each keyword
                      const keywordConnections = new Map<string, number>();
                      
                      sortedCooccurrences.forEach(cooc => {
                        keywordConnections.set(cooc.keyword1, (keywordConnections.get(cooc.keyword1) || 0) + 1);
                        keywordConnections.set(cooc.keyword2, (keywordConnections.get(cooc.keyword2) || 0) + 1);
                      });
                      
                      // Find least connected keyword
                      let leastConnected = { keyword: '', connections: Infinity };
                      keywordConnections.forEach((connections, keyword) => {
                        if (connections < leastConnected.connections) {
                          leastConnected = { keyword, connections };
                        }
                      });
                      
                      return (
                        <>
                          <span className="px-2 py-1 bg-gray-200 text-text-secondary rounded text-sm font-medium">
                            {leastConnected.keyword}
                          </span>
                          <span className="text-text-secondary text-sm">
                            {leastConnected.connections} connections
                          </span>
                        </>
                      );
                    })()}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Relationships Table Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-section-header text-text-primary">
              Relationships List
            </h3>
            
            <div className="flex items-center space-x-3">
              <label className="font-medium text-text-primary">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:border-accent focus:ring-2 focus:ring-accent focus:ring-offset-1 focus:outline-none"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {sortedCooccurrences.length > 0 ? (
            <div className="border border-border-primary rounded-default overflow-hidden">
              <table className="w-full">
                <thead className="bg-panel border-b border-border-primary">
                  <tr>
                    <th className="px-4 py-3 text-left font-subsection text-text-primary">
                      Keyword Pair
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                      Total Count
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                      In Posts
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                      In Comments
                    </th>
                    <th className="px-4 py-3 text-center font-subsection text-text-primary">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-primary">
                  {sortedCooccurrences.map((cooc, index) => (
                    <tr 
                      key={`${cooc.keyword1}-${cooc.keyword2}`}
                      className={`hover:bg-hover-blue transition-colors duration-150 cursor-pointer ${
                        index % 2 === 0 ? 'bg-content' : 'bg-panel'
                      }`}
                      onClick={() => handleTableRowClick(cooc)}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-accent">{cooc.keyword1}</span>
                          <span className="text-text-tertiary">+</span>
                          <span className="font-medium text-accent">{cooc.keyword2}</span>
                        </div>
                      </td>
                      
                      <td className="px-4 py-3 text-right">
                        <span className="font-technical text-text-primary font-semibold">
                          {cooc.cooccurrence_count.toLocaleString()}
                        </span>
                      </td>
                      
                      <td className="px-4 py-3 text-right">
                        <span className="font-technical text-text-secondary">
                          {cooc.in_posts.toLocaleString()}
                        </span>
                      </td>
                      
                      <td className="px-4 py-3 text-right">
                        <span className="font-technical text-text-secondary">
                          {cooc.in_comments.toLocaleString()}
                        </span>
                      </td>
                      
                      <td className="px-4 py-3 text-center">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTableRowClick(cooc);
                          }}
                        >
                          Explore
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 border border-border-primary rounded-default bg-content">
              <div className="text-text-tertiary mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h4 className="font-subsection text-text-primary mb-2">
                No Relationships Available
              </h4>
              <p className="font-body text-text-secondary max-w-md mx-auto">
                Relationship data is not available for this project. This may be because the analysis is still running or has not been completed yet.
              </p>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default KeywordRelationshipsModal;