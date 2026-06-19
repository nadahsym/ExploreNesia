import pandas as pd

def format_price(price):
    """Mengubah angka harga menjadi format Rupiah atau teks 'Gratis'"""
    if pd.isna(price) or price == 0:
        return "Gratis"
    return f"Rp {int(price):,.0f}".replace(",", ".")

def star_rating(rating):
    """Menghasilkan string bintang berdasarkan nilai float rating"""
    stars = int(round(rating))
    return "⭐" * stars

def category_color(category):
    """Mengembalikan warna hex spesifik berdasarkan kategori wisata"""
    colors = {
        "Budaya": "#ff6b6b",
        "Taman Hiburan": "#ffd93d",
        "Cagar Alam": "#6bcb77",
        "Bahari": "#4d96ff",
        "Pusat Perbelanjaan": "#c77dff",
        "Tempat Ibadah": "#ff9f1c"
    }
    return colors.get(category, "#3a86ff") # Default warna biru
