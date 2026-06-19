import base64
import os

SVG_ICONS = {
    "compass": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>',
    "home": '<svg class="{clazz}" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
    "search": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    "package": '<svg class="{clazz}" viewBox="0 0 24 24"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><polygon points="12 22.08 12 12 3 6.92 3 17.08 12 22.08"></polygon><polygon points="12 22.08 21 17.08 21 6.92 12 12 12 22.08"></polygon><polygon points="12 12 21 6.92 12 1.84 3 6.92 12 12"></polygon></svg>',
    "stats": '<svg class="{clazz}" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    "map": '<svg class="{clazz}" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" y1="3" x2="9" y2="18"></line><line x1="15" y1="6" x2="15" y2="21"></line></svg>',
    "semantic": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>',
    "city": '<svg class="{clazz}" viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="9" y1="22" x2="9" y2="16"></line><line x1="15" y1="22" x2="15" y2="16"></line><line x1="9" y1="16" x2="15" y2="16"></line><path d="M8 6h.01M16 6h.01M9 10h.01M15 10h.01M12 6h.01M12 10h.01M8 14h.01M16 14h.01M12 14h.01"></path></svg>',
    "category": '<svg class="{clazz}" viewBox="0 0 24 24"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>',
    "rating": '<svg class="{clazz}" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>',
    "price": '<svg class="{clazz}" viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="2"></circle><path d="M6 12h.01M18 12h.01"></path></svg>',
    "info": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
    "telescope": '<svg class="{clazz}" style="width:48px;height:48px;stroke-width:1.5" viewBox="0 0 24 24"><path d="M10.01 10.01 4 16v5l5-4 5.99-5.99M16.5 7.5l-3 3M19 5l-3 3M15 3l6 6M12 18v3M9 21h6"></path></svg>',
    "plug": '<svg class="{clazz}" style="width:48px;height:48px;stroke-width:1.5" viewBox="0 0 24 24"><path d="M12 2v6M9 8h6M10 12h4M10 18h4M8 12v3a4 4 0 0 0 8 0v-3M12 22v-3"></path></svg>',
    "arrow-right": '<svg class="{clazz}" viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'
}

def get_svg_icon(name: str, clazz: str = "svg-icon") -> str:
    svg_template = SVG_ICONS.get(name, "")
    if svg_template:
        return svg_template.replace("{clazz}", clazz)
    return ""

def get_hero_style(image_path: str, overlay_opacity: float = 0.75, bg_position: str = "center") -> str:
    if os.path.exists(image_path):
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png":
            mime_type = "image/png"
        elif ext == ".webp":
            mime_type = "image/webp"
        elif ext == ".avif":
            mime_type = "image/avif"
        
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            return f"background: linear-gradient(rgba(15, 23, 42, {overlay_opacity}), rgba(15, 23, 42, {overlay_opacity})), url('data:{mime_type};base64,{encoded_string}'); background-size: cover; background-position: {bg_position};"
        except Exception:
            pass
    return ""
