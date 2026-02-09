/**
 * OmniDesk AI - Color Theme
 * Centralized color constants for consistent theming
 */

export const colors = {
  // Primary gradient: Pink → Purple
  primary: {
    pink: '#E91E63',
    purple: '#9C27B0',
    darkPurple: '#6A1B9A',
  },

  // Purple tints for backgrounds
  purple100: '#F3E5F5',
  purple50: '#F9F5FC',

  // Grays
  gray: {
    lightest: '#F5F5F5',
    light: '#E0E0E0',
    medium: '#9E9E9E',
    dark: '#424242',
    darkest: '#212121',
  },

  // Utility colors
  white: '#FFFFFF',
  black: '#000000',
  success: '#66BB6A',
  warning: '#FFA726',
  error: '#EF5350',
};

export const gradients = {
  primary: `linear-gradient(135deg, ${colors.primary.pink} 0%, ${colors.primary.purple} 100%)`,
  primaryVertical: `linear-gradient(180deg, ${colors.primary.pink} 0%, ${colors.primary.purple} 100%)`,
  subtle: `linear-gradient(135deg, ${colors.gray.lightest} 0%, ${colors.white} 100%)`,
  purple: `linear-gradient(180deg, ${colors.purple100} 0%, ${colors.purple50} 100%)`,
};
