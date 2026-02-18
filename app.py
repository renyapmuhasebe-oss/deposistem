import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- AYARLAR VE BAŞLIK ---
st.set_page_config(page_title="Deposistem Pro", page_icon="📦", layout="wide")

# --- TASARIM AYARLARI ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #F8F9FA; }
        h1, h2, h3, .streamlit-expanderHeader, label, .stMarkdown { color: #212529 !important; }
        [data-testid="stMetricValue"] { color: #000000 !important; }
        [data-testid="stMetricLabel"] { color: #6c757d !important; }
        a { color: #0d6efd !important; text-decoration: none; }
        div[data-testid="column"] {
            background-color: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #dee2e6;
        }
    </style>
""", unsafe_allow_html=True)

# --- DOSYA İSİMLERİ ---
FILE_ENVANTER = "envanter.xlsx"
FILE_TEDARIK = "tedarik.xlsx"
FILE_IADE = "iade.xlsx"

# --- VERİ YÜKLEME VE KAYDETME FONKSİYONLARI ---
def verileri_yukle():
    """Excel dosyaları varsa yükler, yoksa boş DataFrame oluşturur."""
    # Envanter
    if os.path.exists(FILE_ENVANTER):
        st.session_state.envanter = pd.read_excel(FILE_ENVANTER)
    elif 'envanter' not in st.session_state:
        st.session_state.envanter = pd.DataFrame(columns=["Ürün Adı", "Ürün Kodu", "Tedarikçi Blok", "Güncel Stok"])
        
    # Tedarik
    if os.path.exists(FILE_TEDARIK):
        st.session_state.tedarik = pd.read_excel(FILE_TEDARIK)
    elif 'tedarik' not in st.session_state:
        st.session_state.tedarik = pd.DataFrame(columns=["Stok Adı", "Stok Kodu", "Adet", "Tedarikçi", "Tarih"])
        
    # İade
    if os.path.exists(FILE_IADE):
        st.session_state.iade = pd.read_excel(FILE_IADE)
    elif 'iade' not in st.session_state:
        st.session_state.iade = pd.DataFrame(columns=["Müşteri Adı", "Ürün Adı", "Sipariş No", "Adet", "Hasar Durumu", "Tarih"])

def verileri_kaydet():
    """Tüm tabloları Excel'e kaydeder."""
    st.session_state.envanter.to_excel(FILE_ENVANTER, index=False)
    st.session_state.tedarik.to_excel(FILE_TEDARIK, index=False)
    st.session_state.iade.to_excel(FILE_IADE, index=False)

# Program açılışında verileri yükle
verileri_yukle()

# --- LOGO ALANI ---
if os.path.exists("logo.jpeg"):
    try:
        image = Image.open("logo.jpeg")
        st.sidebar.image(image, use_container_width=True)
    except:
        st.sidebar.warning("Logo yüklenemedi.")

st.sidebar.title("Menü")

# --- STOK GÜNCELLEME ---
def stok_guncelle(urun_adi, adet, islem_tipi="ekle"):
    if not st.session_state.envanter.empty:
        idx = st.session_state.envanter[st.session_state.envanter["Ürün Adı"] == urun_adi].index
        if not idx.empty:
            idx = idx[0]
            mevcut = int(st.session_state.envanter.at[idx, "Güncel Stok"])
            yeni = mevcut + int(adet) if islem_tipi == "ekle" else max(0, mevcut - int(adet))
            st.session_state.envanter.at[idx, "Güncel Stok"] = yeni
            verileri_kaydet() # Değişikliği anında kaydet
            return True
    return False

# --- YAN MENÜ ---
menu = st.sidebar.selectbox("Bölümler", ["🏠 Ana Sayfa", "📋 Envanter Bölümü", "🚚 Tedarik Bölümü", "↩️ İade Bölümü", "📈 Analiz Bölümü"])

# ================= ANA SAYFA =================
if menu == "🏠 Ana Sayfa":
    st.title("👋Renyap Depo")
    st.markdown("### Depo Durum Özeti")
    
    toplam_cesit = len(st.session_state.envanter)
    try: toplam_stok = st.session_state.envanter["Güncel Stok"].sum()
    except: toplam_stok = 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Ürün Çeşidi", f"{toplam_cesit} Adet")
    m2.metric("Toplam Stok Miktarı", f"{toplam_stok} Adet")
    m3.metric("Kayıt Sistemi", "Aktif (Excel)")
    
    st.info("💾 **Bilgi:** Tüm verileriniz otomatik olarak Excel dosyalarına kaydedilmektedir.")

# ================= ENVANTER BÖLÜMÜ =================
elif menu == "📋 Envanter Bölümü":
    st.header("📋 Envanter Yönetimi")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Yeni Ürün")
        with st.form("inv_form"):
            ad = st.text_input("Ürün Adı")
            kod = st.text_input("Kod")
            ted = st.text_input("Tedarikçi")
            stok = st.number_input("Stok", min_value=0)
            if st.form_submit_button("Kaydet") and ad:
                if ad in st.session_state.envanter["Ürün Adı"].values:
                    st.error("Mevcut!")
                else:
                    yen = pd.DataFrame({"Ürün Adı": [ad], "Ürün Kodu": [kod], "Tedarikçi Blok": [ted], "Güncel Stok": [stok]})
                    st.session_state.envanter = pd.concat([st.session_state.envanter, yen], ignore_index=True)
                    verileri_kaydet() # KAYDET
                    st.success("Kaydedildi.")
    with c2:
        st.dataframe(st.session_state.envanter, use_container_width=True)
        with open(FILE_ENVANTER, "rb") as f:
            st.download_button("Excel İndir", f, file_name="envanter.csv")

# ================= TEDARİK BÖLÜMÜ =================
elif menu == "🚚 Tedarik Bölümü":
    st.header("🚚 Tedarik Girişi")
    if st.session_state.envanter.empty: st.warning("Önce ürün ekleyin.")
    else:
        with st.form("ted_form"):
            urn = st.selectbox("Ürün", st.session_state.envanter["Ürün Adı"].unique())
            kod = st.session_state.envanter[st.session_state.envanter["Ürün Adı"] == urn]["Ürün Kodu"].values[0]
            st.text_input("Kod", value=kod, disabled=True)
            adet = st.number_input("Adet", min_value=1)
            firma = st.text_input("Firma")
            if st.form_submit_button("Giriş Yap"):
                yeni = pd.DataFrame({"Stok Adı": [urn], "Stok Kodu": [kod], "Adet": [adet], "Tedarikçi": [firma], "Tarih": [datetime.now().strftime("%Y-%m-%d")]})
                st.session_state.tedarik = pd.concat([st.session_state.tedarik, yeni], ignore_index=True)
                stok_guncelle(urn, adet, "ekle")
                verileri_kaydet() # KAYDET
                st.success("Stok güncellendi ve kaydedildi.")
        st.divider()
        st.dataframe(st.session_state.tedarik.sort_index(ascending=False), use_container_width=True)

# ================= İADE BÖLÜMÜ =================
elif menu == "↩️ İade Bölümü":
    st.header("↩️ İade İşlemleri")
    if st.session_state.envanter.empty: st.warning("Ürün yok.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            with st.form("iad_form"):
                mus = st.text_input("Müşteri")
                sip = st.text_input("Sipariş No")
                urn = st.selectbox("Ürün", st.session_state.envanter["Ürün Adı"].unique())
                adet = st.number_input("Adet", min_value=1)
                hasar = st.selectbox("Durum", ["Hasarsız", "Hasarlı"])
                ekle = st.checkbox("Stoğa Ekle", value=True)
                if st.form_submit_button("Kaydet") and mus:
                    yeni = pd.DataFrame({"Müşteri Adı": [mus], "Ürün Adı": [urn], "Sipariş No": [sip], "Adet": [adet], "Hasar Durumu": [hasar], "Tarih": [datetime.now().strftime("%Y-%m-%d")]})
                    st.session_state.iade = pd.concat([st.session_state.iade, yeni], ignore_index=True)
                    if ekle: stok_guncelle(urn, adet, "ekle")
                    verileri_kaydet() # KAYDET
                    st.success("İade kaydedildi.")
        with c2:
            st.dataframe(st.session_state.iade.sort_index(ascending=False), use_container_width=True)

# ================= ANALİZ BÖLÜMÜ =================
elif menu == "📈 Analiz Bölümü":
    st.header("📈 Hesaplama Araçları")
    t1, t2 = st.tabs(["💰 Pazaryeri Kar Analizi", "💱 Döviz Hesaplama"])
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            alis = st.number_input("Alış", 100.0)
            satis = st.number_input("Satış", 250.0)
            kargo = st.number_input("Kargo", 40.0)
            kom = st.number_input("Komisyon %", 20.0)
        with c2:
            kesinti = satis * (kom/100) + kargo
            net = satis - kesinti - alis
            color = "green" if net > 0 else "red"
            st.metric("Ciro (Ele Geçen)", f"{satis-kesinti:.2f} TL")
            st.markdown(f"<h3 style='color:{color}'>Net Kar: {net:.2f} TL</h3>", unsafe_allow_html=True)
    with t2:
        c1, c2 = st.columns(2)
        with c1:
            kur = st.number_input("Kur", 32.50)
            fiyat = st.number_input("Döviz Fiyat", 100.0)
            isk = st.number_input("İskonto %", 10.0)
        with c2:
            st.metric("TL Maliyet", f"{(fiyat - (fiyat*isk/100)) * kur:.2f} ₺")

st.sidebar.markdown("---")
st.sidebar.markdown("🌐 [www.renyap.com](https://www.renyap.com)")
