/**
 * Network Data Transformation Utilities
 * Transform co-occurrence data into D3-compatible network format
 * Handles node creation, link weighting, and network statistics
 */

import type { KeywordCooccurrence, NetworkData, NetworkNode, NetworkLink } from '@/types/api';

/**
 * Transform keyword co-occurrence data into D3 network format
 * @param cooccurrences Array of keyword co-occurrence relationships
 * @returns NetworkData with nodes and links for D3 visualization
 */
export const transformCooccurrenceToNetwork = (
  cooccurrences: KeywordCooccurrence[]
): NetworkData => {
  if (!cooccurrences || cooccurrences.length === 0) {
    return {
      nodes: [],
      links: [],
      metadata: {
        totalNodes: 0,
        totalLinks: 0,
        maxConnections: 0,
        minConnections: 0,
        maxWeight: 0,
        minWeight: 0
      }
    };
  }

  // Step 1: Extract unique keywords and count their connections
  const keywordConnections = new Map<string, number>();
  const keywordTotalWeight = new Map<string, number>();

  cooccurrences.forEach(cooc => {
    // Count connections for each keyword
    keywordConnections.set(
      cooc.keyword1, 
      (keywordConnections.get(cooc.keyword1) || 0) + 1
    );
    keywordConnections.set(
      cooc.keyword2, 
      (keywordConnections.get(cooc.keyword2) || 0) + 1
    );

    // Sum total weight (co-occurrence count) for each keyword
    keywordTotalWeight.set(
      cooc.keyword1,
      (keywordTotalWeight.get(cooc.keyword1) || 0) + cooc.cooccurrence_count
    );
    keywordTotalWeight.set(
      cooc.keyword2,
      (keywordTotalWeight.get(cooc.keyword2) || 0) + cooc.cooccurrence_count
    );
  });

  // Step 2: Create nodes array
  const nodes: NetworkNode[] = Array.from(keywordConnections.entries()).map(
    ([keyword, connectionCount]) => ({
      id: keyword,
      connectionCount,
      totalWeight: keywordTotalWeight.get(keyword) || 0,
      // D3 will add x, y, vx, vy during simulation
      x: undefined,
      y: undefined,
      vx: undefined,
      vy: undefined,
      fx: null,
      fy: null
    })
  );

  // Step 3: Create links array
  const links: NetworkLink[] = cooccurrences.map(cooc => ({
    source: cooc.keyword1,
    target: cooc.keyword2,
    weight: cooc.cooccurrence_count,
    inPosts: cooc.in_posts,
    inComments: cooc.in_comments,
    // D3 will replace source/target strings with node references during simulation
    index: undefined
  }));

  // Step 4: Calculate network metadata
  const connectionCounts = Array.from(keywordConnections.values());
  const weights = cooccurrences.map(cooc => cooc.cooccurrence_count);

  const metadata = {
    totalNodes: nodes.length,
    totalLinks: links.length,
    maxConnections: Math.max(...connectionCounts, 0),
    minConnections: Math.min(...connectionCounts, 0),
    maxWeight: Math.max(...weights, 0),
    minWeight: Math.min(...weights, 0)
  };

  return {
    nodes,
    links,
    metadata
  };
};

/**
 * Get the most connected keywords from network data
 * @param networkData Network data with nodes and connection counts
 * @param topN Number of top keywords to return (default: 5)
 * @returns Array of keywords sorted by connection count (descending)
 */
export const getMostConnectedKeywords = (
  networkData: NetworkData,
  topN: number = 5
): Array<{ keyword: string; connections: number; totalWeight: number }> => {
  return networkData.nodes
    .map(node => ({
      keyword: node.id,
      connections: node.connectionCount,
      totalWeight: node.totalWeight
    }))
    .sort((a, b) => b.connections - a.connections)
    .slice(0, topN);
};

/**
 * Get the least connected keywords from network data
 * @param networkData Network data with nodes and connection counts
 * @param bottomN Number of bottom keywords to return (default: 5)
 * @returns Array of keywords sorted by connection count (ascending)
 */
export const getLeastConnectedKeywords = (
  networkData: NetworkData,
  bottomN: number = 5
): Array<{ keyword: string; connections: number; totalWeight: number }> => {
  return networkData.nodes
    .map(node => ({
      keyword: node.id,
      connections: node.connectionCount,
      totalWeight: node.totalWeight
    }))
    .sort((a, b) => a.connections - b.connections)
    .slice(0, bottomN);
};

/**
 * Get the strongest relationships (highest weight links) from network data
 * @param networkData Network data with links and weights
 * @param topN Number of top relationships to return (default: 5)
 * @returns Array of relationships sorted by weight (descending)
 */
export const getStrongestRelationships = (
  networkData: NetworkData,
  topN: number = 5
): Array<{
  keyword1: string;
  keyword2: string;
  weight: number;
  inPosts: number;
  inComments: number;
}> => {
  return networkData.links
    .map(link => ({
      keyword1: typeof link.source === 'string' ? link.source : link.source.id,
      keyword2: typeof link.target === 'string' ? link.target : link.target.id,
      weight: link.weight,
      inPosts: link.inPosts,
      inComments: link.inComments
    }))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, topN);
};

/**
 * Filter network data by minimum connection threshold
 * @param networkData Original network data
 * @param minConnections Minimum number of connections a node must have
 * @returns Filtered network data
 */
export const filterNetworkByConnections = (
  networkData: NetworkData,
  minConnections: number
): NetworkData => {
  // Filter nodes by minimum connections
  const filteredNodes = networkData.nodes.filter(
    node => node.connectionCount >= minConnections
  );

  // Get set of remaining node IDs
  const remainingNodeIds = new Set(filteredNodes.map(node => node.id));

  // Filter links to only include those between remaining nodes
  const filteredLinks = networkData.links.filter(link => {
    const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
    const targetId = typeof link.target === 'string' ? link.target : link.target.id;
    return remainingNodeIds.has(sourceId) && remainingNodeIds.has(targetId);
  });

  // Recalculate metadata
  const connectionCounts = filteredNodes.map(node => node.connectionCount);
  const weights = filteredLinks.map(link => link.weight);

  return {
    nodes: filteredNodes,
    links: filteredLinks,
    metadata: {
      totalNodes: filteredNodes.length,
      totalLinks: filteredLinks.length,
      maxConnections: connectionCounts.length > 0 ? Math.max(...connectionCounts) : 0,
      minConnections: connectionCounts.length > 0 ? Math.min(...connectionCounts) : 0,
      maxWeight: weights.length > 0 ? Math.max(...weights) : 0,
      minWeight: weights.length > 0 ? Math.min(...weights) : 0
    }
  };
};

/**
 * Filter network data by minimum weight threshold
 * @param networkData Original network data
 * @param minWeight Minimum weight (co-occurrence count) a link must have
 * @returns Filtered network data with recalculated node connections
 */
export const filterNetworkByWeight = (
  networkData: NetworkData,
  minWeight: number
): NetworkData => {
  // Filter links by minimum weight
  const filteredLinks = networkData.links.filter(link => link.weight >= minWeight);

  // Recalculate node connections based on filtered links
  const nodeConnections = new Map<string, number>();
  const nodeTotalWeights = new Map<string, number>();

  filteredLinks.forEach(link => {
    const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
    const targetId = typeof link.target === 'string' ? link.target : link.target.id;

    nodeConnections.set(sourceId, (nodeConnections.get(sourceId) || 0) + 1);
    nodeConnections.set(targetId, (nodeConnections.get(targetId) || 0) + 1);

    nodeTotalWeights.set(sourceId, (nodeTotalWeights.get(sourceId) || 0) + link.weight);
    nodeTotalWeights.set(targetId, (nodeTotalWeights.get(targetId) || 0) + link.weight);
  });

  // Filter nodes to only include those that still have connections
  const filteredNodes = networkData.nodes
    .filter(node => nodeConnections.has(node.id))
    .map(node => ({
      ...node,
      connectionCount: nodeConnections.get(node.id) || 0,
      totalWeight: nodeTotalWeights.get(node.id) || 0
    }));

  // Recalculate metadata
  const connectionCounts = filteredNodes.map(node => node.connectionCount);
  const weights = filteredLinks.map(link => link.weight);

  return {
    nodes: filteredNodes,
    links: filteredLinks,
    metadata: {
      totalNodes: filteredNodes.length,
      totalLinks: filteredLinks.length,
      maxConnections: connectionCounts.length > 0 ? Math.max(...connectionCounts) : 0,
      minConnections: connectionCounts.length > 0 ? Math.min(...connectionCounts) : 0,
      maxWeight: weights.length > 0 ? Math.max(...weights) : 0,
      minWeight: weights.length > 0 ? Math.min(...weights) : 0
    }
  };
};