/**
 * OmniDesk AI - Color Theme
 * Pink/Purple gradient with gray accents
 */

export const colors = {
  // Primary gradient: Pink → Purple
  primary: {
    pink: '#E91E63',
    purple: '#9C27B0',
    darkPurple: '#6A1B9A',
  },
  // Purple tints
  purple100: '#F3E5F5', // Very light purple background
  purple50: '#F9F5FC',  // Even lighter purple
  // Grays
  gray: {
    lightest: '#F5F5F5',
    light: '#E0E0E0',
    medium: '#9E9E9E',
    dark: '#424242',
    darkest: '#212121',
  },
  // Utility
  white: '#FFFFFF',
  black: '#000000',
  success: '#4CAF50',
  error: '#F44336',
  warning: '#FF9800',
};

export const gradients = {
  primary: `linear-gradient(135deg, ${colors.primary.pink} 0%, ${colors.primary.purple} 100%)`,
  subtle: `linear-gradient(135deg, ${colors.gray.lightest} 0%, ${colors.white} 100%)`,
};
