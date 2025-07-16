/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors from the specification
        background: '#f5f6f7',
        content: '#ffffff',
        panel: '#fafbfc',
        border: {
          primary: '#e1e4e8',
          secondary: '#d1d5da', 
          emphasis: '#c6cbd1'
        },
        text: {
          primary: '#24292e',
          secondary: '#586069',
          tertiary: '#6a737d'
        },
        accent: '#0366d6',
        success: '#28a745',
        warning: '#ffd33d',
        danger: '#d73a49',
        // Hover states
        hover: {
          blue: 'rgba(3, 102, 214, 0.08)',
          green: 'rgba(40, 167, 69, 0.08)'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'SF Mono', 'Monaco', 'Consolas', 'monospace']
      },
      fontSize: {
        'page-title': ['32px', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
        'section-header': ['20px', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        'subsection': ['16px', { lineHeight: '1.2' }],
        'body': ['14px', { lineHeight: '1.5' }],
        'small': ['12px', { lineHeight: '1.4' }],
        'technical': ['13px', { lineHeight: '1.4' }]
      },
      spacing: {
        // 4px base unit system
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px'
      },
      borderRadius: {
        'default': '6px',
        'input': '4px'
      },
      boxShadow: {
        'card': '0 1px 3px rgba(27, 31, 35, 0.12), 0 1px 0 rgba(255, 255, 255, 0.02)',
        'card-hover': '0 2px 8px rgba(27, 31, 35, 0.15), 0 1px 0 rgba(255, 255, 255, 0.02)',
        'modal': '0 16px 64px rgba(27, 31, 35, 0.15), 0 0 0 1px rgba(27, 31, 35, 0.1)',
        'focus': '0 0 0 3px rgba(3, 102, 214, 0.3)'
      },
      transitionTimingFunction: {
        'sophisticated': 'cubic-bezier(0.4, 0, 0.2, 1)'
      },
      backgroundImage: {
        'gradient-panel': 'linear-gradient(180deg, #ffffff 0%, #fafbfc 100%)',
        'gradient-header': 'linear-gradient(180deg, #ffffff 0%, #fafbfc 100%)',
        'gradient-subtle': 'linear-gradient(180deg, #fafbfc 0%, #f6f8fa 100%)'
      }
    },
  },
  plugins: [],
}