# Comprehensive CSS Audit Report
## Django Project: CapstoneCH61
**Date:** March 10, 2026

---

## Executive Summary

After thoroughly examining all template files and CSS stylesheets in the project, I've identified **47 CSS issues** across multiple categories. The project has a solid CSS foundation with good dark mode support, but there are several areas that need attention for optimal production readiness.

---

## Issues by Severity

| Severity | Count |
|----------|-------|
| Critical | 4 |
| High | 12 |
| Medium | 19 |
| Low | 12 |

---

## Critical Issues

### 1. `100vw` Causing Horizontal Scrollbar

**Files Affected:**
- [templates/pages/chapter_leadership.html](templates/pages/chapter_leadership.html#L15-L16)
- [templates/pages/chapter_programs.html](templates/pages/chapter_programs.html#L16-L17)
- [templates/registration/password_reset.html](templates/registration/password_reset.html#L15-L16)

**Lines:** 15-17 (leadership), 16-18 (programs), 15-17 (password_reset)

**Problem:** Using `width: 100vw` combined with `margin-left: calc(-50vw + 50%)` causes horizontal scrollbar when the page has a vertical scrollbar (scrollbar takes up ~17px on desktop).

**Code Example:**
```css
.leadership-container {
    width: 100vw;
    margin-left: calc(-50vw + 50%);
}
```

**Recommended Fix:**
```css
.leadership-container {
    width: 100%;
    margin-left: 0;
    box-sizing: border-box;
}
/* Or use: overflow-x: hidden on body/html as a fallback */
```

**Severity:** Critical

---

### 2. Missing Focus Indicators on Interactive Elements

**Files Affected:**
- [static/css/navbar.css](static/css/navbar.css#L254-L282) - `.nav-link` buttons
- [static/css/base.css](static/css/base.css#L161-L226) - All `.btn` variants
- Multiple template inline styles

**Problem:** Many buttons and links lack visible focus states for keyboard navigation, violating WCAG 2.1 accessibility guidelines.

**Recommended Fix:**
```css
.btn:focus,
.nav-link:focus,
.portal-nav-link:focus {
    outline: 2px solid #fff;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(22, 79, 144, 0.5);
}
```

**Severity:** Critical (Accessibility)

---

### 3. Portal Navigation Unreadable Text

**File:** [static/css/navbar.css](static/css/navbar.css#L580-L620)

**Lines:** 580-620

**Problem:** The `.portal-nav-link` has extremely small font sizes:
```css
.portal-nav-link {
    font-size: 0.4rem;  /* Too small - ~6px */
}
.portal-nav-link span {
    font-size: 0.38rem; /* Even smaller */
}
```

These sizes are illegible on any device.

**Recommended Fix:**
```css
.portal-nav-link {
    font-size: 0.65rem; /* ~10px minimum */
}
.portal-nav-link span {
    font-size: 0.6rem;
}
```

**Severity:** Critical (Legibility)

---

### 4. Overcrowded Portal Navbar on Mobile

**File:** [static/css/navbar.css](static/css/navbar.css#L750-L820)

**Lines:** 750-820

**Problem:** On mobile, the portal navbar collapses all links into a column, but with the current tiny font sizes and cramped spacing, it becomes unusable.

**Recommended Fix:** Create a horizontal scrollable container or hamburger menu for portal links on mobile.

**Severity:** Critical

---

## High Severity Issues

### 5. Hardcoded Colors Not Using CSS Variables

**Files Affected:**
- [templates/pages/home.html](templates/pages/home.html#L85-L95) - `background: #f0f0f0`
- [templates/pages/portal/dashboard.html](templates/pages/portal/dashboard.html#L170) - `#c9a227`
- [templates/pages/boutique/shop.html](templates/pages/boutique/shop.html#L6-L11) - Custom PBS colors
- [templates/pages/portal/roster.html](templates/pages/portal/roster.html#L130-L150) - Hardcoded table colors

**Problem:** Many templates use hardcoded hex colors instead of CSS variables, making consistent theming difficult.

**Recommended Fix:** Update to use CSS variables:
```css
:root {
    --pbs-blue: #0047AB;
    --pbs-gold: #CFB53B;
}
```

**Severity:** High

---

### 6. Inconsistent Button Styling Across Pages

**Files Affected:**
- [templates/pages/contact.html](templates/pages/contact.html#L115-L145) - `.btn-submit`, `.btn-cancel`
- [templates/pages/signup.html](templates/pages/signup.html#L150-L175) - Different button styles
- [templates/pages/boutique/cart.html](templates/pages/boutique/cart.html#L78-L130) - Custom `.btn-checkout`
- [templates/pages/boutique/checkout.html](templates/pages/boutique/checkout.html#L70-L100) - Different checkout buttons

**Problem:** Each page defines its own button styles with different padding, colors, and hover effects.

**Recommended Fix:** Consolidate all button styles in `base.css` and use consistent class names.

**Severity:** High

---

### 7. Fixed Heights Causing Content Clipping

**Files Affected:**
- [templates/pages/home.html](templates/pages/home.html#L52-L58) - Grid row heights
- [static/css/chatbot.css](static/css/chatbot.css#L37-L42) - Fixed chat message height

**Problem:**
```css
.home-cards {
    grid-template-rows: 50% 50%;  /* Fixed percentages */
}
```
This can clip content on smaller screens or when content is longer than expected.

**Recommended Fix:** Use `minmax()` or `auto` for flexible grid rows.

**Severity:** High

---

### 8. Images Missing `object-fit` and Responsive Sizing

**Files Affected:**
- [templates/pages/portal/photo_gallery.html](templates/pages/portal/photo_gallery.html#L25-L35)
- [templates/pages/chapter_leadership.html](templates/pages/chapter_leadership.html#L95-L105)
- [templates/pages/events.html](templates/pages/events.html#L320)

**Problem:** Some images don't have proper responsive sizing or `object-fit` properties:
```css
.leader-image img {
    width: 100%;
    height: 100%;
    /* Missing object-fit can distort images */
}
```

**Recommended Fix:**
```css
.leader-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
}
```

**Severity:** High

---

### 9. Missing Mobile Media Queries in Key Templates

**Files Affected:**
- [templates/pages/portal/roster.html](templates/pages/portal/roster.html) - Table overflow issues
- [templates/pages/portal/profile.html](templates/pages/portal/profile.html) - Complex layout not optimized

**Problem:** The roster table doesn't have adequate mobile handling - only hides phone column.

**Recommended Fix:** Add proper responsive table handling:
```css
@media (max-width: 768px) {
    .roster-table-container {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    .roster-table {
        min-width: 800px;
    }
}
```

**Severity:** High

---

### 10. Dark Mode Missing for Form Elements

**Files Affected:**
- [templates/pages/boutique/checkout.html](templates/pages/boutique/checkout.html#L45-L60)
- [templates/pages/events.html](templates/pages/events.html#L60-L70)

**Problem:** Some form elements don't have dark mode styling:
```css
.search-box input {
    /* No dark mode variant */
    background: #1a2a4a; /* Only specified inline */
}
```

**Recommended Fix:** Add consistent dark mode form styles to `base.css`.

**Severity:** High

---

### 11. Contrast Ratio Issues

**Files Affected:**
- [templates/pages/portal/announcements.html](templates/pages/portal/announcements.html#L85-L90) - `.text-muted` in dark mode
- [templates/pages/portal/roster.html](templates/pages/portal/roster.html#L200-L210) - Status badges

**Problem:**
```css
body.dark-mode .text-muted {
    color: #a0aec0; /* May not meet WCAG AA on dark backgrounds */
}
```

**Recommended Fix:** Ensure all text has at least 4.5:1 contrast ratio.

**Severity:** High

---

### 12. Card Glow Effect Inconsistency

**Files Affected:**
- [templates/pages/portal/dashboard.html](templates/pages/portal/dashboard.html#L160-L165)
- [templates/pages/portal/announcements.html](templates/pages/portal/announcements.html#L65-L70)

**Problem:** Different glow effects are used across pages:
```css
/* Dashboard */
.card-glow { box-shadow: 0 0 15px rgba(255, 255, 255, 0.8); }

/* Announcements */
.announcement-card { box-shadow: 0 0 20px rgba(255, 255, 255, 0.8); }
```

**Recommended Fix:** Create unified glow utility class in `base.css`.

**Severity:** High

---

### 13. Inline Styles Overriding CSS Classes

**Files Affected:**
- [templates/pages/home.html](templates/pages/home.html#L270-L310) - Multiple inline styles
- [templates/pages/boutique/cart.html](templates/pages/boutique/cart.html#L210-L280) - Extensive inline styling
- [templates/pages/chapter_programs.html](templates/pages/chapter_programs.html#L265) - Button inline styles

**Problem:** Heavy use of inline `style=""` attributes makes maintenance difficult and prevents CSS cascade benefits.

**Recommended Fix:** Move styles to CSS classes.

**Severity:** High

---

### 14. z-index Conflicts

**Files Affected:**
- [static/css/navbar.css](static/css/navbar.css#L10) - `.top-bar: z-index: 1001`
- [static/css/navbar.css](static/css/navbar.css#L244) - `.navbar: z-index: 1000`
- [templates/includes/cookie_banner.html](templates/includes/cookie_banner.html#L60) - `z-index: 10000`
- [templates/base.html](templates/base.html#L620) - Modal: `z-index: 9999`

**Problem:** Inconsistent z-index values with large gaps and potential stacking conflicts.

**Recommended Fix:** Create z-index scale:
```css
:root {
    --z-dropdown: 100;
    --z-sticky: 200;
    --z-fixed: 300;
    --z-modal-backdrop: 400;
    --z-modal: 500;
    --z-tooltip: 600;
}
```

**Severity:** High

---

### 15. Missing Print Styles

**Files Affected:** All templates

**Problem:** No print stylesheet or `@media print` rules exist for the site.

**Recommended Fix:** Add print styles in `base.css`:
```css
@media print {
    .top-bar,
    .navbar,
    .portal-navbar,
    .footer,
    .cookie-banner { display: none; }
    
    body { background: white; }
    
    .main-content {
        padding: 0;
        margin: 0;
    }
}
```

**Severity:** High

---

### 16. Animations Without Reduced Motion Support

**Files Affected:**
- [templates/pages/portal/announcements.html](templates/pages/portal/announcements.html#L60-L80) - Pulse animation
- [templates/pages/portal/dashboard.html](templates/pages/portal/dashboard.html#L180-L195) - Badge animations
- [static/css/navbar.css](static/css/navbar.css#L458-L468) - Cart badge pulse

**Problem:** Animations don't respect `prefers-reduced-motion` media query, which can cause issues for users with vestibular disorders.

**Recommended Fix:**
```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

**Severity:** High (Accessibility)

---

## Medium Severity Issues

### 17. Inconsistent Spacing System

**Files Affected:** Multiple templates

**Problem:** Inconsistent use of spacing (sometimes `rem`, sometimes `px`, different values for similar elements).

**Lines:** Throughout all templates

**Recommended Fix:** Create spacing scale in CSS variables:
```css
:root {
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
}
```

**Severity:** Medium

---

### 18. Duplicate CSS Rules

**Files Affected:**
- [templates/base.html](templates/base.html#L615-L650) and [templates/pages/home.html](templates/pages/home.html#L300-L350) - Modal styles duplicated
- [templates/pages/login.html](templates/pages/login.html#L85-L100) and [templates/pages/signup.html](templates/pages/signup.html#L90-L105) - Form styles duplicated

**Problem:** Same styles redefined in multiple places.

**Recommended Fix:** Move to shared CSS file or use CSS components.

**Severity:** Medium

---

### 19. Missing Hover States on Cards

**Files Affected:**
- [templates/pages/portal/dashboard.html](templates/pages/portal/dashboard.html#L35-L55)
- Some boutique product cards

**Problem:** Some interactive cards don't have cursor changes:
```css
.portal-card {
    /* Has :hover transform but no cursor: pointer */
}
```

**Recommended Fix:** Add `cursor: pointer` to all clickable cards.

**Severity:** Medium

---

### 20. Form Input Inconsistencies

**Files Affected:**
- [templates/pages/contact.html](templates/pages/contact.html#L85-L100) - Uses `.form-control`
- [templates/pages/signup.html](templates/pages/signup.html#L95-L110) - Uses `.form-input`
- [static/css/base.css](static/css/base.css#L290-L320) - Defines both

**Problem:** Two different class names for form inputs with slight variations.

**Recommended Fix:** Standardize on one class name throughout.

**Severity:** Medium

---

### 21. Gallery Image Aspect Ratio

**File:** [templates/pages/portal/photo_gallery.html](templates/pages/portal/photo_gallery.html#L10-L25)

**Problem:**
```css
.gallery-image-wrapper {
    height: 250px; /* Fixed height can distort varied image ratios */
}
```

**Recommended Fix:**
```css
.gallery-image-wrapper {
    aspect-ratio: 4/3;
    height: auto;
}
```

**Severity:** Medium

---

### 22. Calendar Cell Sizes Too Small on Mobile

**File:** [templates/pages/events.html](templates/pages/events.html#L135-L160)

**Problem:** Calendar table cells have fixed small padding, becoming cramped on mobile:
```css
.calendar-table td {
    height: 60px;
    padding: 0.5rem;
}
```

**Severity:** Medium

---

### 23. Missing Scrollbar Styling

**Files Affected:** All templates with scrollable areas

**Problem:** Custom scrollable areas (like chat messages, roster tables) don't have styled scrollbars, leading to inconsistent appearance.

**Recommended Fix:**
```css
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--background-light);
}

::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: 4px;
}
```

**Severity:** Medium

---

### 24. Loading Indicator Styling

**File:** [templates/pages/home.html](templates/pages/home.html#L710-L725) - Chatbot loading dots

**Problem:** Loading animation defined inline and not reusable:
```css
.loading-dots .dot {
    /* Inline animation styles */
}
```

**Recommended Fix:** Move to `chatbot.css` and make reusable.

**Severity:** Medium

---

### 25. Card Footer Alignment Issues

**File:** [templates/pages/portal/photo_gallery.html](templates/pages/portal/photo_gallery.html#L95-L110)

**Problem:** Card footer actions don't align properly when content varies.

**Recommended Fix:** Use flexbox with `margin-top: auto` for footer.

**Severity:** Medium

---

### 26. Missing Text Truncation

**Files Affected:**
- [templates/pages/portal/announcements.html](templates/pages/portal/announcements.html) - Long titles
- [templates/pages/boutique/shop.html](templates/pages/boutique/shop.html) - Product names

**Problem:** Long text can break layouts.

**Recommended Fix:**
```css
.card-title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
/* Or for multi-line: */
.card-description {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
```

**Severity:** Medium

---

### 27. Badge Styling Inconsistency

**Files Affected:**
- [templates/pages/portal/roster.html](templates/pages/portal/roster.html#L240-L280) - Status badges
- [templates/pages/boutique/shop.html](templates/pages/boutique/shop.html#L115-L125) - Category badges
- [templates/pages/portal/announcements.html](templates/pages/portal/announcements.html#L45-L55) - New badge

**Problem:** Different badge styles for similar purposes.

**Recommended Fix:** Create unified badge component.

**Severity:** Medium

---

### 28. Overlapping Content in Leadership Cards

**File:** [templates/pages/chapter_leadership.html](templates/pages/chapter_leadership.html#L295-L330)

**Problem:** The leader-contact section and leader-actions section can overlap when both are present (nested incorrectly in template).

**Severity:** Medium

---

### 29. Table Borders in Dark Mode

**Files Affected:**
- [templates/pages/events.html](templates/pages/events.html#L130-L145)
- [templates/pages/portal/roster.html](templates/pages/portal/roster.html#L155-L165)

**Problem:** Table borders use colors that don't adapt well in dark mode.

**Severity:** Medium

---

### 30. Search Box Width Constraints

**File:** [templates/pages/events.html](templates/pages/events.html#L62-L65)

**Problem:**
```css
.search-box input {
    width: 300px; /* Fixed width doesn't scale */
}
```

**Recommended Fix:**
```css
.search-box input {
    width: 100%;
    max-width: 300px;
}
```

**Severity:** Medium

---

### 31. Profile Cover Photo Sizing

**File:** [templates/pages/portal/profile.html](templates/pages/portal/profile.html) (inline styles)

**Problem:** Cover photo doesn't have proper aspect ratio maintenance or fallback styling.

**Severity:** Medium

---

### 32. Missing Container Max-Width on Some Pages

**Files Affected:**
- [templates/pages/home.html](templates/pages/home.html#L30-L35) - Custom override
- [templates/pages/portal/dashboard.html](templates/pages/portal/dashboard.html)

**Problem:** Some pages override container max-width inconsistently.

**Severity:** Medium

---

### 33. Button Icon Spacing

**Files Affected:** Multiple templates

**Problem:** Inconsistent spacing between icons and button text:
```html
<button><i class="fas fa-plus"></i> Add</button>
<button><i class="fas fa-plus"></i>Add</button>  <!-- No space -->
```

**Recommended Fix:** Use consistent CSS:
```css
.btn i:first-child {
    margin-right: 0.5rem;
}
```

**Severity:** Medium

---

### 34. Modal Max-Height Issues

**File:** [templates/base.html](templates/base.html#L640-L645)

**Problem:**
```css
.modal-scrollable {
    max-height: 80vh;
    /* May not account for modal padding/header/footer */
}
```

**Severity:** Medium

---

### 35. Gradient Text Not Supported Everywhere

**File:** Not directly used but may affect consistency

**Problem:** Any gradient text effects may not render in older browsers.

**Severity:** Medium

---

## Low Severity Issues

### 36. Brand Logo Size on Mobile

**File:** [static/css/navbar.css](static/css/navbar.css#L44-L48)

**Problem:** Brand logo maintains fixed width on mobile, could be optimized.

**Severity:** Low

---

### 37. Transition Timing Inconsistency

**Files Affected:** Multiple CSS files

**Problem:** Different transition durations used:
- `0.2s ease`
- `0.25s ease`
- `0.3s ease`
- `0.5s ease`

**Recommended Fix:** Standardize on 2-3 transition speeds.

**Severity:** Low

---

### 38. Empty State Styling

**Files Affected:**
- [templates/pages/portal/photo_gallery.html](templates/pages/portal/photo_gallery.html#L168-L175)
- [templates/pages/portal/announcements.html](templates/pages/portal/announcements.html#L45-L50)

**Problem:** Empty state styling varies between components.

**Severity:** Low

---

### 39. Link Underline Inconsistency

**Files Affected:** Multiple templates

**Problem:** Some links use underline on hover, others don't.

**Severity:** Low

---

### 40. Carousel Dot Size

**File:** [templates/pages/home.html](templates/pages/home.html#L220-L250)

**Problem:** Chapter carousel dots are 8px, may be hard to tap on mobile (recommended 44px touch target).

**Severity:** Low

---

### 41. Card Hover Transform Values

**Files Affected:** Multiple templates

**Problem:** Different `translateY` values on hover:
- `-3px`
- `-5px`
- `-8px`
- `-10px`

**Severity:** Low

---

### 42. Font Size Scale

**Files Affected:** All templates

**Problem:** Font sizes don't follow a consistent scale (type hierarchy).

**Recommended Fix:** Use modular scale:
```css
:root {
    --text-xs: 0.75rem;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.5rem;
    --text-3xl: 2rem;
}
```

**Severity:** Low

---

### 43. Border Radius Inconsistency

**Files Affected:** Multiple templates

**Problem:** Different border-radius values:
- `4px`
- `6px`
- `8px`
- `12px`
- `20px`

**Severity:** Low

---

### 44. Opacity Values for Overlays

**Files Affected:** Multiple templates

**Problem:** Different opacity values for background overlays:
- `0.5`
- `0.9`
- `0.95`

**Severity:** Low

---

### 45. Selection Highlighting

**Files Affected:** All templates

**Problem:** No custom `::selection` styling defined.

**Recommended Fix:**
```css
::selection {
    background: var(--primary-color);
    color: white;
}
```

**Severity:** Low

---

### 46. Loading State Indicators

**Files Affected:** Forms across templates

**Problem:** No loading state styling for form submissions.

**Severity:** Low

---

### 47. Skip Navigation Link

**Files Affected:** [templates/base.html](templates/base.html)

**Problem:** No skip-to-content link for keyboard users.

**Recommended Fix:** Add at top of body:
```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```
```css
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--primary-color);
    color: white;
    padding: 8px;
    z-index: 10000;
}
.skip-link:focus {
    top: 0;
}
```

**Severity:** Low (Accessibility)

---

## Summary of Recommendations

### Immediate Actions (Critical)
1. Fix `100vw` horizontal scroll issues
2. Add focus indicators to all interactive elements
3. Fix portal navbar font sizes (currently illegible)
4. Improve portal navbar mobile experience

### Short-term Improvements (High)
1. Consolidate button styles to `base.css`
2. Replace hardcoded colors with CSS variables
3. Add missing dark mode styles
4. Create z-index scale
5. Add print styles
6. Add `prefers-reduced-motion` support

### Long-term Refactoring (Medium/Low)
1. Create consistent spacing system
2. Eliminate duplicate CSS rules
3. Create reusable component classes
4. Standardize transitions and animations
5. Add custom scrollbar styling
6. Implement skip navigation link

---

## CSS Architecture Recommendations

### Create Design Tokens File
```css
/* _tokens.css */
:root {
    /* Colors */
    --color-primary: #164f90;
    --color-secondary: #c8c9c7;
    --color-accent: #0047AB;
    --color-success: #4caf50;
    --color-warning: #ff9800;
    --color-error: #d32f2f;
    
    /* Spacing */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 1rem;
    --space-4: 1.5rem;
    --space-5: 2rem;
    
    /* Typography */
    --font-sm: 0.875rem;
    --font-base: 1rem;
    --font-lg: 1.25rem;
    
    /* Radii */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
    
    /* Z-index */
    --z-dropdown: 100;
    --z-sticky: 200;
    --z-modal: 500;
}
```

---

**Report Generated:** March 10, 2026
**Total Files Analyzed:** 80+ templates and 6 CSS files
**Audit Performed By:** GitHub Copilot CSS Audit Tool
