#import library 
import pickle
import streamlit as st
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import pandas as pd

# Muat model dan scaler dari file pickle
aarachmat_model = pickle.load(open('aarachmat.sav', 'rb'))
rmp_model = pickle.load(open('rmp.sav', 'rb'))
scaler_aarachmat = pickle.load(open('scaler_aarachmat.sav', 'rb'))
scaler_rmp = pickle.load(open('scaler_rmp.sav', 'rb'))

# Membuka gambar
gambar = Image.open('logo_unikom_kuning.png')

# Mengonversi gambar ke string base64
buffered = BytesIO()
gambar.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Mengatur gaya CSS untuk centering gambar
st.markdown(
    """
    <style>
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .center-title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

menu = ['Home', 'AA Rachmat', 'RMP', 'Prediksi Beasiswa' ]
choice = st.sidebar.selectbox('Select a Menu', menu)

# Menampilkan gambar di tengah
st.markdown(f'<div class="center"><img src="data:image/png;base64,{img_str}" width="200"></div>', unsafe_allow_html=True)

# Menampilkan judul di tengah
st.markdown('<h2 class="center-title">Universitas Komputer Indonesia</h2>', unsafe_allow_html=True)

# Fungsi untuk mengelompokkan penghasilan
def kelompok_penghasilan(x):
    if x == '> Rp. 4.000.000':
        return 0
    elif x == '> Rp. 3.000.000 - ≤ Rp. 4.000.000':
        return 1
    elif x == '> Rp. 2.000.000 - ≤ Rp. 3.000.000':
        return 2
    elif x == '≤ Rp. 2.000.000':
        return 3
    else:
        return None

# Fungsi untuk mengelompokkan IPK
def kelompok_ipk(ipk):
    if ipk is not None:
        if ipk >= 3.75:
            return 4
        elif ipk >= 3.50:
            return 3
        elif ipk >= 3.25:
            return 2
        elif ipk >= 3.00:
            return 1
        else:
            return 0
    return None

# Fungsi untuk mengelompokkan jumlah saudara
def kelompok_saudara(saudara):
    if saudara is not None:
        if saudara >= 5:
            return 4
        elif saudara == 4:
            return 3
        elif saudara == 3:
            return 2
        elif saudara == 2:
            return 1
        else:
            return 0
    return None

# Halaman Home
if choice == 'Home':
    st.markdown('<h2 class="center-title">Selamat Datang di Aplikasi Data Mining Beasiswa</h2>', unsafe_allow_html=True)
    st.write('Silakan pilih menu di sidebar untuk memulai.')

# Halaman AA Rachmat
elif choice == 'AA Rachmat':
    st.markdown('<h2 class="center-title">Prediksi Beasiswa A&A Rachmat</h2>', unsafe_allow_html=True)
    
    # Upload file CSV atau Excel
    uploaded_file = st.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        st.write("Data yang diunggah:", data)

        if st.button('Prediksi'):
            try:
                # Proses data
                data['Penghasilan'] = data['Penghasilan'].apply(kelompok_penghasilan)
                data['IPK'] = data['IPK'].apply(lambda ipk: kelompok_ipk(ipk) if pd.notnull(ipk) else None)
                data['Status_Beasiswa'] = data['Status_Beasiswa'].apply(lambda x: 1 if x == 'Perpanjangan' else 0)
                data['Cek_Bag_keuangan'] = data['Cek_Bag_keuangan'].apply(lambda x: 1 if x == 'OK' else 0)

                # Standarisasi data
                std_data = scaler_aarachmat.transform(data[['Penghasilan', 'IPK', 'Status_Beasiswa', 'Cek_Bag_keuangan']])
                beasprediction = aarachmat_model.predict(std_data)

                data['Hasil Prediksi'] = ['lulus' if pred == 1 else 'tidak lulus' for pred in beasprediction]
                st.write("Hasil Prediksi:", data)

            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")

# Halaman RMP
elif choice == 'RMP':
    st.markdown('<h2 class="center-title">Prediksi Beasiswa Rawan Melanjutkan Pendidikan</h2>', unsafe_allow_html=True)
    
    # Upload file CSV atau Excel
    uploaded_file = st.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        st.write("Data yang diunggah:", data)

        if st.button('Prediksi'):
            try:
                # Proses data
                data['Penghasilan'] = data['Penghasilan'].apply(kelompok_penghasilan)
                data['Jumlah_Saudara'] = data['Jumlah_Saudara'].apply(lambda x: kelompok_saudara(x) if pd.notnull(x) else None)
                data['Terdaftar_DTKS'] = data['Terdaftar_DTKS'].apply(lambda x: 1 if x == 'ADA' else 0)
                data['SKTM_KIP_Pernyataan'] = data['SKTM_KIP_Pernyataan'].apply(lambda x: 1 if x == 'ADA' else 0)

                # Standarisasi data
                std_data = scaler_rmp.transform(data[['Penghasilan', 'Jumlah_Saudara', 'Terdaftar_DTKS', 'SKTM_KIP_Pernyataan']])
                beasprediction = rmp_model.predict(std_data)

                data['Hasil Prediksi'] = ['lulus' if pred == 1 else 'tidak lulus' for pred in beasprediction]
                st.write("Hasil Prediksi:", data)

            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")


# halaman prediksi beasiswa
elif choice =='Prediksi Beasiswa':
        st.markdown('<h2 class="center-title"> Alat bantu pengambilan keputusan Prediksi Beasiswa UNIKOM</h2>', unsafe_allow_html=True)

        # Input dari pengguna
        beasiswa = st.selectbox('Pilih Beasiswa', ['AA Rachmat', 'RMP'])

# Input umum
        Penghasilan = st.selectbox('Penghasilan', ['> Rp. 4.000.000', '> Rp. 3.000.000 - ≤ Rp. 4.000.000', '> Rp. 2.000.000 - ≤ Rp. 3.000.000', '≤ Rp. 2.000.000'])

        # Input khusus sesuai beasiswa
        if beasiswa == 'AA Rachmat':
            IPK = st.text_input('IPK')
            if IPK:
                try:
                    IPK = float(IPK)
                    if IPK > 4.00 or IPK == 0.00:
                        st.error('IPK tidak valid')
                        IPK = None
                except ValueError:
                    st.error('IPK harus berupa angka')
                    IPK = None
            Status_Beasiswa = st.selectbox('Status Beasiswa', ['Perpanjangan', 'Baru'])
            Cek_Bag_keuangan = st.selectbox('Cek Bagian Keuangan', ['OK', 'NOK'])
        else:
            Jumlah_Saudara = st.text_input('Jumlah Saudara')
            if Jumlah_Saudara:
                try:
                    Jumlah_Saudara = int(Jumlah_Saudara)
                    if Jumlah_Saudara > 15 or Jumlah_Saudara < 1:
                        st.error('Jumlah Saudara harus di antara 1 dan 15')
                        Jumlah_Saudara = None
                except ValueError:
                    st.error('Jumlah Saudara harus berupa angka')
                    Jumlah_Saudara = None
            Terdaftar_DTKS = st.selectbox('Terdaftar di DTKS', ['ADA', 'TIDAK ADA'])
            SKTM_KIP_Pernyataan = st.selectbox('Memiliki SKTM/KIP/Surat Pernyataan', ['ADA', 'TIDAK ADA'])

        hasil_prediksi = ''


        # Tombol untuk memprediksi
        if st.button('Prediksi'):
            try:
                # Ubah input menjadi tipe data yang sesuai
                Penghasilan = kelompok_penghasilan(Penghasilan)
                
                if beasiswa == 'AA Rachmat':
                    if IPK is None:
                        raise ValueError('IPK tidak valid')
                    IPK = kelompok_ipk(IPK)
                    Status_Beasiswa = 1 if Status_Beasiswa == 'Perpanjangan' else 0
                    Cek_Bag_keuangan = 1 if Cek_Bag_keuangan == 'OK' else 0

                    # Print untuk debug
                    st.write(f"Penghasilan: {Penghasilan}, IPK: {IPK}, Status Beasiswa: {Status_Beasiswa}, Cek Bagian Keuangan: {Cek_Bag_keuangan}")

                    # Standarisasi data
                    input_data = np.array([[Penghasilan, IPK, Status_Beasiswa, Cek_Bag_keuangan]])
                    std_data = scaler_aarachmat.transform(input_data)
                    beasprediction = aarachmat_model.predict(std_data)
                else:
                    if Jumlah_Saudara is None:
                        raise ValueError('Jumlah Saudara tidak valid')
                    Jumlah_Saudara = kelompok_saudara(Jumlah_Saudara)
                    Terdaftar_DTKS = 1 if Terdaftar_DTKS == 'ADA' else 0
                    SKTM_KIP_Pernyataan = 1 if SKTM_KIP_Pernyataan == 'ADA' else 0

                    # Print untuk debug
                    st.write(f"Penghasilan: {Penghasilan}, Jumlah saudara: {Jumlah_Saudara}, Terdaftar di DTKS: {Terdaftar_DTKS}, Memiliki SKTM/KIP/PERNYATAAN: {SKTM_KIP_Pernyataan}")

                    # Standarisasi data
                    input_data = np.array([[Penghasilan, Jumlah_Saudara, Terdaftar_DTKS, SKTM_KIP_Pernyataan]])
                    std_data = scaler_rmp.transform(input_data)
                    beasprediction = rmp_model.predict(std_data)

                if beasprediction[0] == 0:
                    hasil_prediksi = 'tidak lulus'
                else:

                    hasil_prediksi = 'lulus'
            except ValueError as e:
                st.error(str(e))

        st.success(hasil_prediksi)

