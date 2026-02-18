import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# --- AYARLAR ---
st.set_page_config(page_title="Deposistem Pro", page_icon="📦", layout="wide")

# --- RENYAP KURUMSAL RENK TASARIMI ---
st.markdown("""
    <style>
        /* --- RENK TANIMLARI ---
           Lacivert: #203864 (Başlıklar)
           Sarı:     #FFC000 (Vurgular)
           Kırmızı:  #C00000 (Linkler)
        */

        /* GENEL ARKA PLAN */
        .stApp { background-color: #FFFFFF; }
        
        /* SIDEBAR (SOL MENÜ) - BEYAZ */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF; 
            border-right: 1px solid #e5e7eb;
        }
        
        /* BAŞLIKLAR (H1, H2, H3) - RENYAP LACİVERTİ */
        h1, h2, h3, h4, h5, h6 { 
            color: #203864 !important; /* Lacivert */
            font-weight: 700 !important;
        }
        
        /* NORMAL YAZILAR - SİYAH */
        label, .stMarkdown, p, span, div { 
            color: #000000 !important; 
        }

        /* --- BUTONLAR (KAYDET VB.) --- */
        div.stButton > button {
            background-color: #203864; /* Lacivert Zemin */
            color: #FFFFFF !important; /* Beyaz Yazı */
            border: none;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        /* Butonun Üzerine Gelince (Hover) */
        div.stButton > button:hover {
            background-color: #FFC000; /* Renyap Sarısı */
            color: #203864 !important; /* Lacivert Yazı */
            border: 1px solid #203864;
        }

        /* --- INPUT ALANLARI --- */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] div {
            background-color: #FFFFFF !important;
            border: 1px solid #ced4da;
            color: #000000 !important;
        }
        
        /* Inputa Tıklayınca (Focus) - Lacivert Çerçeve */
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #203864 !important;
            box-shadow: 0 0 0 1px #203864;
        }

        /* KOLONLAR (KUTULAR) */
        div[data-testid="column"] {
            background-color: #FFFFFF; 
            border-radius: 12px; 
            padding: 20px; 
            border: 1px solid #e5e7eb; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* Hafif gölge */
        }

        /* TABLOLAR */
        [data-testid="stDataFrame"] { background-color: #FFFFFF; }

        /* --- MENÜ BUTONLARI --- */
        .stRadio label {
            background-color: #FFFFFF;
            color: #203864 !important; /* Yazılar Lacivert */
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            margin-bottom: 5px;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }

        /* Menü Hover */
        .stRadio label:hover {
            background-color: #FFC000; /* Sarı */
            color: #203864 !important;
            border-color: #203864;
            cursor: pointer;
        }

        /* Seçili Olan Menü (Streamlit'te tam kontrol zordur ama deneriz) */
        .stRadio div[role='radiogroup'] > label[data-baseweb="radio"] {
             /* Standart stil */
        }

        /* LİNKLER - RENYAP KIRMIZISI */
        a { color: #C00000 !important; text-decoration: none; font-weight: bold; }
        
        /* METRİKLER */
        [data-testid="stMetricLabel"] { color: #203864 !important; }
        [data-testid="stMetricValue"] { color: #203864 !important; }
        
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

# --- KAYIT VE FONKSİYONLAR ---
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

# --- LOGO İŞLEMLERİ ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if 'sayfa' not in st.session_state:
    st.session_state.sayfa = "🏠 Ana Sayfa"

if os.path.exists("logo.jpeg"):
    try:
        img_str = get_base64_image("logo.jpeg")
        # Logoya tıklayınca Ana Sayfaya döner
        logo_html = f'''
        <a href="" target="_self">
            <img src="data:image/jpeg;base64,{img_str}" width="100%" style="border-radius:10px; margin-bottom:20px;">
        </a>
        '''
        st.sidebar.markdown(logo_html, unsafe_allow_html=True)
    except:
        st.sidebar.warning("Logo Hatası")

# MENÜ SEÇENEKLERİ
secenekler = ["🏠 Ana Sayfa", "📋 Envanter", "🚚 Tedarik", "↩️ İade", "📈 Analiz"]

try: index_no = secenekler.index(st.session_state.sayfa)
except: index_no = 0

menu = st.sidebar.radio("MENÜ", secenekler, index=index_no, label_visibility="collapsed")

if menu != st.session_state.sayfa:
    st.session_state.sayfa = menu
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 [www.renyap.com](https://www.renyap.com)")

# ================= ANA SAYFA =================
if st.session_state.sayfa == "🏠 Ana Sayfa":
    st.title("👋 Yönetim Paneli")
    st.markdown("---")
    
    toplam_cesit = len(st.session_state.envanter)
    try: toplam_stok = st.session_state.envanter["Güncel Stok"].sum()
    except: toplam_stok = 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Çeşit", f"{toplam_cesit}")
    m2.metric("Toplam Stok", f"{toplam_stok}")
    m3.metric("Kayıt Durumu", "✅ Excel")
    
    st.markdown("### 🚀 Hızlı Erişim")
    c1, c2 = st.columns(2)
    with c1:
        st.info("📋 **Envanter:** Ürün listesi ve stok raporu.")
        st.warning("🚚 **Tedarik:** Mal kabul ve stok girişi.")
    with c2:
        st.error("↩️ **İade:** Müşteri iadeleri ve hasar kaydı.")
        st.success("📈 **Analiz:** Kar/Zarar ve maliyet hesaplama.")

# ================= ENVANTER =================
elif st.session_state.sayfa == "📋 Envanter":
    st.header("📋 Envanter Yönetimi")
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
elif st.session_state.sayfa == "🚚 Tedarik":
    st.header("🚚 Tedarik Girişi")
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
elif st.session_state.sayfa == "↩️ İade":
    st.header("↩️ İade İşlemleri")
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
elif st.session_state.sayfa == "📈 Analiz":
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
            st.markdown(f"<div style='background-color:#FFFFFF; padding:15px; border-left:5px solid {color}; border:1px solid #e5e7eb; border-radius:10px;'><h3 style='color:{color}; margin:0;'>Net Kar: {net:.2f} TL</h3></div>", unsafe_allow_html=True)
    with t2:
        kur = st.number_input("Kur", 32.50)
        fiyat = st.number_input("Fiyat ($)", 100.0)
        isk = st.number_input("İskonto %", 10.0)
        st.metric("TL Maliyet", f"{(fiyat - (fiyat*isk/100)) * kur:.2f} ₺")
