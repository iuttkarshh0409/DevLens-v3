from fastapi import APIRouter, Query, Response
from typing import Optional
import hashlib

router = APIRouter(prefix="/api", tags=["badges"])

# Simple in-memory cache to prevent re-generating SVG nodes
badge_cache = {}

def generate_svg_badge(label: str, val_str: str, color: str, style: str = "flat") -> str:
    """Generates a Shields.io style SVG badge locally."""
    # Compute widths based on text length (crude approximation for pixel width)
    label_width = len(label) * 6 + 12
    val_width = len(val_str) * 6 + 12
    total_width = label_width + val_width

    # Style templates
    if style == "flat-square":
        rx = "0"
    elif style == "plastic":
        rx = "4"
    else:  # flat
        rx = "3"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="{total_width}" height="20" rx="{rx}" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{val_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + val_width / 2}" y="15" fill="#010101" fill-opacity=".3">{val_str}</text>
    <text x="{label_width + val_width / 2}" y="14">{val_str}</text>
  </g>
</svg>"""
    return svg

@router.get("/badge")
async def get_badge(
    label: str = Query("devlens", description="Left side badge label"),
    value: str = Query("audit", description="Right side value"),
    metric: Optional[str] = Query(None, description="E.g. 'score' or 'status'"),
    color: Optional[str] = Query(None, description="Custom hex color or name"),
    style: str = Query("flat", description="Badge style: flat, flat-square, plastic")
):
    # Determine color by default metrics if provided
    badge_color = color or "#4c1"  # Default green
    
    if metric == "score":
        try:
            score_val = float(value)
            if score_val >= 9.0:
                badge_color = "#4c1" # bright green
            elif score_val >= 7.0:
                badge_color = "#a4a61d" # yellow green
            elif score_val >= 5.0:
                badge_color = "#dfb317" # yellow
            else:
                badge_color = "#e05d44" # red
        except ValueError:
            pass
    elif metric == "status":
        if value.lower() in ["passed", "success", "healthy"]:
            badge_color = "#4c1"
        else:
            badge_color = "#e05d44"

    # Cache key
    cache_key = hashlib.md5(f"{label}:{value}:{badge_color}:{style}".encode()).hexdigest()
    if cache_key in badge_cache:
        return Response(content=badge_cache[cache_key], media_type="image/svg+xml")

    svg_content = generate_svg_badge(label, value, badge_color, style)
    badge_cache[cache_key] = svg_content
    return Response(content=svg_content, media_type="image/svg+xml")
