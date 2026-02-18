import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- AYARLAR VE BAŞLIK ---
st.set_page_config(page_title="Deposistem Pro", page_icon="📦", layout="wide")

# --- TASARIM AYARLARI (BEYAZ TEMA & KART TASARIMLARI) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #F8F9FA; }
        h1, h2, h3, .streamlit-expanderHeader, label, .stMarkdown { color: #212529 !important; }
        [data-testid="stMetricValue"] { color: #000000 !important; }
        [data-testid="stMetricLabel"] { color: #6c757d !important; }
        a { color: #0d6efd !important; text-decoration: none; }
        
        /* Dashboard Kartları İçin Stil */
        div[data-testid="column"] {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #dee2e6;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO VE BAŞLIK ALANI ---
if os.path.exists("logo.jpeg"):
    st.sidebar.image("logo.jpeg", use_container_width=True)
else:
    st.sidebar.warning("Logo bulunamadı.")

st.sidebar.title("Menü")

# --- VERİ TABANI SİMÜLASYONU ---
if 'envanter' not in st.session_state:
    st.session_state.envanter = pd.DataFrame(columns=["Ürün Adı", "Ürün Kodu", "Tedarikçi Blok", "Güncel Stok"])
if 'tedarik' not in st.session_state:
    st.session_state.tedarik = pd.DataFrame(columns=["Stok Adı", "Stok Kodu", "Adet", "Tedarikçi", "Tarih"])
if 'iade' not in st.session_state:
    st.session_state.iade = pd.DataFrame(columns=["Müşteri Adı", "Ürün Adı", "Sipariş No", "Adet", "Hasar Durumu", "Tarih"])

# --- STOK GÜNCELLEME FONKSİYONU ---
def stok_guncelle(urun_adi, adet, islem_tipi="ekle"):
    if not st.session_state.envanter.empty:
        idx = st.session_state.envanter[st.session_state.envanter["Ürün Adı"] == urun_adi].index
        if not idx.empty:
            idx = idx[0]
            mevcut = int(st.session_state.envanter.at[idx, "Güncel Stok"])
            yeni = mevcut + int(adet) if islem_tipi == "ekle" else max(0, mevcut - int(adet))
            st.session_state.envanter.at[idx, "Güncel Stok"] = yeni
            return True
    return False

# --- YAN MENÜ ---
menu = st.sidebar.selectbox("Bölümler", 
                            ["🏠 Ana Sayfa", "📋 Envanter Bölümü", "🚚 Tedarik Bölümü", "↩️ İade Bölümü", "📈 Analiz Bölümü"])

# ================= ANA SAYFA (DASHBOARD) =================
if menu == "🏠 Ana Sayfa":
    st.title("👋 Hoş Geldiniz, Renyap Depo Yönetimi")
    st.markdown("### Depo Durum Özeti")
    
    toplam_cesit = len(st.session_state.envanter)
    try:
        toplam_stok = st.session_state.envanter["Güncel Stok"].sum()
    except:
        toplam_stok = 0
        
    son_hareket = datetime.now().strftime("%d-%m-%Y")

    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Ürün Çeşidi", f"{toplam_cesit} Adet", "Envanter")
    m2.metric("Toplam Stok Miktarı", f"{toplam_stok} Adet", "Depo")
    m3.metric("Sistem Tarihi", son_hareket)

    st.markdown("---")
    st.subheader("🚀 Modül Tanıtımları")

    c1, c2 = st.columns(2)
    with c1:
        st.info("📋 **Envanter Bölümü**")
        st.write("Ürün listesi, stok durumu ve excel raporlama.")
        st.warning("🚚 **Tedarik Bölümü**")
        st.write("Mal kabul ve otomatik stok artırma.")
    with c2:
        st.error("↩️ **İade Bölümü**")
        st.write("İade kabul ve hasar kontrolü.")
        st.success("📈 **Analiz Bölümü**")
        st.write("Kur maliyeti ve Pazaryeri Kar/Zarar analizi.")

# ================= ENVANTER BÖLÜMÜ =================
elif menu == "📋 Envanter Bölümü":
    st.header("📋 Envanter Yönetimi")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Yeni Ürün Ekle")
        with st.form("envanter_form"):
            u_adi = st.text_input("Ürün Adı")
            u_kodu = st.text_input("Ürün Kodu")
            t_blok = st.text_input("Tedarikçi Blok")
            baslangic_stok = st.number_input("Başlangıç Stoğu", min_value=0, value=0)
            submit = st.form_submit_button("Kaydet")
            if submit and u_adi:
                if u_adi in st.session_state.envanter["Ürün Adı"].values:
                    st.error("Kayıtlı ürün!")
                else:
                    yeni = pd.DataFrame({"Ürün Adı": [u_adi], "Ürün Kodu": [u_kodu], "Tedarikçi Blok": [t_blok], "Güncel Stok": [baslangic_stok]})
                    st.session_state.envanter = pd.concat([st.session_state.envanter, yeni], ignore_index=True)
                    st.success("Eklendi.")
    with col2:
        st.subheader("Mevcut Liste")
        st.dataframe(st.session_state.envanter, use_container_width=True)
        if not st.session_state.envanter.empty:
            st.download_button("Excel İndir", data=st.session_state.envanter.to_csv().encode('utf-8'), file_name="envanter.csv")

# ================= TEDARİK BÖLÜMÜ =================
elif menu == "🚚 Tedarik Bölümü":
    st.header("🚚 Tedarik Girişi")
    if st.session_state.envanter.empty:
        st.warning("Önce Envanterden ürün ekleyin.")
    else:
        with st.form("tedarik_form"):
            urunler = st.session_state.envanter["Ürün Adı"].unique()
            secilen = st.selectbox("Stok Adı", urunler)
            kod = st.session_state.envanter[st.session_state.envanter["Ürün Adı"] == secilen]["Ürün Kodu"].values[0]
            st.text_input("Stok Kodu", value=kod, disabled=True)
            adet = st.number_input("Adet", min_value=1)
            tedarikci = st.text_input("Tedarikçi")
            if st.form_submit_button("Kaydet"):
                yeni = pd.DataFrame({"Stok Adı": [secilen], "Stok Kodu": [kod], "Adet": [adet], "Tedarikçi": [tedarikci], "Tarih": [datetime.now().strftime("%Y-%m-%d")]})
                st.session_state.tedarik = pd.concat([st.session_state.tedarik, yeni], ignore_index=True)
                stok_guncelle(secilen, adet, "ekle")
                st.success("Stok güncellendi.")
        st.divider()
        st.dataframe(st.session_state.tedarik.sort_index(ascending=False), use_container_width=True)

# ================= İADE BÖLÜMÜ =================
elif menu == "↩️ İade Bölümü":
    st.header("↩️ İade İşlemleri")
    if st.session_state.envanter.empty:
        st.warning("Ürün yok.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            with st.form("iade_form"):
                mus = st.text_input("Müşteri")
                sip = st.text_input("Sipariş No")
                urun = st.selectbox("Ürün", st.session_state.envanter["Ürün Adı"].unique())
                adet = st.number_input("Adet", min_value=1)
                hasar = st.selectbox("Durum", ["Hasarsız", "Hasarlı"])
                stok_ekle = st.checkbox("Stoğa Ekle", value=True)
                if st.form_submit_button("Kaydet") and mus:
                    yeni = pd.DataFrame({"Müşteri Adı": [mus], "Ürün Adı": [urun], "Sipariş No": [sip], "Adet": [adet], "Hasar Durumu": [hasar], "Tarih": [datetime.now().strftime("%Y-%m-%d")]})
                    st.session_state.iade = pd.concat([st.session_state.iade, yeni], ignore_index=True)
                    if stok_ekle: stok_guncelle(urun, adet, "ekle")
                    st.success("İade alındı.")
        with c2:
            st.dataframe(st.session_state.iade.sort_index(ascending=False), use_container_width=True)

# ================= ANALİZ BÖLÜMÜ (GÜNCELLENDİ) =================
elif menu == "📈 Analiz Bölümü":
    st.header("📈 Hesaplama Araçları")
    
    # İki ayrı sekme oluşturuyoruz
    tab1, tab2 = st.tabs(["💰 Pazaryeri Kar Analizi", "💱 Döviz Hesaplama"])
    
    # --- SEKME 1: PAZARYERİ ANALİZİ ---
    with tab1:
        st.subheader("Pazaryeri Kar/Zarar Hesaplama")
        st.markdown("Verilen değerlere göre net karı hesaplar.")
        
        col_giris, col_sonuc = st.columns(2)
        
        with col_giris:
            alis_fiyati = st.number_input("Alış Fiyatı (Maliyet)", min_value=0.0, value=100.0, step=1.0)
            satis_fiyati = st.number_input("Satış Fiyatı", min_value=0.0, value=250.0, step=1.0)
            kargo_maliyeti = st.number_input("Kargo Maliyeti", min_value=0.0, value=40.0, step=1.0)
            iskonto_orani = st.number_input("Komisyon / İskonto Oranı (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.5)
            
        with col_sonuc:
            # Hesaplamalar
            iskonto_tutari = satis_fiyati * (iskonto_orani / 100)
            toplam_kesinti = kargo_maliyeti + iskonto_tutari
            kalan_net_tutar = satis_fiyati - toplam_kesinti
            net_kar = kalan_net_tutar - alis_fiyati
            
            # Renk belirleme (Kar ise yeşil, zarar ise kırmızı)
            renk = "green" if net_kar > 0 else "red"
            
            st.write(f"📉 **Kesintiler:**")
            st.write(f"- İskonto Tutarı: {iskonto_tutari:.2f} TL")
            st.write(f"- Kargo Tutarı: {kargo_maliyeti:.2f} TL")
            st.markdown("---")
            
            st.metric("💵 Kalan Net Tutar (Ciro)", f"{kalan_net_tutar:.2f} TL")
            
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid {renk};">
                <h3 style="color: {renk}; margin:0;">Kalan Kar: {net_kar:.2f} TL</h3>
            </div>
            """, unsafe_allow_html=True)

    # --- SEKME 2: DÖVİZ HESAPLAMA (ESKİ ÖZELLİK) ---
    with tab2:
        st.subheader("Döviz Maliyet Çevirici")
        c1, c2 = st.columns(2)
        with c1:
            kur = st.number_input("Kur", value=32.50)
            fiyat = st.number_input("Fiyat (Döviz)", value=100.0)
            iskonto = st.number_input("İskonto (%)", value=10.0)
        with c2:
            net = fiyat - (fiyat * iskonto / 100)
            tl = net * kur
            st.metric("Net Döviz", f"{net:.2f}")
            st.metric("TL Karşılığı", f"{tl:,.2f} ₺")

st.sidebar.markdown("---")
st.sidebar.markdown("🌐 [www.renyap.com](https://www.renyap.com)")