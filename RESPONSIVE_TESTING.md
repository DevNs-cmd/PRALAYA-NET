# Responsive UI Testing Checklist

This guide ensures the PRALAYA-NET dashboard works correctly across all device sizes.

## Responsive Breakpoints

The dashboard uses the following responsive breakpoints (aligned with Tailwind CSS):

- **Mobile**: 320px - 639px (small phones)
- **Small**: 640px - 767px (large phones)
- **Tablet (md)**: 768px - 1023px (tablets)
- **Desktop (lg)**: 1024px - 1439px (small/medium desktops)
- **Large Desktop (xl)**: 1440px+ (large monitors)

## Testing Devices

### Mobile Testing (320px - 639px)

**Devices to test:**
- iPhone SE (375px)
- iPhone 12 (390px)
- Samsung Galaxy S21 (360px)
- Android phone (320px minimum)

**Mobile-Specific Features to Verify:**
- [ ] Hamburger menu button appears (left panel toggle)
- [ ] Hamburger menu button appears (right panel toggle)
- [ ] Menu buttons animate smoothly (rotate icon animation)
- [ ] Left panel (ControlPanel) shows as full-screen modal when opened
- [ ] Right panel (IntelligenceFeed) shows as full-screen modal when opened
- [ ] Mobile overlay appears behind open panels
- [ ] Tapping overlay closes the open panel
- [ ] Header title displays at 18px font size
- [ ] Header subtitle is hidden on mobile
- [ ] Timestamp is hidden on mobile
- [ ] Backend status label hidden (shows only indicator)
- [ ] Error banner padding is 12px 16px
- [ ] No horizontal scrolling on any screen
- [ ] Map displays full-width below header
- [ ] Charts and content don't overflow
- [ ] Buttons are large enough to tap (minimum 44px height)
- [ ] Form inputs are appropriately sized

### Tablet Testing (768px - 1023px)

**Devices to test:**
- iPad Mini (768px)
- iPad 10th Gen (820px)
- Samsung Galaxy Tab S6 (800px)
- Android tablet (768px)

**Tablet-Specific Features to Verify:**
- [ ] Left panel (ControlPanel) displays as sidebar
- [ ] Left panel width is 280px
- [ ] Right panel (IntelligenceFeed) is hidden by default on tablet
- [ ] Hamburger menu button for right panel visible
- [ ] Center content (map) fills remaining space
- [ ] Header elements display with proper spacing
- [ ] Header subtitle is visible
- [ ] Timestamp is still hidden
- [ ] Two-column grid layout (left sidebar + main content)
- [ ] Left panel content scrolls independently
- [ ] Maps scale properly for tablet aspect ratio
- [ ] Charts display with appropriate sizing
- [ ] No horizontal scrolling
- [ ] Panels close automatically when window resizes to mobile

### Desktop Testing (1024px+)

**Devices to test:**
- Laptop at 1024px
- Full HD (1920px)
- Ultra-wide (2560px)
- Desktop monitors

**Desktop-Specific Features to Verify:**
- [ ] Three-column layout visible (left: 320px, center: flexible, right: 380px)
- [ ] Left panel (ControlPanel) displays as sidebar
- [ ] Right panel (IntelligenceFeed) displays as sidebar
- [ ] Both sidebars show full content without modal
- [ ] Hamburger menu buttons are hidden
- [ ] Header displays with full spacing and all elements
- [ ] Header title at 20px font size
- [ ] Header subtitle is visible
- [ ] Timestamp is visible
- [ ] Map fills center column
- [ ] All three columns scroll independently if needed
- [ ] No empty space or awkward gaps
- [ ] Content adapts well to wide screens

## Component-Level Testing

### Header/Navigation
- [ ] Logo/title displays correctly at all sizes
- [ ] Navigation elements are accessible
- [ ] Mobile menu buttons appear/disappear appropriately
- [ ] Backend status indicator visible on all sizes
- [ ] Error banner displays correctly at all sizes

### Map Container
- [ ] Map displays full-width on mobile
- [ ] Map height adjusts properly (400px min on mobile, 100% on desktop)
- [ ] Map controls are accessible and sized for touch on mobile
- [ ] No map overflow on any device size
- [ ] Map performs smoothly on tablet and desktop

### Control Panel (Left Sidebar)
- [ ] Hidden on mobile by default
- [ ] Toggles open/closed with hamburger menu on mobile
- [ ] Shows as sidebar on tablet+
- [ ] All buttons fit within panel width (280px tablet, 320px desktop)
- [ ] Form inputs don't overflow
- [ ] Scrolls independently when content overflows
- [ ] Content readable on mobile when panel is open

### Intelligence Feed (Right Sidebar)
- [ ] Hidden on tablet by default
- [ ] Toggles open/closed with hamburger menu on mobile/tablet
- [ ] Shows as sidebar on desktop only (1024px+)
- [ ] Alert items display correctly at all sizes
- [ ] Text doesn't overflow on any size
- [ ] Scrolls smoothly
- [ ] Feed updates don't cause layout shifts

### Status Items
- [ ] Display in appropriate grid layout for screen size
- [ ] Cards don't overflow on mobile
- [ ] Padding and margin scale appropriately
- [ ] Text is readable on all sizes
- [ ] Icons display correctly

### Buttons and Controls
- [ ] Buttons are appropriately sized for each screen
- [ ] Button text doesn't overflow
- [ ] Multiple buttons stack vertically on mobile
- [ ] Buttons arranged horizontally on tablet+
- [ ] Touch-friendly size on mobile (minimum 44px height)
- [ ] Hover states work on desktop
- [ ] Active states clear and visible

### Tables and Data Display
- [ ] Tables display as single-column cards on mobile
- [ ] Table headers hidden on mobile, shown with `data-label` attribute
- [ ] Horizontal scroll on mobile if absolutely needed
- [ ] Tablet view shows 2-column table if space allows
- [ ] Desktop shows full table layout

## Browser-Specific Testing

### Chrome
- [ ] Mobile emulation shows correct layout
- [ ] DevTools responsive mode works correctly
- [ ] Scrollbar styling appears correct
- [ ] Animations are smooth

### Firefox
- [ ] Mobile view displays correctly
- [ ] Responsive Design Mode works
- [ ] All CSS features supported

### Safari
- [ ] Mobile Safari on iPhone displays correctly
- [ ] iPad Safari shows proper tablet layout
- [ ] Desktop Safari shows desktop layout
- [ ] Touch interactions work smoothly

### Edge
- [ ] Responsive mode works correctly
- [ ] All features display properly

## Performance Testing

- [ ] Dashboard loads quickly on mobile network (3G)
- [ ] No layout shifts when menu opens/closes
- [ ] Smooth animations on mobile (60fps target)
- [ ] No excessive scrolling on any device
- [ ] Images scale appropriately for device
- [ ] No console errors related to responsiveness

## Accessibility Testing (Mobile-Focused)

- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming (16px minimum on mobile)
- [ ] Color contrast meets WCAG AA standards
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Menu can be closed with keyboard (Escape)
- [ ] Focus states are visible
- [ ] Screen readers can navigate mobile layout

## Orientation Testing

### Portrait Mode (Mobile/Tablet)
- [ ] Layout adjusts for portrait orientation
- [ ] Sidebar panels adapt to portrait width
- [ ] Map height reduces appropriately
- [ ] No horizontal scrolling

### Landscape Mode (Mobile/Tablet)
- [ ] Landscape layout works correctly
- [ ] Sidebar panels remain accessible
- [ ] Map uses available horizontal space
- [ ] Header doesn't take excessive vertical space

## Testing Procedure

### Manual Testing
1. Open dashboard in browser
2. Open DevTools (F12)
3. Click responsive mode icon
4. Test each breakpoint listed above
5. Verify all features in the checklist
6. Test with actual devices if available

### Using Chrome DevTools
1. Press `Ctrl+Shift+M` (or `Cmd+Shift+M` on Mac) to enable responsive mode
2. Select specific device from dropdown OR manually set width
3. Rotate device to test portrait/landscape
4. Test touch interactions by enabling "Emulate mobile" option
5. Check console for errors

### Real Device Testing
1. Build and deploy dashboard to staging
2. Access on physical iPhone, Android, iPad, and desktop
3. Test all gestures (tap, scroll, pinch-zoom)
4. Verify performance on actual network speeds
5. Test in different lighting conditions for visibility

## Known Responsive Features

### CSS Responsive Properties
- Grid columns: `1fr` (mobile) → `280px 1fr` (tablet) → `320px 1fr 380px` (desktop)
- Header padding: `12px 16px` (mobile) → `12px 20px` (tablet+)
- Font sizes scale: title 18px (mobile) → 20px (tablet+)
- Panel visibility toggled with `.mobile-open` class and `display` property
- Hamburger menu animation: `rotate(360deg)` transform on `.mobile-menu-btn.active`

### React Responsive Features
- `mobileMenuOpen` state: Controls left panel visibility
- `mobileRightPanelOpen` state: Controls right panel visibility
- Window resize listener: Auto-closes modals when window ≥ 768px
- Mobile overlay: Dismisses panels when clicked

## Debugging Tips

### If layout breaks on specific width:
1. Check CSS media queries in `index.css`
2. Verify correct breakpoint is being targeted
3. Look for conflicting CSS rules
4. Check browser DevTools computed styles
5. Test with different zoom levels

### If menu button doesn't work:
1. Verify `mobileMenuOpen` state updates in React
2. Check `onClick` handler on hamburger button
3. Verify `.mobile-open` class is applied correctly
4. Check z-index values (should be 999 for modals)

### If content overflows:
1. Check element width constraints
2. Verify `overflow: hidden` is set on parent
3. Look for elements with fixed widths
4. Check padding/margin values
5. Use `min-width: 0` on flex children

## Version History

- **v1.0** - Initial responsive implementation
- Mobile-first approach with progressive enhancement
- Three-column desktop layout
- Hamburger menu system
- Responsive grid and typography
- Mobile modal panels

## Future Improvements

- [ ] Add gesture support (swipe to close panels)
- [ ] Implement responsive images with srcset
- [ ] Add tablet-specific optimizations
- [ ] Create print-friendly layout
- [ ] Add dark mode responsive testing
- [ ] Implement PWA features
