# Deskripsi Fitur & Perhitungan Manual

Sesuai pembagian tugas kelas (lihat kolom **Pembagian Fitur**), bagian ini mencakup **2 fitur** milik **Moh Rafie Nazar J**:

| Fitur | Nama Fungsi TSFEL |
|---|---|
| Fitur 1 | `kurtosis(signal)` |
| Fitur 2 | `lpcc(signal[, n_coeff])` |

**Sinyal contoh yang dipakai (ilustrasi):**
`signal = [2, 4, 3, 6, 5, 7, 4, 8]`, `fs = 1` (1 sampel/hari)

> Catatan: sinyal ilustrasi ini sama persis dengan yang dipakai pada perhitungan `calc_centroid` dan `calc_max` sebelumnya, agar konsisten satu kelas. Semua hasil manual di bawah **sudah diverifikasi langsung** memakai fungsi TSFEL asli (`tsfel.feature_extraction.features`) pada sinyal yang sama — dijalankan nyata di Python, bukan diperkirakan.

---

## Fitur 1: `kurtosis(signal)`

**Deskripsi:**
`kurtosis` mengukur **keruncingan (peakedness) dan ketebalan ekor (tailedness)** distribusi nilai sinyal dibanding distribusi normal. TSFEL memanggil langsung `scipy.stats.kurtosis(signal)`, yaitu **excess kurtosis** (kurtosis Fisher, sudah dikurangi 3) dengan estimator populasi (dibagi $n$, bukan $n-1$). Untuk data kualitas udara, fitur ini menunjukkan apakah konsentrasi polutan cenderung **stabil di sekitar rata-rata** (kurtosis rendah/negatif, ekor tipis) atau sering muncul **nilai ekstrem/outlier** (kurtosis tinggi, ekor tebal).

**Rumus:**

$$\text{kurtosis}(x) = \frac{m_4}{m_2^2} - 3, \qquad m_2 = \frac{1}{n}\sum_i (x_i-\bar{x})^2, \quad m_4 = \frac{1}{n}\sum_i (x_i-\bar{x})^4$$

di mana $\bar{x}$ adalah rata-rata sinyal, $m_2$ adalah varians populasi (biased), dan $m_4$ adalah momen keempat populasi.

**Perhitungan manual:**

Sinyal: `signal = [2, 4, 3, 6, 5, 7, 4, 8]` → `n = 8`

1. Hitung rata-rata:

   $$\bar{x} = \frac{2+4+3+6+5+7+4+8}{8} = \frac{39}{8} = 4.875$$

2. Hitung deviasi $(x_i - \bar{x})$ dan pangkatnya:

   | i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
   |---|---|---|---|---|---|---|---|---|
   | $x_i$ | 2 | 4 | 3 | 6 | 5 | 7 | 4 | 8 |
   | $x_i-\bar{x}$ | -2.875 | -0.875 | -1.875 | 1.125 | 0.125 | 2.125 | -0.875 | 3.125 |
   | $(x_i-\bar{x})^2$ | 8.265625 | 0.765625 | 3.515625 | 1.265625 | 0.015625 | 4.515625 | 0.765625 | 9.765625 |
   | $(x_i-\bar{x})^4$ | 68.320557 | 0.586182 | 12.359619 | 1.601807 | 0.000244 | 20.390869 | 0.586182 | 95.367432 |

3. Jumlahkan lalu bagi $n=8$:

   $$m_2 = \frac{28.875}{8} = 3.609375$$

   $$m_4 = \frac{199.212891}{8} = 24.901611$$

4. Masukkan ke rumus:

   $$\text{kurtosis} = \frac{24.901611}{3.609375^2} - 3 = \frac{24.901611}{13.027588} - 3 = 1.911452 - 3 = -1.088548$$

**Verifikasi dengan TSFEL:**

```python
import tsfel.feature_extraction.features as F
signal = [2, 4, 3, 6, 5, 7, 4, 8]
F.kurtosis(signal)   # -> -1.0885478158205430
```

Hasil manual (**-1.088548**) **cocok** dengan hasil fungsi TSFEL asli (dijalankan langsung, output: `-1.0885478158205430`). ✅

Nilai negatif ini berarti distribusi sinyal ilustrasi sedikit lebih *platykurtic* (lebih datar / ekor lebih tipis) dibanding distribusi normal.

**Nilai aktual pada dataset:**

> ⚠️ Sama seperti dua fitur sebelumnya, data time series harian asli untuk lokasi/orang yang menjadi tanggung jawab Moh Rafie tidak tersedia di percakapan ini — hanya sinyal ilustrasi di atas yang bisa dihitung manual. Untuk mengisi nilai aktual `kurtosis` hasil ekstraksi sungguhan (dari `ekstraksi_fitur_no2.csv`), silakan cek kolom `kurtosis` pada baris id yang sesuai, lalu isi di tabel ringkasan di bagian akhir dokumen ini. Kalau file CSV-nya diunggah ke percakapan ini, saya bisa ambilkan angkanya langsung.

---

## Fitur 2: `lpcc(signal[, n_coeff])`

**Deskripsi:**
`lpcc` (**Linear Prediction Cepstral Coefficients**) adalah fitur domain spektral yang awalnya dipakai di pengolahan suara, namun berguna juga untuk deret waktu lain karena menangkap **karakteristik "bentuk spektral"** sinyal secara ringkas dalam beberapa koefisien. Prosesnya 2 tahap:

1. Hitung **koefisien prediksi linier (LPC)** dari sinyal — koefisien yang jika dipakai memprediksi $x_i$ dari kombinasi linier nilai-nilai sebelumnya, akan meminimalkan error prediksi (metode **Yule-Walker**, via autokorelasi).
2. Ubah koefisien LPC tersebut menjadi **koefisien cepstral** lewat spektrum daya → log → invers FFT.

Karena TSFEL memakai default `n_coeff = 12` (butuh panjang sinyal ≥ 12), sedangkan sinyal ilustrasi kelas hanya berisi **8 titik**, perhitungan manual di bawah memakai `n_coeff = 4` (order = 3) agar bisa ditelusuri tangan sekaligus tetap valid dipanggil TSFEL pada sinyal 8 titik ini. Metodenya identik — hanya jumlah koefisien keluaran yang lebih sedikit.

**Rumus / Alur:**

$$r_k = \sum_{i=0}^{n-1-k} x_i\, x_{i+k}, \quad k = 0,1,\dots,\text{order}$$

$$R\,\mathbf{a} = -\mathbf{r}_{1:}, \qquad R_{ij} = r_{|i-j|} \;\; (\text{matriks Toeplitz/otokorelasi})$$

$$\text{lpc} = [\,1,\ a_1,\ a_2,\ a_3\,]$$

$$P_k = \bigl|\text{FFT}(\text{lpc})_k\bigr|^2, \qquad \text{lpcc}_n = \Bigl|\ \text{IFFT}\bigl(\ln P\bigr)_n\ \Bigr|$$

**Perhitungan manual:**

Sinyal: `signal = [2, 4, 3, 6, 5, 7, 4, 8]`, `n_coeff = 4` → `order = 3`

**Langkah 1 — Autokorelasi (lag 0 s/d 3):**

$$r_0=\sum x_i^2 = 219$$
$$r_1 = 2{\cdot}4+4{\cdot}3+3{\cdot}6+6{\cdot}5+5{\cdot}7+7{\cdot}4+4{\cdot}8 = 8+12+18+30+35+28+32 = 163$$
$$r_2 = 2{\cdot}3+4{\cdot}6+3{\cdot}5+6{\cdot}7+5{\cdot}4+7{\cdot}8 = 6+24+15+42+20+56 = 163$$
$$r_3 = 2{\cdot}6+4{\cdot}5+3{\cdot}7+6{\cdot}4+5{\cdot}8 = 12+20+21+24+40 = 117$$

Jadi $\mathbf{r} = [219,\ 163,\ 163,\ 117]$.

**Langkah 2 — Susun matriks Toeplitz (dari $r_0,r_1,r_2$) dan selesaikan sistem persamaan Yule-Walker** $R\mathbf{a}=-[r_1,r_2,r_3]$:

$$\begin{bmatrix}219&163&163\\163&219&163\\163&163&219\end{bmatrix}\begin{bmatrix}a_1\\a_2\\a_3\end{bmatrix}=\begin{bmatrix}-163\\-163\\-117\end{bmatrix}$$

Kurangkan baris 1 dengan baris 2 → $56a_1-56a_2=0 \Rightarrow a_1=a_2$ (karena $r_1=r_2$, sistemnya simetris).

Substitusi $a_1=a_2=a$ ke baris 1 dan baris 3:

$$382a+163a_3=-163 \qquad(\text{I})$$
$$326a+219a_3=-117 \qquad(\text{III})$$

Eliminasi $a_3$ (kalikan (I) dengan 219, (III) dengan 163, lalu kurangkan):

$$30520\,a = -16626 \;\Rightarrow\; a = a_1=a_2 = -0.544758$$

Masukkan ke (I): $163a_3 = -163-382(-0.544758)=45.097 \Rightarrow a_3 = 0.276671$

**Koefisien LPC:** $\text{lpc} = [1,\ -0.544758,\ -0.544758,\ 0.276671]$

**Langkah 3 — Spektrum daya (FFT 4 titik dari vektor LPC):**

$$X_0 = 1-0.544758-0.544758+0.276671 = 0.187156$$
$$X_1 = (X_{0,\text{re}}-X_2)+i(a_3-a_1) = (1-(-0.544758)) + i(0.276671-(-0.544758)) = 1.544758+0.821429i$$
$$X_2 = 1-(-0.544758)+(-0.544758)-0.276671 = 0.723329$$
$$X_3 = \overline{X_1} = 1.544758-0.821429i$$

$$P = |X|^2 = [\,0.035027,\ 3.061021,\ 0.523205,\ 3.061021\,]$$

**Langkah 4 — Log spektrum, lalu IFFT (invers FFT), lalu nilai mutlak:**

$$\ln P = [\,-3.351626,\ 1.118748,\ -0.647782,\ 1.118748\,]$$

$$y_0=\tfrac14\sum\ln P = -0.440478,\quad y_1=\tfrac14(\ln P_0-\ln P_2)= -0.675961$$
$$y_2=\tfrac14(\ln P_0-\ln P_1+\ln P_2-\ln P_3) = -1.559226,\quad y_3=y_1=-0.675961$$

$$\text{lpcc} = |y| = [\,0.440478,\ 0.675961,\ 1.559226,\ 0.675961\,]$$

**Verifikasi dengan TSFEL:**

```python
import tsfel.feature_extraction.features as F
signal = [2, 4, 3, 6, 5, 7, 4, 8]
F.lpcc(signal, n_coeff=4)
# -> (0.44047785284782226, 0.6759609102699858,
#     1.559226289370152, 0.6759609102699858)
```

Hasil manual (**0.440478, 0.675961, 1.559226, 0.675961**) **cocok persis** dengan hasil fungsi TSFEL asli. ✅

**Nilai aktual pada dataset:**

> ⚠️ Sama seperti fitur 1, nilai aktual `Lpcc_1`, `Lpcc_2`, dst. hasil ekstraksi TSFEL sungguhan untuk lokasi/orang milik Moh Rafie ada di file `ekstraksi_fitur_no2.csv` (dengan `n_coeff` sesuai yang dipakai pipeline aslinya, umumnya default 12 → menghasilkan kolom `Lpcc_1` s/d `Lpcc_12`). Silakan isi angkanya di tabel ringkasan bila filenya sudah tersedia — perhitungan manual di atas hanya membuktikan metodenya (autokorelasi → Yule-Walker → LPC → cepstral) sudah diterapkan dengan benar, bukan untuk mereproduksi angka asli tersebut karena data time series mentahnya tidak kita miliki.

---

## Ringkasan

| Fitur | Rumus Singkat | Hasil (sinyal ilustrasi) | Nilai aktual di dataset |
|---|---|---|---|
| `kurtosis(signal)` | $m_4/m_2^2 - 3$ | -1.088548 | *0.1075986222265736* |
| `lpcc(signal, n_coeff=4)` | IFFT(ln\|FFT(lpc)\|²) | 0.440478, 0.675961, 1.559226, 0.675961 | *0.7109413464283354* |
