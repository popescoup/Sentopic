/**
 * Trends Chart Component
 * D3-powered line chart visualization for keyword trends over time
 * Supports both mention frequency and sentiment trends with interactive features
 */

import React from 'react';
import * as d3 from 'd3';
import { useD3 } from '@/hooks/useD3';

interface TrendsDataPoint {
  time_period: string;
  formatted_date: string;
  [key: string]: string | number; // Dynamic fields for keyword data
}

interface TrendsChartProps {
  /** Chart data points */
  data: TrendsDataPoint[];
  /** Keywords being analyzed */
  keywords: string[];
  /** Chart type: 'mentions' or 'sentiment' */
  chartType: 'mentions' | 'sentiment';
  /** Width of the visualization container */
  width?: number;
  /** Height of the visualization container */
  height?: number;
  /** Additional CSS classes */
  className?: string;
}

export const TrendsChart: React.FC<TrendsChartProps> = ({
    data,
    keywords,
    chartType,
    width = 800,
    height = 400,
    className = ''
  }) => {
    
    // Professional color palette for chart lines (matches your design system)
    const colorScale = d3.scaleOrdinal<string>()
      .domain(keywords)
      .range(['#0366d6', '#28a745', '#dc3545', '#ffc107', '#6f42c1']);
  
    const svgRef = useD3((svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) => {
    // Clear previous content
    svg.selectAll('*').remove();

    // Set up margins for professional chart layout
    const margin = { top: 20, right: 120, bottom: 35, left: 60 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    // If no data, show empty state
    if (!data || data.length === 0) {
      svg
        .append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('class', 'fill-text-tertiary font-body text-sm')
        .text('No trend data available');
      return;
    }

    // Create main chart group (this will appear above the masks)
    const chartGroup = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create zoom container group
    const zoomGroup = chartGroup.append('g').attr('class', 'zoom-container');

    // Parse dates and set up scales - handle different formats
    // Check if we have monthly data (format: YYYY-MM) or daily/weekly (format: YYYY-MM-DD)
    const sampleDate = data[0]?.time_period || '';
    const isMonthlyFormat = sampleDate.match(/^\d{4}-\d{2}$/);
    
    // Use appropriate date parser based on format
    const parseDate = isMonthlyFormat 
      ? d3.timeParse('%Y-%m')
      : d3.timeParse('%Y-%m-%d');
    
    const dates = data.map(d => {
      // For monthly format, ensure we have a valid date string
      if (isMonthlyFormat && d.time_period.match(/^\d{4}-\d{2}$/)) {
        return parseDate(d.time_period);
      } else if (!isMonthlyFormat && d.time_period.match(/^\d{4}-\d{2}-\d{2}$/)) {
        return parseDate(d.time_period);
      }
      return null;
    }).filter(Boolean) as Date[];
    
    const xScale = d3.scaleTime()
      .domain(d3.extent(dates) as [Date, Date])
      .range([0, chartWidth]);

    // Set up Y scale based on chart type
    let yDomain: [number, number];
    if (chartType === 'sentiment') {
      // Fixed domain for sentiment (-1 to 1)
      yDomain = [-1, 1];
    } else {
      // Dynamic domain for mentions
      const allValues = keywords.flatMap(keyword => 
        data.map(d => d[`${keyword.replace(/[^a-zA-Z0-9]/g, '_')}_${chartType}`] as number || 0)
      );
      const maxValue = d3.max(allValues) || 0;
      yDomain = [0, maxValue * 1.1]; // Add 10% padding
    }

    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([chartHeight, 0]);

    // Create line generator
    const line = d3.line<TrendsDataPoint>()
      .x(d => {
        const parsedDate = parseDate(d.time_period);
        return parsedDate ? xScale(parsedDate) : 0;
      })
      .y(d => {
        const safeKeyword = keywords[0]?.replace(/[^a-zA-Z0-9]/g, '_');
        return yScale(d[`${safeKeyword}_${chartType}`] as number || 0);
      })
      .curve(d3.curveMonotoneX); // Smooth curves

    // Add clipping path to contain zoomed content
    const clipPath = svg.append('defs')
      .append('clipPath')
      .attr('id', `chart-clip-${Math.random().toString(36).substr(2, 9)}`)
      .append('rect')
      .attr('width', chartWidth)
      .attr('height', chartHeight);

    // Apply clipping to zoom group
    zoomGroup.attr('clip-path', `url(#${clipPath.attr('id')})`);

    // Create axis generators
    const xAxis = d3.axisBottom(xScale)
      .tickFormat((domainValue) => {
        const date = domainValue as Date;
        return d3.timeFormat('%b %d')(date);
      });

    const yAxisFormat = chartType === 'sentiment' 
      ? d3.format('+.2f') 
      : d3.format('d');

    const yAxis = d3.axisLeft(yScale)
      .tickFormat((domainValue) => {
        const value = domainValue as number;
        return yAxisFormat(value);
      });

    // Add grid lines (in chart group, not zoom group, so they align with axes)
    const xAxisGrid = d3.axisBottom(xScale)
    .tickSize(-chartHeight)
    .tickFormat(() => '');

    const yAxisGrid = d3.axisLeft(yScale)
    .tickSize(-chartWidth)
    .tickFormat(() => '');

    const xGridGroup = chartGroup.append('g')
    .attr('class', 'grid x-grid')
    .attr('transform', `translate(0,${chartHeight})`)
    .call(xAxisGrid as any);

    xGridGroup.selectAll('line')
    .attr('stroke', '#f6f8fa')
    .attr('stroke-width', 1);

    // Remove the domain line (the line at the bottom/right of the grid)
    xGridGroup.select('.domain').remove();

    const yGridGroup = chartGroup.append('g')
    .attr('class', 'grid y-grid')
    .call(yAxisGrid as any);

    yGridGroup.selectAll('line')
    .attr('stroke', '#f6f8fa')
    .attr('stroke-width', 1);

    // Remove the domain line (the line at the left/top of the grid)
    yGridGroup.select('.domain').remove();
    
    // Add white overlay masks (after grid and chart content, but before axes)
    const maskGroup = chartGroup.append('g').attr('class', 'boundary-masks');
    
    // Left mask (covers area left of Y-axis) - positioned relative to chartGroup
    maskGroup.append('rect')
    .attr('x', -margin.left)
    .attr('y', -margin.top)
    .attr('width', margin.left)
    .attr('height', height)
    .attr('fill', '#ffffff');

    // Right mask (covers area right of chart) - positioned relative to chartGroup
    maskGroup.append('rect')
    .attr('x', chartWidth)  // Moved 1px to the right to show the last grid line
    .attr('y', -margin.top)
    .attr('width', margin.right)
    .attr('height', height)
    .attr('fill', '#ffffff');

    // Top mask (covers area above chart) - positioned relative to chartGroup
    maskGroup.append('rect')
    .attr('x', -margin.left)
    .attr('y', -margin.top)
    .attr('width', chartWidth + margin.left + margin.right)
    .attr('height', margin.top)
    .attr('fill', '#ffffff');

    // Bottom mask (covers area below X-axis) - positioned relative to chartGroup
    maskGroup.append('rect')
    .attr('x', -margin.left)
    .attr('y', chartHeight)
    .attr('width', chartWidth + margin.left + margin.right)
    .attr('height', margin.bottom)
    .attr('fill', '#ffffff');
    
    // Add axes (outside zoom group so they stay fixed) - AFTER masks
    const xAxisGroup = chartGroup.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(xAxis as any);
    
    xAxisGroup.selectAll('text')
      .attr('class', 'font-small fill-text-secondary')
      .style('text-anchor', 'middle');

    const yAxisGroup = chartGroup.append('g')
      .attr('class', 'y-axis')
      .call(yAxis as any);
    
    yAxisGroup.selectAll('text')
      .attr('class', 'font-small fill-text-secondary');

    // Add Y axis label (positioned based on text length)
    chartGroup.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', chartType === 'sentiment' ? 0 - margin.left : 0 - (margin.left / 2))
    .attr('x', 0 - (chartHeight / 2))
    .attr('dy', chartType === 'sentiment' ? '1em' : '0.02em')
    .attr('class', 'font-small fill-text-primary text-center')
    .text(chartType === 'sentiment' ? 'Average Sentiment' : 'Mention Count');

    // Create tooltip div
    const tooltip = d3.select('body')
      .selectAll('.trends-tooltip')
      .data([0])
      .join('div')
      .attr('class', 'trends-tooltip absolute bg-content border border-border-primary rounded-input px-3 py-2 font-small text-text-primary shadow-card z-50 pointer-events-none')
      .style('opacity', 0);

    // Draw lines for each keyword
    keywords.forEach((keyword, index) => {
        const safeKeyword = keyword.replace(/[^a-zA-Z0-9]/g, '_');
        const fieldName = `${safeKeyword}_${chartType}`;
        
        // Update line generator for this keyword
        const keywordLine = d3.line<TrendsDataPoint>()
          .x(d => {
            const parsedDate = parseDate(d.time_period);
            return parsedDate ? xScale(parsedDate) : 0;
          })
          .y(d => yScale(d[fieldName] as number || 0))
          .curve(d3.curveMonotoneX);
  
        // Draw the line
      const path = zoomGroup.append('path')
      .datum(data)
      .attr('class', `trend-line trend-line-${index}`)
      .attr('fill', 'none')
      .attr('stroke', colorScale(keyword))
      .attr('stroke-width', 2.5)
      .attr('d', keywordLine);

    // Add dots for data points
    const dots = zoomGroup.selectAll(`.dots-${index}`)
      .data(data)
      .enter()
      .append('circle')
      .attr('class', `dots-${index} trend-dot`)
      .attr('cx', d => {
        const parsedDate = parseDate(d.time_period);
        return parsedDate ? xScale(parsedDate) : 0;
      })
      .attr('cy', d => yScale(d[fieldName] as number || 0))
      .attr('r', 4)
      .attr('fill', colorScale(keyword))
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');

      // Add hover interactions
      dots
        .on('mouseover', function(event, d) {
          // Get current zoom transform to calculate proper scaled radius
          const currentTransform = d3.zoomTransform(svg.node()!);
          const scaleInverse = 1 / currentTransform.k;
          
          d3.select(this)
            .transition()
            .duration(100)
            .attr('r', 6 * scaleInverse);

          // Get the current keyword's value
          const currentValue = d[fieldName] as number || 0;
          
          // Find all keywords that have the exact same value at this time period
          const overlappingKeywords: Array<{keyword: string, value: number}> = [];
          
          keywords.forEach(kw => {
            const safeKw = kw.replace(/[^a-zA-Z0-9]/g, '_');
            const kwFieldName = `${safeKw}_${chartType}`;
            const kwValue = d[kwFieldName] as number || 0;
            
            // Only include keywords that have the exact same value
            if (kwValue === currentValue) {
              overlappingKeywords.push({
                keyword: kw,
                value: kwValue
              });
            }
          });

          // Format the value once since all overlapping keywords have the same value
          const formattedValue = chartType === 'sentiment' 
            ? (currentValue >= 0 ? '+' : '') + currentValue.toFixed(3)
            : currentValue.toLocaleString();

          let tooltipHTML;
          
          if (overlappingKeywords.length === 1) {
            // Single keyword - use original tooltip format
            tooltipHTML = `
              <div class="font-medium text-text-primary">${overlappingKeywords[0].keyword}</div>
              <div class="text-text-secondary">${d.formatted_date}</div>
              <div class="font-medium text-accent">
                ${chartType === 'sentiment' ? 'Sentiment: ' : 'Mentions: '}${formattedValue}
              </div>
            `;
          } else {
            // Multiple keywords with same value - use combined tooltip format
            const keywordsList = overlappingKeywords.map(kw => kw.keyword).join(', ');
            
            tooltipHTML = `
              <div class="font-medium text-text-primary">${keywordsList}</div>
              <div class="text-text-secondary">${d.formatted_date}</div>
              <div class="font-medium text-accent">
                ${chartType === 'sentiment' ? 'Sentiment: ' : 'Mentions: '}${formattedValue}
              </div>
            `;
          }

          tooltip
            .style('opacity', 1)
            .html(tooltipHTML)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
          // Get current zoom transform to calculate proper scaled radius
          const currentTransform = d3.zoomTransform(svg.node()!);
          const scaleInverse = 1 / currentTransform.k;
          
          d3.select(this)
            .transition()
            .duration(100)
            .attr('r', 4 * scaleInverse);

          tooltip.style('opacity', 0);
        });

      // Animate line drawing
      const totalLength = path.node()?.getTotalLength() || 0;
      path
        .attr('stroke-dasharray', totalLength + ' ' + totalLength)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1000)
        .ease(d3.easeLinear)
        .attr('stroke-dashoffset', 0);
    });

    // Add legend (will appear above the masks)
    const legend = chartGroup.append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${chartWidth + 20}, 20)`);

    keywords.forEach((keyword, index) => {
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${index * 25})`);
    
      legendRow.append('line')
        .attr('x1', 0)
        .attr('x2', 15)
        .attr('stroke', colorScale(keyword))
        .attr('stroke-width', 2.5);
    
      const textElement = legendRow.append('text')
        .attr('x', 20)
        .attr('y', 0)
        .attr('class', 'font-small fill-text-primary');
    
      // Break keyword into chunks of maximum 9 characters per line
      const maxCharsPerLine = 9;
      const lineHeight = 12; // pixels between lines
      
      if (keyword.length <= maxCharsPerLine) {
        // Single line - use normal positioning
        textElement.append('tspan')
          .attr('x', 20)
          .attr('dy', '0.35em')
          .text(keyword);
      } else {
        // Multiple lines needed
        const words = keyword.split(' ');
        let currentLine = '';
        let lineNumber = 0;
        
        words.forEach((word, wordIndex) => {
          // Check if adding this word would exceed the line limit
          const testLine = currentLine ? currentLine + ' ' + word : word;
          
          if (testLine.length <= maxCharsPerLine) {
            // Word fits on current line
            currentLine = testLine;
            
            // If this is the last word, add the line
            if (wordIndex === words.length - 1) {
              textElement.append('tspan')
                .attr('x', 20)
                .attr('dy', lineNumber === 0 ? '0.35em' : `${lineHeight}px`)
                .text(currentLine);
            }
          } else {
            // Word doesn't fit - finish current line and start new one
            if (currentLine) {
              textElement.append('tspan')
                .attr('x', 20)
                .attr('dy', lineNumber === 0 ? '0.35em' : `${lineHeight}px`)
                .text(currentLine);
              lineNumber++;
            }
            
            // Handle the word that didn't fit
            if (word.length <= maxCharsPerLine) {
              // Word fits on its own line
              currentLine = word;
              
              // If this is the last word, add the line
              if (wordIndex === words.length - 1) {
                textElement.append('tspan')
                  .attr('x', 20)
                  .attr('dy', `${lineHeight}px`)
                  .text(currentLine);
              }
            } else {
              // Word is too long - need to break it
              let remainingWord = word;
              
              while (remainingWord.length > 0) {
                if (remainingWord.length <= maxCharsPerLine) {
                  // Last piece fits
                  const prefix = lineNumber > 0 || currentLine ? '-' : '';
                  textElement.append('tspan')
                    .attr('x', 20)
                    .attr('dy', lineNumber === 0 ? '0.35em' : `${lineHeight}px`)
                    .text(prefix + remainingWord);
                  lineNumber++;
                  remainingWord = '';
                } else {
                  // Need to break the word
                  const charsToTake = lineNumber > 0 ? maxCharsPerLine - 1 : maxCharsPerLine; // Reserve space for hyphen on continuation lines
                  const piece = remainingWord.substring(0, charsToTake);
                  
                  textElement.append('tspan')
                    .attr('x', 20)
                    .attr('dy', lineNumber === 0 ? '0.35em' : `${lineHeight}px`)
                    .text(lineNumber > 0 ? '-' + piece : piece);
                  
                  remainingWord = remainingWord.substring(charsToTake);
                  lineNumber++;
                }
              }
              
              currentLine = '';
            }
          }
        });
      }
    });

    // Add zero line for sentiment charts
    if (chartType === 'sentiment') {
        zoomGroup.append('line')
          .attr('x1', 0)
          .attr('x2', chartWidth)
          .attr('y1', yScale(0))
          .attr('y2', yScale(0))
          .attr('stroke', '#6a737d')
          .attr('stroke-width', 1)
          .attr('stroke-dasharray', '3,3');
      }
  
      // Set up zoom behavior with dynamic axis updates and constraints
    const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([1, 5])
    .translateExtent([[0, 0], [chartWidth, chartHeight]])
    .extent([[0, 0], [chartWidth, chartHeight]])
    .on('zoom', (event) => {
      const transform = event.transform;
      
      // Apply transform to zoom group
      zoomGroup.attr('transform', transform.toString());
      
      // Calculate scaling factors for visual elements
      const scaleInverse = 1 / transform.k;
      
      // Update line widths to scale with zoom
      zoomGroup.selectAll('.trend-line')
        .attr('stroke-width', 2.5 * scaleInverse);
      
      // Update dot sizes to scale with zoom
      zoomGroup.selectAll('.trend-dot')
        .attr('r', 4 * scaleInverse)
        .attr('stroke-width', 2 * scaleInverse);
      
      // Update axes with new scales
      const newXScale = transform.rescaleX(xScale);
      const newYScale = transform.rescaleY(yScale);
      
      // Update X axis
      const newXAxis = d3.axisBottom(newXScale)
        .tickFormat((domainValue) => {
          const date = domainValue as Date;
          return d3.timeFormat('%b %d')(date);
        });
      
      xAxisGroup.call(newXAxis as any);
      xAxisGroup.selectAll('text')
        .attr('class', 'font-small fill-text-secondary')
        .style('text-anchor', 'middle');
      
      // Update Y axis
      const newYAxis = d3.axisLeft(newYScale)
        .tickFormat((domainValue) => {
          const value = domainValue as number;
          return yAxisFormat(value);
        });
      
      yAxisGroup.call(newYAxis as any);
      yAxisGroup.selectAll('text')
        .attr('class', 'font-small fill-text-secondary');
      
      // Update grid lines to align with new axis scales
    const newXGrid = d3.axisBottom(newXScale)
    .tickSize(-chartHeight)
    .tickFormat(() => '');

    const newYGrid = d3.axisLeft(newYScale)
    .tickSize(-chartWidth)
    .tickFormat(() => '');

    // Remove old grid lines and recreate them with proper positioning
    xGridGroup.selectAll('*').remove();
    yGridGroup.selectAll('*').remove();

    xGridGroup.call(newXGrid as any);
    xGridGroup.selectAll('line')
    .attr('stroke', '#f6f8fa')
    .attr('stroke-width', 1);
    // Remove domain line after zoom update
    xGridGroup.select('.domain').remove();

    yGridGroup.call(newYGrid as any);
    yGridGroup.selectAll('line')
    .attr('stroke', '#f6f8fa')
    .attr('stroke-width', 1);
    // Remove domain line after zoom update  
    yGridGroup.select('.domain').remove();
    });

    // Apply zoom behavior to SVG
    svg.call(zoom);
    
    // Add double-click to reset zoom
    svg.on('dblclick.zoom', () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity);
    });
  
    }, [data, keywords, chartType, width, height]);

  return (
    <div className={`trends-chart-container ${className}`}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-border-primary rounded-default bg-content"
        style={{ maxWidth: '100%', height: 'auto' }}
      >
        {/* D3 will render content here */}
      </svg>
      
      {/* Chart info */}
      <div className="mt-3 flex items-center justify-center text-small text-text-secondary">
        <div className="text-text-tertiary">
          Scroll to zoom • Drag to pan • Double-click to reset • Hover over data points for details
        </div>
      </div>
    </div>
  );
};

export default TrendsChart;