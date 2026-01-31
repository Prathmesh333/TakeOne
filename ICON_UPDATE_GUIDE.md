# Icon Update Guide - Custom SVG Icons

This document lists all the custom SVG icons that need to be integrated into the UI.

## Icons to Update

### 1. TakeOne Logo (Clapperboard)
**Location**: Sidebar header
**Current**: Generic play button
**New**: Film clapperboard icon
```
Status: ✅ UPDATED
```

### 2. Home Icon (Smiley Face)
**Location**: Sidebar navigation
**Current**: House icon
**New**: Smiley face icon
```
Status: ✅ UPDATED
```

### 3. Library Icon (Book)
**Location**: Sidebar navigation
**Current**: Generic book
**New**: Open book icon
```
Status: ✅ UPDATED
```

### 4. Statistics Icon (Bar Chart)
**Location**: Sidebar stats section header
**Current**: Text only
**New**: Bar chart icon
```
Status: ✅ UPDATED
```

### 5. Indexed Content Icon (Floppy Disk)
**Location**: Sidebar stats - Total Scenes metric
**Current**: None
**New**: Floppy disk/save icon
```
Status: ✅ UPDATED
```

### 6. Upload Video Icon (Cloud Upload)
**Location**: Library page - File upload section
**Current**: Generic upload
**New**: Cloud with arrow up
```
Status: ⏳ PENDING - Need to find in code
```

### 7. URL Upload Icon (Link/Permalink)
**Location**: Library page - URL input section
**Current**: Generic link
**New**: Chain link icon
```
Status: ⏳ PENDING - Need to find in code
```

### 8. Browse Files Icon (Gallery)
**Location**: Library page - File browser
**Current**: Generic folder
**New**: Image gallery grid icon
```
Status: ⏳ PENDING - Need to find in code
```

### 9. Navigation Icon (Compass)
**Location**: Quick links section
**Current**: Generic arrow
**New**: Compass/navigation icon
```
Status: ⏳ PENDING - Need to find in code
```

### 10. View All Videos Icon (Gallery Grid)
**Location**: Home page - Quick links
**Current**: Generic grid
**New**: Photo gallery grid icon
```
Status: ⏳ PENDING - Need to find in code
```

## Layout Fixes Needed

### Sidebar Statistics Section
- ✅ Fixed padding and spacing
- ✅ Added icon to "Indexed Content" metric
- ✅ Improved visual hierarchy
- ✅ Better color contrast with cyan glow

### Library Manager Buttons
- ⏳ Need to adjust button sizes
- ⏳ Add consistent padding
- ⏳ Ensure proper alignment

### Quick Links Section
- ⏳ Add icons to all quick link buttons
- ⏳ Standardize button sizes
- ⏳ Improve spacing

## Next Steps

1. Search for upload/URL sections in Library page
2. Update remaining icons
3. Fix button sizing and padding
4. Test all icon displays
5. Ensure responsive behavior

## Color Scheme for Icons

All icons should use:
- **Default**: `currentColor` (inherits from parent)
- **Active/Hover**: Cyan glow effect
- **Gradient**: Cyan to Rust for primary elements

## Icon Size Standards

- **Logo**: 48x48px
- **Navigation**: 20x20px
- **Section Headers**: 16x16px
- **Inline Icons**: 14x14px
- **Buttons**: 18x18px
