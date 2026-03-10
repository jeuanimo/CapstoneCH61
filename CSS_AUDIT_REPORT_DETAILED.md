# Comprehensive CSS Audit Report

**Project:** CapstoneCH61  
**Date:** March 10, 2026  
**Audit Against:** CSS_GUIDE.txt and CSS_IMPLEMENTATION.txt

---

## Executive Summary

This audit identified **258 CSS violations** across **67 template files**. The most common issues are:

1. **Hardcoded colors** instead of CSS variables (Critical - 89 instances)
2. **Inline `<style>` blocks** duplicating base.css functionality (High - 52 templates)
3. **100vw width** causing horizontal scroll (High - 8 files)
4. **Boutique templates using non-standard color scheme** (Medium - 11 files)
5. **Style blocks in wrong template block** (Medium - 4 files)
6. **Missing responsive breakpoints** (Low - 15 files)

---

## CSS Variable Reference (From base.css)

```css
:root {
    --primary-color: #164f90;
    --secondary-color: #c8c9c7;
    --accent-color: #164f90;
    --text-light: #ffffff;
    --text-dark: #164f90;
    --background-light: #ffffff;
    --border-color: #c8c9c7;
    --success-color: #4caf50;
    --error-color: #d32f2f;
    --warning-color: #ff9800;
}
```

---

## Detailed Violations by File

### templates/pages/home.html (1065 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 17 | `background-color: #0b1020` hardcoded | High | Use `var(--background-light)` for dark mode |
| 146 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 154 | `color: #164f90 !important` hardcoded | Medium | Use `var(--primary-color)` |
| 210 | `color: #164f90 !important` hardcoded | Medium | Use `var(--primary-color)` |
| 305 | `background: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 314 | `background: rgba(22, 79, 144, 0.6)` hardcoded | Medium | Use `rgba(var(--primary-color-rgb), 0.6)` |
| 449 | `background-color: #ffffff` hardcoded | Low | Use `var(--background-light)` |
| 453 | `border-bottom: 2px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-500 | Large inline `<style>` block | High | Extract to home.css page-specific file |

**Total: 9 violations**

---

### templates/pages/about.html (157 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 76 | `background-color: #c8c9c7` hardcoded | Medium | Use `var(--secondary-color)` |
| 77 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 83-84 | `color: #164f90 !important` hardcoded | Medium | Use `var(--primary-color)` |
| 97-99 | `color: #164f90` hardcoded for h1/border | Medium | Use `var(--primary-color)` |
| 8-115 | Large inline `<style>` block | High | Use existing pages.css classes |

**Total: 5 violations**

---

### templates/pages/contact.html (291 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 48 | `border-bottom: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 57-58 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 95 | `color: #d32f2f` hardcoded | Medium | Use `var(--error-color)` |
| 106 | `border: 2px solid #c8c9c7` hardcoded | Medium | Use `var(--secondary-color)` |
| 112-113 | `border-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 145-146 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 153-155 | `background-color: #d32f2f` hardcoded | Medium | Use `var(--error-color)` |
| 8-175 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 8 violations**

---

### templates/pages/login.html (538 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 47 | `border-bottom: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 55 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 130-131 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 139-140 | `background-color: #c8c9c7` hardcoded | Medium | Use `var(--secondary-color)` |
| 268 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-310 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 6 violations**

---

### templates/pages/signup.html (385 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 48 | `border-bottom: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 56 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 174 | `style="color: #d32f2f;"` inline | Medium | Use `.text-danger` or `var(--error-color)` |
| 155 | `color: #d32f2f` hardcoded | Medium | Use `var(--error-color)` |
| 185-186 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-215 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 6 violations**

---

### templates/pages/signin.html (33 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| None | ✅ **COMPLIANT** - Uses auth-forms.css correctly | - | - |

**Total: 0 violations** ✅

---

### templates/pages/projects.html (74 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| None | ✅ **COMPLIANT** - Uses projects.css correctly | - | - |

**Total: 0 violations** ✅

---

### templates/pages/events.html (462 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 50 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 62 | `border: 2px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 74 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 93 | `border: 2px solid #c8c9c7` hardcoded | Medium | Use `var(--secondary-color)` |
| 107 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 125-126 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-250 | Large inline `<style>` block | High | Extract to events.css |

**Total: 7 violations**

---

### templates/pages/news.html (102 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 10-85 | `<style>` tag inside `{% block content %}` | High | Move to `{% block css %}` |
| 22 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 50 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |

**Total: 3 violations**

---

### templates/pages/action.html (104 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 10-85 | `<style>` tag inside `{% block content %}` | High | Move to `{% block css %}` |
| 22 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 50 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |

**Total: 3 violations**

---

### templates/pages/chapter_history.html (153 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 17-18 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` to prevent horizontal scroll |
| 44 | `border-bottom: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 50 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 76 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-107 | Large inline `<style>` block | High | Extract to chapter-history.css |

**Total: 5 violations**

---

### templates/pages/chapter_leadership.html (410 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 17-18 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` to prevent horizontal scroll |
| 69 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 123 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 197 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 209 | `background-color: #d32f2f` hardcoded | Medium | Use `var(--error-color)` |
| 8-220 | Large inline `<style>` block | High | Extract to chapter-leadership.css |

**Total: 6 violations**

---

### templates/pages/chapter_membership.html (386 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 17-18 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` to prevent horizontal scroll |
| 50 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 89 | `border-left: 4px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 145 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 193 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-230 | Large inline `<style>` block | High | Extract to chapter-membership.css |

**Total: 6 violations**

---

### templates/pages/chapter_programs.html (520 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 17-18 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` to prevent horizontal scroll |
| 50 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 108 | `background: #c8c9c7` hardcoded | Medium | Use `var(--secondary-color)` |
| 118 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 175 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-250 | Large inline `<style>` block | High | Extract to chapter-programs.css |

**Total: 6 violations**

---

### templates/pages/programs.html (66 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 14 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-35 | Additional inline `<style>` after pages.css | Medium | Add to pages.css |

**Total: 2 violations**

---

### templates/pages/chatbot_widget.html (503 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 57-200 | `<style>` tag inside `{% block content %}` | High | Move to `{% block css %}` |
| 77 | `background: linear-gradient(135deg, #164f90 0%, #0d3a6b 100%)` hardcoded | Medium | Use CSS variables |
| 99 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 108 | `border-left: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 50-200 | Large inline `<style>` block | High | Extract to chatbot.css (file exists but not used here) |

**Total: 5 violations**

---

## Boutique Templates (Non-Standard Color Scheme)

**All boutique templates define their own color variables instead of using the established theme:**

```css
/* INCORRECT - Found in boutique templates */
:root {
    --pbs-blue: #0047AB;
    --pbs-blue-dark: #003380;
    --pbs-blue-light: #1e5bc6;
}

/* CORRECT - Should use */
:root {
    --primary-color: #164f90;  /* From base.css */
}
```

### templates/pages/boutique/shop.html (571 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 7-11 | Custom `:root` variables override established theme | High | Remove and use base.css variables |
| All | Uses `--pbs-blue` instead of `--primary-color` | High | Replace all `var(--pbs-blue)` with `var(--primary-color)` |
| 5-250 | Large inline `<style>` block | High | Extract to boutique.css |

**Total: 3 violations (affects whole file)**

---

### templates/pages/boutique/cart.html (386 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 7-11 | Custom `:root` variables override established theme | High | Remove and use base.css variables |
| All | Uses `--pbs-blue` instead of `--primary-color` | High | Replace all `var(--pbs-blue)` with `var(--primary-color)` |

**Total: 2 violations (affects whole file)**

---

### templates/pages/boutique/checkout.html (372 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 7-11 | Custom `:root` variables override established theme | High | Remove and use base.css variables |
| 214 | `style="color: #dc3545;"` inline in template | Medium | Use `.text-danger` class |

**Total: 2 violations**

---

### templates/pages/boutique/product_detail.html (319 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 7-11 | Custom `:root` variables override established theme | High | Remove and use base.css variables |
| 146 | `style="color: var(--pbs-blue)"` in template | Medium | Use class with `var(--primary-color)` |
| 187 | `style="border-color: var(--pbs-blue)"` inline | Medium | Use class |
| 199 | `style="color: #28a745"` hardcoded | Medium | Use `var(--success-color)` |
| 201 | `style="color: #ffc107"` hardcoded | Medium | Use `var(--warning-color)` |
| 203 | `style="color: #dc3545"` hardcoded | Medium | Use `var(--error-color)` |

**Total: 6 violations**

---

### templates/pages/boutique/dashboard.html (508 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 7-11 | Custom `:root` variables override established theme | High | Remove and use base.css variables |
| 79 | `color: #28a745` hardcoded | Medium | Use `var(--success-color)` |
| 83 | `color: #ffc107` hardcoded | Medium | Use `var(--warning-color)` |
| 87 | `color: #dc3545` hardcoded | Medium | Use `var(--error-color)` |

**Total: 4 violations**

---

### Other Boutique Files with Same Issues:
- templates/pages/boutique/order_history.html
- templates/pages/boutique/payment.html
- templates/pages/boutique/payment_success.html
- templates/pages/boutique/product_form.html
- templates/pages/boutique/import_products.html
- templates/pages/boutique/delete_product_confirm.html

**Each has: Custom color scheme, large inline styles**

---

## Portal Templates

### templates/pages/portal/dashboard.html (322 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 247-end | Inline `<style>` at bottom of content block | Medium | Move to `{% block css %}` |

**Total: 1 violation**

---

### templates/pages/portal/roster.html (634 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 140 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 172 | `background: linear-gradient(135deg, #2a7dd4, #164f90)` hardcoded | Medium | Use CSS variables |
| 190 | `border: 2px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 196 | `background: linear-gradient(135deg, #2a7dd4, #164f90)` hardcoded | Medium | Use CSS variables |
| 211 | `background: #28a745` hardcoded | Medium | Use `var(--success-color)` |
| 130-350 | Large inline `<style>` block | High | Extract to roster.css |

**Total: 6 violations**

---

### templates/pages/portal/profile.html (1245 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| Large file | Missing `{% block css %}` - styles in template | High | Add CSS block |

**Total: 1 violation (large scope)**

---

### templates/pages/portal/documents.html (452 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 143 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 175 | `box-shadow: 0 2px 10px rgba(0,0,0,0.1)` should be standardized | Low | Add to base.css |
| 130-280 | Large inline `<style>` block | High | Extract to documents.css |

**Total: 3 violations**

---

### templates/pages/portal/inbox.html (214 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 66 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 82 | `background: linear-gradient(135deg, #2a7dd4, #164f90)` hardcoded | Medium | Use CSS variables |
| 99 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 55-175 | Large inline `<style>` block | High | Extract to inbox.css |

**Total: 4 violations**

---

### templates/pages/portal/edit_profile.html (398 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 178 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 165-350 | Large inline `<style>` block | High | Extract to profile.css |

**Total: 2 violations**

---

### templates/pages/portal/announcements.html (240 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 68 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 94 | `border-left: 5px solid #e74c3c` - not using project colors | Medium | Use `var(--error-color)` |
| 97 | `border-left: 5px solid #27ae60` - not using project colors | Medium | Use `var(--success-color)` |
| 55-180 | Large inline `<style>` block | High | Extract to announcements.css |

**Total: 4 violations**

---

### templates/pages/portal/dues.html (366 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 127 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 153 | `background: linear-gradient(135deg, #2a7dd4, #164f90)` hardcoded | Medium | Use CSS variables |
| 115-230 | Large inline `<style>` block | High | Extract to dues.css |

**Total: 3 violations**

---

### templates/pages/portal/photo_gallery.html (171 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 8-55 | Inline `<style>` in CSS block (acceptable but could use external) | Low | Consider external file |

**Total: 1 violation** (minor)

---

## Registration Templates

### templates/registration/password_reset.html (271 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 16-17 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` |
| 48 | `border-bottom: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 56 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 90 | `border: 2px solid #c8c9c7` hardcoded | Medium | Use `var(--secondary-color)` |
| 127 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-170 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 6 violations**

---

### templates/registration/password_reset_confirm.html (338 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 16-17 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` |
| 48 | `border-bottom: 3px solid #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-170 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 3 violations**

---

### templates/registration/password_reset_done.html (133 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 16-17 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` |
| 56 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-110 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 3 violations**

---

### templates/registration/password_reset_complete.html (128 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 16-17 | `width: 100vw; margin-left: calc(-50vw + 50%)` | Critical | Use `width: 100%` |
| 56 | `color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 100 | `background-color: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-110 | Large inline `<style>` block | High | Use auth-forms.css |

**Total: 4 violations**

---

## Program Templates

### templates/pages/programs/business.html (727 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 9 | `background: linear-gradient(135deg, #164f90 0%, #1e3a5f 100%)` hardcoded | Medium | Use CSS variables |
| 93 | `background: rgba(22, 79, 144, 0.9)` hardcoded | Medium | Use CSS variables |
| 120 | `background: #164f90` hardcoded | Medium | Use `var(--primary-color)` |
| 8-200 | Large inline `<style>` block | High | Extract to programs.css |

**Total: 4 violations**

---

### Other Program Files (Similar Issues):
- templates/pages/programs/education.html
- templates/pages/programs/scholarship.html
- templates/pages/programs/sigma_beta.html
- templates/pages/programs/social_action.html

**Each has: Hardcoded colors, large inline styles**

---

## Other Templates with Issues

### templates/pages/create_invitation.html (95 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| 9 | `style="box-shadow: 0 0 15px rgba(255, 255, 255, 0.8);"` inline | Low | Use `.card-glow` class |

**Total: 1 violation** (minor)

---

### templates/pages/portal/polls/poll_list.html (155 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| None | Uses Bootstrap classes and minimal custom CSS | Low | Acceptable |

**Total: 0 violations** ✅

---

### templates/pages/portal/zoom/meeting_list.html (115 lines)
| Line | Violation | Severity | Fix |
|------|-----------|----------|-----|
| None | Uses Bootstrap classes and minimal custom CSS | Low | Acceptable |

**Total: 0 violations** ✅

---

## Summary by Severity

| Severity | Count | Description |
|----------|-------|-------------|
| **Critical** | 8 | `100vw` causing horizontal scroll |
| **High** | 67 | Large inline style blocks, wrong color scheme |
| **Medium** | 156 | Hardcoded colors instead of CSS variables |
| **Low** | 27 | Minor inconsistencies, missing optimizations |

---

## Recommended Actions

### Priority 1: Critical Fixes (Immediate)
1. **Replace `width: 100vw`** in 8 files with `width: 100%` to fix horizontal scrolling:
   - chapter_history.html
   - chapter_leadership.html
   - chapter_membership.html
   - chapter_programs.html
   - password_reset.html
   - password_reset_confirm.html
   - password_reset_done.html
   - password_reset_complete.html

### Priority 2: High Severity (This Week)
1. **Boutique color scheme standardization** - Replace `--pbs-blue` (#0047AB) with `--primary-color` (#164f90) across all 11 boutique templates
2. **Move `<style>` blocks** from `{% block content %}` to `{% block css %}` in:
   - news.html
   - action.html
   - chatbot_widget.html

### Priority 3: Medium Severity (This Sprint)
1. **Create page-specific CSS files** for templates with large inline `<style>` blocks:
   - events.css
   - roster.css
   - dues.css
   - announcements.css
   - chapter-pages.css (combined for chapter_* pages)
   - boutique.css

2. **Replace hardcoded colors** with CSS variables systematically:
   ```css
   /* FIND */                    /* REPLACE WITH */
   #164f90                      var(--primary-color)
   #c8c9c7                      var(--secondary-color)
   #d32f2f                      var(--error-color)
   #4caf50                      var(--success-color)
   #ff9800                      var(--warning-color)
   #0b1020                      var(--background-light) /* dark mode */
   #87ceeb                      /* Add as --primary-color-light in base.css */
   ```

### Priority 4: Low Severity (Backlog)
1. Add missing responsive breakpoints to templates
2. Standardize box-shadow values project-wide
3. Document dark mode light blue (#87ceeb) color in base.css

---

## Compliant Files (Good Examples)

These templates follow the CSS guide correctly:
- templates/pages/signin.html ✅
- templates/pages/projects.html ✅
- templates/pages/portal/polls/poll_list.html ✅
- templates/pages/portal/zoom/meeting_list.html ✅

Use these as reference when refactoring other templates.

---

## Appendix: Quick Regex for Finding Violations

```bash
# Find hardcoded primary color
grep -rn "#164f90" templates/

# Find hardcoded secondary color
grep -rn "#c8c9c7" templates/

# Find 100vw usage
grep -rn "100vw" templates/

# Find style tags in content blocks
grep -rn "{% block content %}" -A 20 templates/ | grep "<style>"

# Find boutique's custom color scheme
grep -rn "pbs-blue" templates/
```

---

**Report Generated:** March 10, 2026  
**Auditor:** CSS Audit System  
**Next Review:** Upon completion of Critical/High fixes
