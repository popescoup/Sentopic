/**
 * useD3 Custom Hook
 * Manages D3 lifecycle, DOM manipulation, and cleanup within React components
 * Provides safe integration between D3's imperative style and React's declarative approach
 */

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

/**
 * Custom hook for integrating D3 with React
 * Handles the lifecycle of D3 visualizations and ensures proper cleanup
 * 
 * @param renderFunction Function that receives a D3 selection and renders the visualization
 * @param dependencies Array of dependencies that trigger re-rendering when changed
 * @returns Ref object to attach to the target element (usually SVG)
 */
export const useD3 = <T extends Element>(
  renderFunction: (selection: d3.Selection<T, unknown, null, undefined>) => void,
  dependencies: React.DependencyList = []
) => {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!ref.current) return;

    // Create D3 selection from the ref element
    const selection = d3.select(ref.current);

    // Call the render function with the selection
    try {
      renderFunction(selection);
    } catch (error) {
      console.error('Error in D3 render function:', error);
    }

    // Cleanup function
    return () => {
      // Stop any ongoing transitions
      selection.selectAll('*').interrupt();
      
      // Remove event listeners that D3 might have attached
      selection.on('.zoom', null);
      selection.on('.drag', null);
      selection.on('.brush', null);
      
      // Clear any D3-managed data
      selection.selectAll('*').data([]);
      
      // Remove any tooltips or temporary elements D3 might have created
      d3.selectAll('.d3-tooltip').remove();
      d3.selectAll('[class*="d3-"]').remove();
    };
  }, dependencies);

  return ref;
};

/**
 * Hook for managing D3 with resize capabilities
 * Automatically handles window resize events and re-renders the visualization
 * 
 * @param renderFunction Function that receives a D3 selection, width, and height
 * @param dependencies Array of dependencies that trigger re-rendering when changed
 * @returns Object with ref and current dimensions
 */
export const useD3WithResize = <T extends Element>(
  renderFunction: (
    selection: d3.Selection<T, unknown, null, undefined>,
    width: number,
    height: number
  ) => void,
  dependencies: React.DependencyList = []
) => {
  const ref = useRef<T>(null);
  const dimensionsRef = useRef({ width: 0, height: 0 });

  useEffect(() => {
    if (!ref.current) return;

    const element = ref.current;
    const selection = d3.select(element);

    // Function to get current dimensions
    const updateDimensions = () => {
      const rect = element.getBoundingClientRect();
      dimensionsRef.current = {
        width: rect.width || 800,
        height: rect.height || 400
      };
    };

    // Function to render with current dimensions
    const render = () => {
      updateDimensions();
      const { width, height } = dimensionsRef.current;
      
      try {
        renderFunction(selection, width, height);
      } catch (error) {
        console.error('Error in D3 render function:', error);
      }
    };

    // Initial render
    render();

    // Set up resize observer for responsive behavior
    const resizeObserver = new ResizeObserver(() => {
      render();
    });

    resizeObserver.observe(element);

    // Cleanup function
    return () => {
      resizeObserver.disconnect();
      
      // Stop any ongoing transitions
      selection.selectAll('*').interrupt();
      
      // Remove event listeners
      selection.on('.zoom', null);
      selection.on('.drag', null);
      selection.on('.brush', null);
      
      // Clear D3 data
      selection.selectAll('*').data([]);
      
      // Remove temporary elements
      d3.selectAll('.d3-tooltip').remove();
      d3.selectAll('[class*="d3-"]').remove();
    };
  }, dependencies);

  return {
    ref,
    dimensions: dimensionsRef.current
  };
};

/**
 * Hook for managing D3 tooltips
 * Provides utilities for creating and managing tooltips in D3 visualizations
 * 
 * @returns Object with tooltip utility functions
 */
export const useD3Tooltip = () => {
  const showTooltip = (
    event: MouseEvent,
    content: string,
    className: string = 'absolute bg-content border border-border-primary rounded-input px-2 py-1 font-small text-text-primary shadow-card z-50 pointer-events-none'
  ) => {
    // Remove any existing tooltips
    hideTooltip();

    // Create new tooltip
    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', `d3-tooltip ${className}`)
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 10) + 'px')
      .style('opacity', 0);

    // Add content
    tooltip.html(content);

    // Fade in
    tooltip.transition()
      .duration(200)
      .style('opacity', 1);

    return tooltip;
  };

  const hideTooltip = () => {
    d3.selectAll('.d3-tooltip')
      .transition()
      .duration(200)
      .style('opacity', 0)
      .remove();
  };

  const updateTooltip = (event: MouseEvent) => {
    d3.selectAll('.d3-tooltip')
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 10) + 'px');
  };

  return {
    showTooltip,
    hideTooltip,
    updateTooltip
  };
};

/**
 * Hook for managing D3 zoom behavior
 * Provides consistent zoom configuration and management
 * 
 * @param scaleExtent Array with min and max zoom levels
 * @returns Object with zoom behavior and utility functions
 */
export const useD3Zoom = (scaleExtent: [number, number] = [0.1, 10]) => {
  const zoomBehavior = useRef<d3.ZoomBehavior<any, any> | null>(null);

  const createZoom = <T extends Element>(
    selection: d3.Selection<T, unknown, null, undefined>,
    onZoom: (event: d3.D3ZoomEvent<T, unknown>) => void
  ) => {
    zoomBehavior.current = d3.zoom<T, unknown>()
      .scaleExtent(scaleExtent)
      .on('zoom', onZoom);

    selection.call(zoomBehavior.current);

    return zoomBehavior.current;
  };

  const resetZoom = <T extends Element>(
    selection: d3.Selection<T, unknown, null, undefined>,
    duration: number = 750
  ) => {
    if (zoomBehavior.current) {
      selection
        .transition()
        .duration(duration)
        .call(zoomBehavior.current.transform, d3.zoomIdentity);
    }
  };

  const zoomToFit = <T extends Element>(
    selection: d3.Selection<T, unknown, null, undefined>,
    bounds: [[number, number], [number, number]],
    padding: number = 20,
    duration: number = 750
  ) => {
    if (zoomBehavior.current) {
      const [[x0, y0], [x1, y1]] = bounds;
      const width = (selection.node() as any)?.clientWidth || 800;
      const height = (selection.node() as any)?.clientHeight || 600;

      const scale = Math.min(
        (width - padding * 2) / (x1 - x0),
        (height - padding * 2) / (y1 - y0)
      );

      const translate: [number, number] = [
        width / 2 - scale * (x0 + x1) / 2,
        height / 2 - scale * (y0 + y1) / 2
      ];

      selection
        .transition()
        .duration(duration)
        .call(
          zoomBehavior.current.transform,
          d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
        );
    }
  };

  return {
    createZoom,
    resetZoom,
    zoomToFit,
    zoomBehavior: zoomBehavior.current
  };
};

export default useD3;