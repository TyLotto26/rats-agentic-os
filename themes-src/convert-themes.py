#!/usr/bin/env python3
"""Convert tweakcn theme presets to dashboard CSS theme files.
Focuses on dark themes suitable for the Rats Agentic OS dashboard."""

import re, os, json

# Read the TypeScript file
with open("/home/tyreseN/rats-agentic-os/themes-src/theme-presets.ts") as f:
    content = f.read()

# Walk through each theme block
# We'll track depth to find top-level theme objects
lines = content.split('\n')

# Collect all theme blocks
# Pattern: at indent level 2 we have "theme-key": {  ...  },
themes_raw = {}
current_key = None
brace_depth = 0
block_lines = []

for line in lines:
    stripped = line.rstrip()
    indent = len(line) - len(line.lstrip())
    
    # Check for top-level theme key (indent 2)
    m = re.match(r'\s{2}"?([\w-]+)"?\s*:\s*\{', line)
    if m and indent == 2:
        current_key = m.group(1)
        block_lines = [line]
        brace_depth = 1
        continue
    
    if current_key is not None:
        block_lines.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0:
            # End of this theme block
            themes_raw[current_key] = '\n'.join(block_lines)
            current_key = None
            block_lines = []

print(f"Extracted {len(themes_raw)} themes")

def extract_css_vars(block_text, mode='dark'):
    """Extract CSS variable values for a given mode (light/dark)"""
    # Find the mode section
    mode_m = re.search(rf'{mode}:\s*\{{([^}}]+)\}}', block_text)
    if not mode_m:
        return None
    
    mode_text = mode_m.group(1)
    
    # Extract all properties
    props = {}
    for prop_m in re.finditer(r'\"?([\w-]+)\"?:\s*"([^"]*)"', mode_text):
        props[prop_m.group(1)] = prop_m.group(2)
    
    return props

def props_to_dashboard_css(key, label, dark_props, light_props):
    """Convert shadcn props to dashboard CSS theme format"""
    
    bg = dark_props.get('background', '#000000')
    fg = dark_props.get('foreground', '#ffffff')
    primary = dark_props.get('primary', '#3b82f6')
    card_bg = dark_props.get('card', '#171717')
    secondary = dark_props.get('secondary', '#262626')
    muted = dark_props.get('muted', '#1f1f1f')
    border = dark_props.get('border', '#404040')
    accent = dark_props.get('accent', '#1e3a8a')
    
    radius = dark_props.get('radius', '0.5rem')
    
    # Map shadcn colors to dashboard semantic names
    # shadcn: background/foreground/card/popover/primary/secondary/muted/accent/destructive/border/input/ring
    # dashboard: --accent / --bg / --text-* / --red/yellow/etc
    
    # Determine accent color from shadcn primary (for dashboard, primary=accent)
    accent_color = primary
    
    # Build the CSS
    css = f"""/* ═══════════════════════════════════════════
   {label.upper()} — Dark Theme
   Rats on Wallstreet — Agentic OS
   
   Generated from tweakcn shadcn/ui preset
   ═══════════════════════════════════════════ */

[data-theme="{key}"] {{
  /* ── Primary Accent ── */
  --accent: {accent_color};
  --accent-strong: {hex_to_rgba(accent_color, 0.85)};
  --accent-mid: {hex_to_rgba(accent_color, 0.50)};
  --accent-dim: {hex_to_rgba(accent_color, 0.20)};
  --accent-faint: {hex_to_rgba(accent_color, 0.06)};
  --accent-edge: {hex_to_rgba(accent_color, 0.12)};

  /* ── Semantic Colors ── */
  --red: {dark_props.get('destructive', '#ef4444')};
  --yellow: {dark_props.get('chart-3', '#E8B84B')};
  --purple: {dark_props.get('chart-4', '#C084FC')};
  --blue: {dark_props.get('chart-1', '#67B8E8')};
  --orange: {dark_props.get('chart-5', '#E8954B')};
  --green: {dark_props.get('chart-2', '#4ADE80')};

  /* ── Backgrounds ── */
  --bg: {bg};
  --bg-panel: {card_bg};
  --bg-card: {lighten_color(card_bg, 3)};
  --bg-elevated: {lighten_color(card_bg, 6)};

  /* ── Text ── */
  --text-primary: {hex_to_rgba(fg, 0.90)};
  --text-secondary: {hex_to_rgba(fg, 0.60)};
  --text-faint: {hex_to_rgba(fg, 0.25)};
  --text-white: {fg};

  /* ── Ambient glow ── */
  --accent-glow: {hex_to_rgba(accent_color, 0.03)};

  /* ── Kanban lane tints ── */
  --lane-pending: {card_bg};
  --lane-in-progress: {hex_to_rgba(accent_color, 0.08)};
  --lane-completed: {hex_to_rgba(dark_props.get('chart-2', '#4ADE80'), 0.08)};

  /* ── Radius ── */
  --radius: {radius};
}}
"""

    return css

def hex_to_rgba(hex_color, alpha):
    """Convert hex color to rgba string"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c*2 for c in hex_color)
    if len(hex_color) != 6:
        return f"rgba(128, 128, 128, {alpha})"
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def lighten_color(hex_color, percent):
    """Lighten a hex color by a percentage"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c*2 for c in hex_color)
    if len(hex_color) != 6:
        return "#" + hex_color
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r * (1 + percent/100)))
    g = min(255, int(g * (1 + percent/100)))
    b = min(255, int(b * (1 + percent/100)))
    return f"#{r:02x}{g:02x}{b:02x}"

# Themes to convert (dark-focused, dashboard-appropriate)
theme_list = [
    "modern-minimal", "violet-bloom", "twitter", "mocha-mousse",
    "doom-64", "catppuccin", "graphite", "perpetuity",
    "kodama-grove", "cosmic-night", "tangerine", "quantum-rose",
    "nature", "bold-tech", "elegant-luxury", "amber-minimal",
    "neo-brutalism", "solar-dusk", "cyberpunk", "pastel-dreams",
    "caffeine", "ocean-breeze", "retro-arcade", "midnight-bloom",
    "northern-lights", "starry-night", "claude", "vercel",
    "darkmatter", "mono", "soft-pop", "sage-garden",
]

output_dir = "/home/tyreseN/rats-agentic-os/themes"
os.makedirs(output_dir, exist_ok=True)

converted = 0
for key in theme_list:
    if key not in themes_raw:
        continue
    
    block = themes_raw[key]
    
    # Get label
    label_m = re.search(r'label:\s*"([^"]+)"', block)
    label = label_m.group(1) if label_m else key
    
    dark_props = extract_css_vars(block, 'dark')
    if not dark_props:
        continue
    
    light_props = extract_css_vars(block, 'light')
    
    css = props_to_dashboard_css(key, label, dark_props, light_props)
    
    filepath = os.path.join(output_dir, f"{key}.css")
    with open(filepath, 'w') as f:
        f.write(css)
    converted += 1
    print(f"  ✓ {key:25s} → {label}")

print(f"\nConverted {converted}/{len(theme_list)} themes to CSS files in {output_dir}")
