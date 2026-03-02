import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import io

# --- VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_v10_auth.json"

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ogrenciler": {}}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = veri_yukle()

# --- TASARIM ---
st.set_page_config(page_title="Nida GÖMCELİ Akademi", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: white; }
    .auth-card { background: #11141b; padding: 25px; border-radius: 20px; border: 1px solid #00d4ff; text-align: center; }
    .welcome-msg { color: #2ecc71; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ VE ŞİFRE BELİRLEME SİSTEMİ ---
if "logged_in" not in st.session_state:
    st.markdown('<div class="auth-card"><h1>🛡️ Nida GÖMCELİ Akademi Giriş</h1>', unsafe_allow_html=True)
    
    tab_login, tab_setup = st.tabs(["Giriş Yap", "İlk Kez Şifre Oluştur"])
    
    with tab_login:
        user_input = st.text_input("Kullanıcı Adı (Ad Soyad)")
        pass_input = st.text_input("Şifre", type="password")
        if st.button("Sisteme Eriş"):
            if user_input == "admin" and pass_input == "nida2024":
                st.session_state.update({"logged_in": True, "role": "admin"})
                st.rerun()
            elif user_input in st.session_state.db["ogrenciler"]:
                saved_pass = st.session_state.db["ogrenciler"][user_input].get("sifre")
                if saved_pass == pass_input:
                    st.session_state.update({"logged_in": True, "role": "ogrenci", "user": user_input})
                    st.rerun()
                else: st.error("Hatalı şifre!")
            else: st.error("Kullanıcı bulunamadı!")

    with tab_setup:
        st.info("Nida Hocanızdan aldığınız kullanıcı adıyla şifrenizi belirleyin.")
        setup_user = st.text_input("Ad Soyad (Sistemdeki)")
        new_pass = st.text_input("Yeni Şifreniz", type="password")
        confirm_pass = st.text_input("Yeni Şifre Tekrar", type="password")
        
        if st.button("Şifremi Kaydet"):
            if setup_user in st.session_state.db["ogrenciler"]:
                if new_pass == confirm_pass and len(new_pass) > 3:
                    st.session_state.db["ogrenciler"][setup_user]["sifre"] = new_pass
                    veri_kaydet(st.session_state.db)
                    st.success("Şifreniz oluşturuldu! Giriş yap sekmesine dönebilirsiniz.")
                else: st.warning("Şifreler eşleşmiyor veya çok kısa!")
            else: st.error("İsminiz sistemde kayıtlı değil. Lütfen Nida Hocanıza danışın.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- ADMIN ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Yönetici: Nida G.")
        if st.sidebar.button("Güvenli Çıkış"): del st.session_state["logged_in"]; st.rerun()

        with st.expander("👤 Yeni Öğrenci Kaydı & WhatsApp Daveti"):
            n_name = st.text_input("Öğrenci Ad Soyad")
            s_turu = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
            v_tel = st.text_input("Veli/Öğrenci No (905...)")
            h_hedef = st.number_input("Haftalık Soru Hedefi", 100, 5000, 500)
            
            if st.button("Öğrenciyi Tanımla"):
                st.session_state.db["ogrenciler"][n_name] = {
                    "soru_takip": [], "denemeler": [], "tel": v_tel, 
                    "sinav": s_turu, "hedef": h_hedef, "sifre": None
                }
                veri_kaydet(st.session_state.db)
                
                # WHATSAPP DAVET MESAJI
                davet_msg = f"🛡️ Nida GÖMCELİ Akademi'ye Hoş Geldin!\n\n"
                davet_msg += f"Merhaba {n_name}, koçluk sistemimiz aktif edildi. 🚀\n\n"
                davet_msg += f"👉 Giriş Linki: nida-akademi.streamlit.app\n"
                davet_msg += f"👤 Kullanıcı Adın: {n_name}\n\n"
                davet_msg += "Sisteme ilk kez girdiğinde 'İlk Kez Şifre Oluştur' sekmesinden kendi şifreni belirleyebilirsin. İyi çalışmalar dilerim!"
                
                wa_url = f"https://wa.me/{v_tel}?text={urllib.parse.quote(davet_msg)}"
                st.success(f"{n_name} eklendi!")
                st.markdown(f'<a href="{wa_url}" target="_blank" style="background:#25d366; color:white; padding:10px; border-radius:8px; text-decoration:none; display:block; text-align:center;">💬 Öğrenciye WhatsApp Daveti Gönder</a>', unsafe_allow_html=True)

    # --- ÖĞRENCİ PANELİ (Önceki v9 özelliklerinin tamamı burada devam eder) ---
    else:
        st.write(f"Hoş geldin, {st.session_state['user']}!")
        # (Soru girişi, deneme analizi vb. modüller buraya eklenecek)