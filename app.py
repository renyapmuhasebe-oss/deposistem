import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- AYARLAR ---
st.set_page_config(page_title="Deposistem Pro", page_icon="📦", layout="wide")

# --- TASARIM (BEYAZ TEMA & MENÜ DÜZENİ) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #dee2e6; }
        h1, h2, h3, .streamlit-expanderHeader, label, .stMarkdown { color: #212529 !important; }
        [data-testid="stMetricValue"] { color: #000000 !important; }
        a { color: #0d6efd !important; text-decoration: none; }
        
        /* Dashboard Kartları */
        div[data-testid="column"] {
            background-color: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #dee2e6;
        }
        
        /* Sol Menüdeki Radyo Butonlarını Güzelleştirme */
        .stRadio > div { gap: 10px; }
        .stRadio label { font-size: 16px !important; font-weight: 500 !important; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# --- DOSYA İSİMLERİ ---
FILE_ENVANTER = "envanter.xlsx"
FILE_TEDARIK = "tedarik.xlsx"
FILE_IADE = "iade.xlsx"

# --- VERİ YÜKLEME ---
if 'envanter' not in st.session_state:
    if os.path.exists(FILE_ENVANTER): st.session_state.envanter = pd.read_excel(FILE_ENVANTER)
    else: st.session_state.envanter = pd.DataFrame(columns=["Ürün Adı", "Ürün Kodu", "Tedarikçi Blok", "Güncel Stok"])

if 'tedarik' not in st.session_state:
    if os.path.exists(FILE_TEDARIK): st.session_state.tedarik = pd.read_excel(FILE_TEDARIK)
    else: st.session_state.tedarik = pd.DataFrame(columns=["Stok Adı", "Stok Kodu", "Adet", "Tedarikçi", "Tarih"])

if 'iade' not in st.session_state:
    if os.path.exists(FILE_IADE): st.session_state.iade = pd.read_excel(FILE_IADE)
    else: st.session_state.iade = pd.DataFrame(columns=["Müşteri Adı", "Ürün Adı", "Sipariş No", "Adet", "Hasar Durumu", "Tarih"])

def verileri_kaydet():
    st.session_state.envanter.to_excel(FILE_ENVANTER, index=False)
    st.session_state.tedarik.to_excel(FILE_TEDARIK, index=False)
    st.session_state.iade.to_excel(FILE_IADE, index=False)

def stok_guncelle(urun_adi, adet, islem_tipi="ekle"):
    if not st.session_state.envanter.empty:
        idx = st.session_state.envanter[st.session_state.envanter["Ürün Adı"] == urun_adi].index
        if not idx.empty:
            idx = idx[0]
            mevcut = int(st.session_state.envanter.at[idx, "Güncel Stok"])
            yeni = mevcut + int(adet) if islem_tipi == "ekle" else max(0, mevcut - int(adet))
            st.session_state.envanter.at[idx, "Güncel Stok"] = yeni
            verileri_kaydet()
            return True
    return False

# --- SOL MENÜ TASARIMI ---
if os.path.exists("logo.jpeg"):
    try:
        st.sidebar.image(Image.open("logo.jpeg"), use_container_width=True)
    except: pass

st.sidebar.write("---") # Çizgi

# BURASI DEĞİŞTİ: Selectbox yerine Radio kullanıldı
menu = st.sidebar.radio(
    "MENÜ", 
    ["🏠 Ana Sayfa", "📋 Envanter Bölümü", "🚚 Tedarik Bölümü", "↩️ İade Bölümü", "📈 Analiz Bölümü"],
    label_visibility="collapsed" # Başlığı gizle, sade görünsün
)

st.sidebar.write("---")
st.sidebar.caption("Deposistem v2.1")
st.sidebar.markdown("🌐 [www.renyap.com](https://www.renyap.com)")

# ================= ANA SAYFA =================
if menu == "🏠 Ana Sayfa":
    st.title("👋 Yönetim Paneli")
    
    toplam_cesit = len(st.session_state.envanter)
    try: toplam_stok = st.session_state.envanter["Güncel Stok"].sum()
    except: toplam_stok = 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Çeşit", f"{toplam_cesit}")
    m2.metric("Toplam Stok", f"{toplam_stok}")
    m3.metric("Kayıt Durumu", "✅ Excel")
    
    st.markdown("### Hızlı Erişim")
    c1, c2 = st.columns(2)
    with c1:
        st.info("📋 **Envanter:** Ürün listesi ve stok raporu.")
        st.warning("🚚 **Tedarik:** Mal kabul ve stok girişi.")
    with c2:
        st.error("↩️ **İade:** Müşteri iadeleri ve hasar kaydı.")
        st.success("📈 **Analiz:** Kar/Zarar ve maliyet hesaplama.")

# ================= ENVANTER =================
elif menu == "📋 Envanter Bölümü":
    st.header("📋 Envanter")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Ürün Ekle")
        with st.form("inv"):
            ad = st.text_input("Ürün Adı")
            kod = st.text_input("Kod")
            ted = st.text_input("Tedarikçi")
            stok = st.number_input("Stok", min_value=0)
            if st.form_submit_button("Ekle") and ad:
                if ad not in st.session_state.envanter["Ürün Adı"].values:
                    yen = pd.DataFrame({"Ürün Adı": [ad], "Ürün Kodu": [kod], "Tedarikçi Blok": [ted], "Güncel Stok": [stok]})
                    st.session_state.envanter = pd.concat([st.session_state.envanter, yen], ignore_index=True)
                    verileri_kaydet()
                    st.success("Eklendi")
                else: st.error("Mevcut!")
    with c2:
        st.dataframe(st.session_state.envanter, use_container_width=True)
        with open(FILE_ENVANTER, "rb") as f: st.download_button("Excel İndir", f, "envanter.csv")

# ================= TEDARİK =================
elif menu == "🚚 Tedarik Bölümü":
    st.header("🚚 Tedarik")
    if not st.session_state.envanter.empty:
        with st.form("ted"):
            urn = st.selectbox("Ürün", st.session_state.envanter["Ürün Adı"].unique())
            kod = st.session_state.envanter[st.session_state.envanter["Ürün Adı"] == urn]["Ürün Kodu"].values[0]
            st.text_input("Kod", value=kod, disabled=True)
            adet = st.number_input("Adet", min_value=1)
            firma = st.text_input("Firma")
            if st.form_submit_button("Giriş") and urn:
                yeni = pd.DataFrame({"Stok Adı": [urn], "Stok Kodu": [kod], "Adet": [adet], "Tedarikçi": [firma], "Tarih": [datetime.now().strftime("%d-%m-%Y")]})
                st.session_state.tedarik = pd.concat([st.session_state.tedarik, yeni], ignore_index=True)
                stok_guncelle(urn, adet, "ekle")
                st.success("Kaydedildi")
        st.divider()
        st.dataframe(st.session_state.tedarik.sort_index(ascending=False), use_container_width=True)
    else: st.warning("Önce ürün ekleyin.")

# ================= İADE =================
elif menu == "↩️ İade Bölümü":
    st.header("↩️ İade")
    if not st.session_state.envanter.empty:
        c1, c2 = st.columns(2)
        with c1:
            with st.form("iad"):
                mus = st.text_input("Müşteri")
                sip = st.text_input("Sipariş No")
                urn = st.selectbox("Ürün", st.session_state.envanter["Ürün Adı"].unique())
                adet = st.number_input("Adet", min_value=1)
                hasar = st.selectbox("Durum", ["Hasarsız", "Hasarlı"])
                ekle = st.checkbox("Stoğa Ekle", value=True)
                if st.form_submit_button("Kaydet") and mus:
                    yeni = pd.DataFrame({"Müşteri Adı": [mus], "Ürün Adı": [urn], "Sipariş No": [sip], "Adet": [adet], "Hasar Durumu": [hasar], "Tarih": [datetime.now().strftime("%d-%m-%Y")]})
                    st.session_state.iade = pd.concat([st.session_state.iade, yeni], ignore_index=True)
                    if ekle: stok_guncelle(urn, adet, "ekle")
                    verileri_kaydet()
                    st.success("Kaydedildi")
        with c2: st.dataframe(st.session_state.iade.sort_index(ascending=False), use_container_width=True)
    else: st.warning("Önce ürün ekleyin.")

# ================= ANALİZ =================
elif menu == "📈 Analiz Bölümü":
    st.header("📈 Analiz")
    t1, t2 = st.tabs(["💰 Pazaryeri", "💱 Döviz"])
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
            st.metric("Ciro", f"{satis-kesinti:.2f} TL")
            st.markdown(f"<h3 style='color:{color}'>Net Kar: {net:.2f} TL</h3>", unsafe_allow_html=True)
    with t2:
        kur = st.number_input("Kur", 32.50)
        fiyat = st.number_input("Fiyat ($)", 100.0)
        isk = st.number_input("İskonto %", 10.0)
        st.metric("TL Maliyet", f"{(fiyat - (fiyat*isk/100)) * kur:.2f} ₺")
