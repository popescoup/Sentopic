/**
 * Keyword Network Graph Component
 * D3-powered network visualization for keyword co-occurrences
 * Renders keywords as nodes and relationships as edges with interactive features
 */

import React from 'react';
import * as d3 from 'd3';
import { useD3 } from '@/hooks/useD3';
import type { NetworkNode, NetworkLink, NetworkData } from '@/types/api';

interface KeywordNetworkGraphProps {
  /** Network data with nodes and links */
  networkData: NetworkData;
  /** Function called when a link is clicked for exploration */
  onLinkClick: (source: string, target: string) => void;
  /** Width of the visualization container */
  width?: number;
  /** Height of the visualization container */
  height?: number;
  /** Additional CSS classes */
  className?: string;
}

export const KeywordNetworkGraph: React.FC<KeywordNetworkGraphProps> = ({
  networkData,
  onLinkClick,
  width = 800,
  height = 400,
  className = ''
}) => {

  // Use custom D3 hook for lifecycle management - this returns the ref we need
  const svgRef = useD3((svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) => {
    
    // Clear previous content
    svg.selectAll('*').remove();

    // ADD THIS DEBUG LOG HERE
    console.log('🔍 D3 Render Function Called:', {
      svgElement: svg.node(),
      svgSize: svg.node()?.getBoundingClientRect(),
      dataNodes: networkData.nodes.length,
      dataLinks: networkData.links.length,
      width,
      height
    });

    // If no data, show empty state
    if (!networkData.nodes.length || !networkData.links.length) {
      svg
        .append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('class', 'fill-text-tertiary font-body text-sm')
        .text('No keyword relationships to display');
      return;
    }

    // Create main group for zoom/pan
    const g = svg.append('g').attr('class', 'network-container');

    // Define scales for node size and link width
    const nodeConnectionScale = d3
      .scaleLinear()
      .domain(d3.extent(networkData.nodes, d => d.connectionCount) as [number, number])
      .range([8, 24]);

    const linkWidthScale = d3
      .scaleLinear()
      .domain(d3.extent(networkData.links, d => d.weight) as [number, number])
      .range([1, 6]);

    // Create force simulation
    const simulation = d3
    .forceSimulation<NetworkNode>(networkData.nodes)
    .force('link', d3.forceLink<NetworkNode, NetworkLink>(networkData.links)
      .id(d => d.id)
      .distance(80)
      .strength(0.3)
    )
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide<NetworkNode>().radius(d => nodeConnectionScale(d.connectionCount) + 4));

    // Create links
    const links = g
      .selectAll('.link')
      .data(networkData.links)
      .enter()
      .append('line')
      .attr('class', 'link cursor-pointer transition-all duration-150')
      .attr('stroke', '#e1e4e8')
      .attr('stroke-width', d => linkWidthScale(d.weight))
      .attr('opacity', 0.6)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke', '#0366d6')
          .attr('opacity', 0.8);
        
        // Show tooltip
        const tooltip = d3.select('body')
          .append('div')
          .attr('class', 'absolute bg-content border border-border-primary rounded-input px-2 py-1 font-small text-text-primary shadow-card z-50 pointer-events-none')
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px')
          .text(`"${d.source}" + "${d.target}": ${d.weight} co-occurrences`);
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke', '#e1e4e8')
          .attr('opacity', 0.6);
        
        // Remove tooltip
        d3.selectAll('.absolute').remove();
      })
      .on('click', function(event, d) {
        event.stopPropagation();
        onLinkClick(
          typeof d.source === 'string' ? d.source : d.source.id,
          typeof d.target === 'string' ? d.target : d.target.id
        );
      });

    // Create nodes
    const nodes = g
      .selectAll('.node')
      .data(networkData.nodes)
      .enter()
      .append('g')
      .attr('class', 'node cursor-pointer')
      .call(d3.drag<SVGGElement, NetworkNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      );

    // Add circles to nodes
    nodes
      .append('circle')
      .attr('r', d => nodeConnectionScale(d.connectionCount))
      .attr('fill', '#0366d6')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .attr('class', 'transition-all duration-150')
      .on('mouseover', function(event, d) {
        // Highlight connected links
        links
          .attr('stroke', link => {
            const isConnected = (
              (typeof link.source === 'string' ? link.source : link.source.id) === d.id ||
              (typeof link.target === 'string' ? link.target : link.target.id) === d.id
            );
            return isConnected ? '#0366d6' : '#e1e4e8';
          })
          .attr('opacity', link => {
            const isConnected = (
              (typeof link.source === 'string' ? link.source : link.source.id) === d.id ||
              (typeof link.target === 'string' ? link.target : link.target.id) === d.id
            );
            return isConnected ? 0.8 : 0.2;
          });

        // Highlight this node
        d3.select(this)
          .attr('fill', '#2563eb')
          .attr('r', nodeConnectionScale(d.connectionCount) + 2);

        // Show tooltip
        const tooltip = d3.select('body')
          .append('div')
          .attr('class', 'absolute bg-content border border-border-primary rounded-input px-2 py-1 font-small text-text-primary shadow-card z-50 pointer-events-none')
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px')
          .text(`"${d.id}": ${d.connectionCount} connections`);
      })
      .on('mouseout', function(event, d) {
        // Reset link styles
        links
          .attr('stroke', '#e1e4e8')
          .attr('opacity', 0.6);

        // Reset node style
        d3.select(this)
          .attr('fill', '#0366d6')
          .attr('r', nodeConnectionScale(d.connectionCount));

        // Remove tooltip
        d3.selectAll('.absolute').remove();
      });

    // Add labels to nodes
    nodes
      .append('text')
      .text(d => d.id)
      .attr('class', 'font-small fill-text-primary pointer-events-none')
      .attr('text-anchor', 'middle')
      .attr('dy', d => nodeConnectionScale(d.connectionCount) + 16)
      .attr('font-size', '11px')
      .attr('font-weight', '500');

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', d => (d.source as NetworkNode).x!)
        .attr('y1', d => (d.source as NetworkNode).y!)
        .attr('x2', d => (d.target as NetworkNode).x!)
        .attr('y2', d => (d.target as NetworkNode).y!);

      nodes.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Stop simulation after a reasonable time to preserve performance
    setTimeout(() => {
      simulation.stop();
    }, 5000);

  }, [networkData, onLinkClick, width, height]);

  return (
    <div className={`network-graph-container ${className}`}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-border-primary rounded-default bg-content"
        style={{ maxWidth: '100%', height: 'auto' }}
      >
        {/* D3 will render content here */}
      </svg>
      
      {/* Legend */}
      <div className="mt-3 flex items-center justify-center space-x-6 text-small text-text-secondary">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-accent"></div>
          <span>Keywords (size = connections)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-6 h-0.5 bg-border-secondary"></div>
          <span>Co-occurrences (thickness = frequency)</span>
        </div>
        <div className="text-text-tertiary">
          Drag nodes • Hover for details • Click edges to explore
        </div>
      </div>
    </div>
  );
};

export default KeywordNetworkGraph;