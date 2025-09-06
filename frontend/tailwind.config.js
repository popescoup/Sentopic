/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Terminal color palette
        background: '#f0f0f0',
        content: '#ffffff',
        panel: '#e8e8e8',
        border: {
          DEFAULT: '#c0c0c0',
          primary: '#c0c0c0',
          secondary: '#d4d4d4', 
          emphasis: '#808080',
          dark: '#808080',
          light: '#d4d4d4'
        },
        text: {
          primary: '#000000',
          secondary: '#333333',
          tertiary: '#666666'
        },
        // Terminal accent colors
        accent: '#0066cc',
        success: '#00ff41',  // Terminal green
        warning: '#ffb000',  // Amber
        danger: '#cc0000',   // Bold red
        info: '#00ffff',     // Cyan
        // Sentiment colors
        sentiment: {
          positive: '#00ff41',
          negative: '#cc0000',
          neutral: '#666666'
        },
        // Hover states
        hover: {
          blue: 'rgba(0, 102, 204, 0.1)',
          green: 'rgba(0, 255, 65, 0.1)',
          panel: '#e0e0e0'
        }
      },
      fontFamily: {
        // Terminal fonts - monospace everywhere
        sans: ['Courier New', 'Courier', 'monospace'],
        mono: ['Courier New', 'SF Mono', 'Monaco', 'Consolas', 'monospace'],
        terminal: ['Courier New', 'Courier', 'monospace'],
        primary: ['Courier New', 'Courier', 'monospace']
      },
      fontSize: {
        // Existing terminal font scale
        'caption': ['10px', { lineHeight: '1.1', letterSpacing: '0.5px' }],
        'small': ['12px', { lineHeight: '1.3', letterSpacing: '0.5px' }],    // Increased from 10px
        'body': ['14px', { lineHeight: '1.3' }],                             // Increased from 12px  
        'large': ['16px', { lineHeight: '1.3' }],                            // Increased from 14px
        'title': ['18px', { lineHeight: '1.1', letterSpacing: '1px' }],      // Increased from 16px
        'header': ['20px', { lineHeight: '1.1', letterSpacing: '-0.5px' }],
        
        // New larger sizes for buttons
        'button-lg': ['16px', { lineHeight: '1.2', letterSpacing: '0.5px' }],
        'button-xl': ['18px', { lineHeight: '1.2', letterSpacing: '0.5px' }],
        
        // Legacy aliases (updated)
        'page-title': ['16px', { lineHeight: '1.1', letterSpacing: '1px' }],
        'section-header': ['14px', { lineHeight: '1.3', letterSpacing: '1px' }],
        'subsection': ['12px', { lineHeight: '1.3' }],
        'technical': ['12px', { lineHeight: '1.3' }]
      },
      spacing: {
        // Terminal spacing scale - dense layout (4px base)
        '1': '4px',    // xs
        '1.5': '6px',  // sm 
        '2': '8px',    // md - most common
        '3': '12px',   // lg
        '4': '16px',   // xl
        '6': '24px',   // xxl
        
        // Component-specific spacing
        'button-sm': '6px',
        'button-md': '8px', 
        'button-lg': '12px',
        'panel': '8px',
        'input': '6px'
      },
      borderRadius: {
        // Terminal geometry - sharp edges everywhere
        'none': '0px',
        'default': '0px',
        'input': '0px',
        'sm': '0px',
        'md': '0px',
        'lg': '0px',
        'full': '0px'
      },
      borderWidth: {
        // Terminal definition
        'thin': '1px',
        'medium': '2px', 
        'thick': '3px',
        DEFAULT: '1px'
      },
      boxShadow: {
        // Terminal depth - minimal shadows
        'none': 'none',
        'light': '1px 1px 2px rgba(0,0,0,0.1)',
        'medium': '2px 2px 4px rgba(0,0,0,0.15)',
        'card': '1px 1px 2px rgba(0,0,0,0.1)',
        'card-hover': '2px 2px 4px rgba(0,0,0,0.15)',
        'modal': '2px 2px 8px rgba(0,0,0,0.2)',
        'focus': '0 0 0 2px #0066cc'
      },
      transitionTimingFunction: {
        // Terminal responsiveness
        'instant': 'ease',
        'terminal': 'ease'
      },
      transitionDuration: {
        // Fast terminal feedback
        'instant': '100ms',
        'quick': '150ms',
        'normal': '200ms'
      },
      backgroundImage: {
        // Remove gradients - flat terminal aesthetic
        'gradient-panel': 'none',
        'gradient-header': 'none', 
        'gradient-subtle': 'none'
      },
      letterSpacing: {
        // Terminal text spacing
        'terminal-tight': '-0.5px',
        'terminal': '0px',
        'terminal-wide': '0.5px',
        'terminal-widest': '1px'
      },
      lineHeight: {
        // Terminal density
        'terminal-tight': '1.1',
        'terminal': '1.3',
        'terminal-relaxed': '1.4'
      },
      zIndex: {
        // Clean z-index scale
        'dropdown': '200',
        'tooltip': '300', 
        'header': '100',
        'modal': '1000'
      }
    },
  },
  plugins: [],
}