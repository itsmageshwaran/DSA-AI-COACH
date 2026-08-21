# Theme System Architecture & Guidelines: DSA AI Coach

## 1. Overview

The **DSA AI Coach** implements a **System-First Design Token Theme Architecture** adhering to the "Calm Intelligence" design philosophy. The application supports three theme modes:
1. **Light Mode (`light`)**: Clean, high-clarity daylight palette with subtle slate borders and neutral zinc surfaces.
2. **Dark Mode (`dark`)**: Low-fatigue dark palette with elevated charcoal cards and midnight background.
3. **System Preference (`system`)**: Dynamically synchronizes with the user's OS color scheme (`prefers-color-scheme: dark`) and automatically reacts to OS theme changes in real-time.

---

## 2. Zero-FOUT (Flash of Unstyled Theme) Engine

To eliminate theme flashing (FOUT) before React hydrates:
1. An inline blocking script is embedded directly into `frontend/index.html` within the `<head>` tag.
2. It synchronously parses `localStorage.getItem('dsa-ui-theme')`.
3. If set to `dark`, or if set to `system` (or unset) and `window.matchMedia('(prefers-color-scheme: dark)').matches` is true, it immediately injects the `.dark` class onto `document.documentElement` before any CSS or JS bundles render.

```html
<!-- In frontend/index.html -->
<script>
  (function() {
    try {
      const stored = localStorage.getItem('dsa-ui-theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (stored === 'dark' || (!stored && prefersDark) || (stored === 'system' && prefersDark)) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (e) {}
  })();
</script>
```

---

## 3. Design Token Architecture (CSS Variables)

Tokens are declared semantically in `frontend/src/index.css` under `:root` and `.dark`, and exposed to Tailwind CSS v4 via `@theme`:

| Semantic Token | Light Mode Value | Dark Mode Value | Usage |
| :--- | :--- | :--- | :--- |
| `--background` | `#f8fafc` (Slate 50) | `#0a0b0e` (Deep Midnight) | Global app canvas background |
| `--surface` | `#ffffff` (Pure White) | `#111318` (Surface Charcoal) | Main content cards, sidebars, headers |
| `--surface-muted` | `#f1f5f9` (Slate 100) | `#1a1d24` (Subtle Charcoal) | Input backgrounds, inactive chips, code blocks |
| `--surface-hover` | `#e2e8f0` (Slate 200) | `#232731` (Hover Charcoal) | Interactive button/item hover states |
| `--border` | `#e2e8f0` (Slate 200) | `#232731` (Muted Slate) | Dividers, card strokes, container borders |
| `--text-primary` | `#0f172a` (Slate 900) | `#f8fafc` (Slate 50) | Main headings, primary copy |
| `--text-secondary` | `#475569` (Slate 600) | `#94a3b8` (Slate 400) | Secondary labels, descriptions, metadata |
| `--text-muted` | `#94a3b8` (Slate 400) | `#64748b` (Slate 500) | Inactive labels, placeholder text |
| `--accent` | `#2563eb` (Blue 600) | `#3b82f6` (Blue 500) | Primary interactive actions, active states |
| `--success` | `#16a34a` (Green 600) | `#22c55e` (Green 500) | Passed tests, completed lessons |
| `--warning` | `#d97706` (Amber 600) | `#f59e0b` (Amber 500) | Medium difficulty, pending items |
| `--error` | `#dc2626` (Red 600) | `#ef4444` (Red 500) | Compilation errors, failed tests |

---

## 4. Component Usage & Theme Context

### `useTheme()` Hook
```tsx
import { useTheme } from '../features/theme/ThemeContext';

function MyComponent() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  // theme: 'light' | 'dark' | 'system'
  // resolvedTheme: 'light' | 'dark'
}
```

### Monaco Editor Dynamic Theme Binding
In `frontend/src/pages/ProblemWorkspacePage.tsx`:
```tsx
<Editor
  height="100%"
  defaultLanguage="python"
  theme={resolvedTheme === 'dark' ? 'vs-dark' : 'vs'}
  value={code}
  onChange={(value) => setCode(value || '')}
/>
```

### `<ThemeToggle />` Component
- Supports two display variants:
  - `segmented` (default): 3-way toggle (☀ Light, ◐ System, 🌙 Dark).
  - `icon-button`: Compact cyclical toggle.
- Integrated into:
  - Top Navigation Header (`DashboardLayout.tsx`)
  - Bottom Sidebar (`DashboardLayout.tsx`)
  - Workspace Header (`ProblemWorkspacePage.tsx`)
  - Auth Page (`AuthPage.tsx`)
  - Onboarding Page (`OnboardingPage.tsx`)

---

## 5. Accessibility & Contrast (WCAG 2.2 AA)

1. **Socratic Coach Micro-Cards**:
   - `Observation` card: `bg-amber-500/10 border-amber-500/25` with `text-amber-900` in light mode and `text-amber-100` in dark mode.
   - `Probing Question` card: `bg-cyan-500/10 border-cyan-500/30` with `text-cyan-900` in light mode and `text-cyan-100` in dark mode.
   - `Actionable Hint` card: `bg-emerald-500/10 border-emerald-500/25` with `text-emerald-900` in light mode and `text-emerald-100` in dark mode.
2. **Text Contrast Ratios**:
   - Primary Headings: > 14:1 contrast ratio against `--background`.
   - Secondary Text: > 6:1 contrast ratio against `--surface`.
   - Interactive elements and focus rings: 3:1 focus ring with `--ring` token.
