import { ModuleRegistry, AllCommunityModule, themeAlpine } from 'ag-grid-community';

ModuleRegistry.registerModules([AllCommunityModule]);

// Custom theme based on Alpine
export const gridTheme = themeAlpine.withParams({
  fontFamily: "'Inter', sans-serif",
  fontSize: 13,
  headerFontWeight: 600,
  backgroundColor: '#ffffff',
  headerBackgroundColor: '#f8fafc',
  headerFontSize: 12,
  oddRowBackgroundColor: '#ffffff',
  rowHoverColor: '#eef2ff',
  selectedRowBackgroundColor: '#e0e7ff',
  borderColor: '#e2e8f0',
  rowBorder: { color: '#f1f5f9', width: 1, style: 'solid' },
});
