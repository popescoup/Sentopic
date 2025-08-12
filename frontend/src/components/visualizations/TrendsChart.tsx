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
    const margin = { top: 20, right: 120, bottom: 60, left: 60 };
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

    // Create main chart group
    const chartGroup = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Parse dates and set up scales
    const parseDate = d3.timeParse('%Y-%m-%d');
    const dates = data.map(d => parseDate(d.time_period)!).filter(Boolean);
    
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
      .x(d => xScale(parseDate(d.time_period)!))
      .y(d => {
        const safeKeyword = keywords[0]?.replace(/[^a-zA-Z0-9]/g, '_');
        return yScale(d[`${safeKeyword}_${chartType}`] as number || 0);
      })
      .curve(d3.curveMonotoneX); // Smooth curves

    // Add grid lines for professional appearance
    const xAxisGrid = d3.axisBottom(xScale)
      .tickSize(-chartHeight)
      .tickFormat(() => '');

    const yAxisGrid = d3.axisLeft(yScale)
      .tickSize(-chartWidth)
      .tickFormat(() => '');

    chartGroup.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(xAxisGrid as any)
      .selectAll('line')
      .attr('stroke', '#f6f8fa')
      .attr('stroke-width', 1);

    chartGroup.append('g')
      .attr('class', 'grid')
      .call(yAxisGrid as any)
      .selectAll('line')
      .attr('stroke', '#f6f8fa')
      .attr('stroke-width', 1);

    // Add X axis
    const xAxis = d3.axisBottom(xScale)
      .tickFormat((domainValue) => {
        const date = domainValue as Date;
        return d3.timeFormat('%b %d')(date);
      });

    chartGroup.append('g')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(xAxis as any)
      .selectAll('text')
      .attr('class', 'font-small fill-text-secondary')
      .style('text-anchor', 'middle');

    // Add Y axis
    const yAxisFormat = chartType === 'sentiment' 
      ? d3.format('+.2f') 
      : d3.format('d');

    const yAxis = d3.axisLeft(yScale)
      .tickFormat((domainValue) => {
        const value = domainValue as number;
        return yAxisFormat(value);
      });

    chartGroup.append('g')
      .call(yAxis as any)
      .selectAll('text')
      .attr('class', 'font-small fill-text-secondary');

    // Add Y axis label
    chartGroup.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (chartHeight / 2))
      .attr('dy', '1em')
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
        .x(d => xScale(parseDate(d.time_period)!))
        .y(d => yScale(d[fieldName] as number || 0))
        .curve(d3.curveMonotoneX);

      // Draw the line
      const path = chartGroup.append('path')
        .datum(data)
        .attr('class', 'trend-line')
        .attr('fill', 'none')
        .attr('stroke', colorScale(keyword))
        .attr('stroke-width', 2.5)
        .attr('d', keywordLine);

      // Add dots for data points
      const dots = chartGroup.selectAll(`.dots-${index}`)
        .data(data)
        .enter()
        .append('circle')
        .attr('class', `dots-${index} trend-dot`)
        .attr('cx', d => xScale(parseDate(d.time_period)!))
        .attr('cy', d => yScale(d[fieldName] as number || 0))
        .attr('r', 4)
        .attr('fill', colorScale(keyword))
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer');

      // Add hover interactions
      dots
        .on('mouseover', function(event, d) {
          d3.select(this)
            .transition()
            .duration(100)
            .attr('r', 6);

          const value = d[fieldName] as number || 0;
          const formattedValue = chartType === 'sentiment' 
            ? (value >= 0 ? '+' : '') + value.toFixed(3)
            : value.toLocaleString();

          tooltip
            .style('opacity', 1)
            .html(`
              <div class="font-medium text-text-primary">${keyword}</div>
              <div class="text-text-secondary">${d.formatted_date}</div>
              <div class="font-medium text-accent">
                ${chartType === 'sentiment' ? 'Sentiment: ' : 'Mentions: '}${formattedValue}
              </div>
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
          d3.select(this)
            .transition()
            .duration(100)
            .attr('r', 4);

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

    // Add legend
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

      legendRow.append('text')
        .attr('x', 20)
        .attr('y', 0)
        .attr('dy', '0.35em')
        .attr('class', 'font-small fill-text-primary')
        .text(keyword);
    });

    // Add zero line for sentiment charts
    if (chartType === 'sentiment') {
      chartGroup.append('line')
        .attr('x1', 0)
        .attr('x2', chartWidth)
        .attr('y1', yScale(0))
        .attr('y2', yScale(0))
        .attr('stroke', '#6a737d')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '3,3');
    }

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
          Hover over data points for details • {chartType === 'sentiment' ? 'Sentiment ranges from -1 (negative) to +1 (positive)' : 'Higher values indicate more mentions'}
        </div>
      </div>
    </div>
  );
};

export default TrendsChart;