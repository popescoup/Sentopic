/**
 * Collection Manager Page
 * CRUD interface for managing Reddit data collections
 * 
 * Phase 1: Placeholder with professional styling
 * Phase 6: Full implementation with collection creation and management
 */

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

const CollectionManager: React.FC = () => {
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
          <Button variant="primary">
            + New Collection
          </Button>
          <Button variant="secondary">
            Batch Operations
          </Button>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="font-body text-text-secondary">
            3 collections
          </span>
        </div>
      </div>

      {/* Collections Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {/* Example Collection Cards */}
        <Card hover>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-subsection text-text-primary">
                r/iphone
              </h3>
              <span className="text-success font-small bg-green-100 px-2 py-1 rounded-input">
                Completed
              </span>
            </div>
            <p className="font-small text-text-tertiary">
              Hot • 50 posts • Created 2 days ago
            </p>
          </div>
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between font-body text-text-secondary">
              <span>Posts collected:</span>
              <span className="font-technical">47/50</span>
            </div>
            <div className="flex justify-between font-body text-text-secondary">
              <span>Comments collected:</span>
              <span className="font-technical">312</span>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" className="flex-1">
              View Details
            </Button>
            <Button variant="ghost" size="sm">
              ⋯
            </Button>
          </div>
        </Card>

        <Card hover>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-subsection text-text-primary">
                r/apple
              </h3>
              <span className="text-success font-small bg-green-100 px-2 py-1 rounded-input">
                Completed
              </span>
            </div>
            <p className="font-small text-text-tertiary">
              Top (Week) • 25 posts • Created 1 week ago
            </p>
          </div>
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between font-body text-text-secondary">
              <span>Posts collected:</span>
              <span className="font-technical">25/25</span>
            </div>
            <div className="flex justify-between font-body text-text-secondary">
              <span>Comments collected:</span>
              <span className="font-technical">189</span>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" className="flex-1">
              View Details
            </Button>
            <Button variant="ghost" size="sm">
              ⋯
            </Button>
          </div>
        </Card>

        <Card hover className="border-2 border-accent bg-blue-50">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-subsection text-text-primary">
                r/electricvehicles
              </h3>
              <span className="text-accent font-small bg-blue-100 px-2 py-1 rounded-input">
                Running
              </span>
            </div>
            <p className="font-small text-text-tertiary">
              Hot • 30 posts • Started 5 minutes ago
            </p>
          </div>
          
          <div className="mb-4">
            <div className="flex justify-between font-body text-text-secondary mb-2">
              <span>Progress:</span>
              <span className="font-technical">67%</span>
            </div>
            <div className="w-full bg-border-primary rounded-full h-2">
              <div 
                className="bg-accent h-2 rounded-full transition-all duration-300" 
                style={{ width: '67%' }}
              ></div>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" className="flex-1">
              View Progress
            </Button>
            <Button variant="ghost" size="sm" className="text-danger">
              Stop
            </Button>
          </div>
        </Card>
      </div>

      {/* Collection Details Table Preview */}
      <Card>
        <div className="mb-4">
          <h2 className="font-section-header text-text-primary mb-2">
            Collection Details
          </h2>
          <p className="font-body text-text-secondary">
            Detailed collection management interface will be implemented in Phase 6.
          </p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border-primary">
                <th className="text-left py-3 pr-4 font-subsection text-text-primary">
                  <input type="checkbox" className="mr-3" />
                  Subreddit
                </th>
                <th className="text-left py-3 px-4 font-subsection text-text-primary">Status</th>
                <th className="text-left py-3 px-4 font-subsection text-text-primary">Posts</th>
                <th className="text-left py-3 px-4 font-subsection text-text-primary">Comments</th>
                <th className="text-left py-3 px-4 font-subsection text-text-primary">Created</th>
                <th className="text-left py-3 pl-4 font-subsection text-text-primary">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border-primary hover:bg-panel">
                <td className="py-3 pr-4">
                  <div className="flex items-center">
                    <input type="checkbox" className="mr-3" />
                    <span className="font-body text-text-primary">r/iphone</span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className="text-success font-small bg-green-100 px-2 py-1 rounded-input">
                    Completed
                  </span>
                </td>
                <td className="py-3 px-4 font-technical text-text-secondary">47/50</td>
                <td className="py-3 px-4 font-technical text-text-secondary">312</td>
                <td className="py-3 px-4 font-body text-text-secondary">2 days ago</td>
                <td className="py-3 pl-4">
                  <Button variant="ghost" size="sm">⋯</Button>
                </td>
              </tr>
              <tr className="border-b border-border-primary hover:bg-panel">
                <td className="py-3 pr-4">
                  <div className="flex items-center">
                    <input type="checkbox" className="mr-3" />
                    <span className="font-body text-text-primary">r/apple</span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className="text-success font-small bg-green-100 px-2 py-1 rounded-input">
                    Completed
                  </span>
                </td>
                <td className="py-3 px-4 font-technical text-text-secondary">25/25</td>
                <td className="py-3 px-4 font-technical text-text-secondary">189</td>
                <td className="py-3 px-4 font-body text-text-secondary">1 week ago</td>
                <td className="py-3 pl-4">
                  <Button variant="ghost" size="sm">⋯</Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div className="mt-4 pt-4 border-t border-border-primary flex justify-between items-center">
          <span className="font-body text-text-secondary">
            3 collections selected
          </span>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">Export</Button>
            <Button variant="danger" size="sm">Delete Selected</Button>
          </div>
        </div>
      </Card>

      {/* Phase Information */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary">
        <h2 className="font-section-header text-text-primary mb-3">
          Collection Manager Implementation Roadmap
        </h2>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Phase 6: Full Implementation
            </h3>
            <ul className="font-body text-text-secondary space-y-1">
              <li>• Collection creation wizard with batch support</li>
              <li>• Real-time progress tracking</li>
              <li>• Advanced filtering and search</li>
              <li>• Bulk operations (delete, export)</li>
              <li>• Collection usage tracking</li>
              <li>• Integration with project creation</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Backend Integration
            </h3>
            <ul className="font-body text-text-secondary space-y-1">
              <li>• POST /collections (batch creation)</li>
              <li>• GET /collections (list all)</li>
              <li>• GET /collections/[batch_id]/status</li>
              <li>• DELETE /collections/[id]</li>
              <li>• Collection parameters validation</li>
              <li>• Progress monitoring and status updates</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default CollectionManager;