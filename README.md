# Proyek Analisis Data Dicoding: E-Commerce Public Dataset

## Deskripsi
Proyek ini berisi proses analisis pada dataset Olist E-Commerce Public dataset yang berisi informasi tentang pelanggan, pembelian, kategori barang, dan lainnya, serta visualisasi data berupa dashboard menggunakan Streamlit. Tujuan dibuatnya proyek ini adalah untuk memberikan insight yang berguna untuk membentuk strategis bisnis dan memahami experience pelanggan kedepannya.
## Instalasi
1. Install repository
```shell
git clone https://github.com/muris1112/proyek_analisis_data.git
```
2. Buat environment baru menggunakan pipenv
```
mkdir proyek_analisis_data_env
cd proyek_analisis_data_env
pipenv install
```
3. Aktifkan environment dan install dependency
```
pipenv shell
pip install -r ../proyek_analisis_data/requirements.txt
```
4. Pergi ke direktori proyek_analisis_data dan jalankan Jupyter
```
cd ../proyek_analisis_data
jupyter notebook
```
## Menjalankan Dashboard
1. Gunakan command ini untuk menjalankan dashboard secara local (pastikan environment sudah aktif) :
```
streamlit run dashboard/dashboard.py
```
atau gunakan link berikut untuk mengakses dashboard yang sudah di deploy di Streamit : [link](https://muhammadidris-submission.streamlit.app/).