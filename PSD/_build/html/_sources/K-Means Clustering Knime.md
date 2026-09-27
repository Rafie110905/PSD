---
title: K-Means Clustering Polutan

---

## Interpretasi Hasil Clustering (Scatter Plot KNIME)

Berikut adalah visualisasi *Scatter Plot* dari hasil K-Means Clustering yang dilakukan di KNIME untuk masing-masing polutan (NO2, CO, dan SO2), beserta interpretasinya. Sumbu X menunjukkan nama daerah, sedangkan Sumbu Y menunjukkan penetapan Cluster.

### 1 Polutan NO2 (K = 6)

![image](https://hackmd.io/_uploads/r1e60VDTYfg.png)


Berdasarkan visualisasi grafik untuk polutan **NO2**, algoritma K-Means telah membagi data menjadi **6 kelompok (cluster_0 hingga cluster_5)**.

Beberapa wawasan (insight) yang bisa diambil dari persebaran plot ini:
* **Persebaran Multipel pada Satu Daerah**: Beberapa daerah memiliki titik data yang menyebar di lebih dari satu cluster. Hal ini wajar terjadi apabila dataset dipecah dalam jendela waktu tertentu (misal per minggu atau per bulan). Artinya, karakteristik polusi di daerah tersebut cukup fluktuatif sehingga bisa menyerupai pola cluster A pada waktu tertentu, dan berubah mengikuti pola cluster B pada waktu lain.
* **Dominasi Cluster 4**: Cluster 4 tampaknya menjadi kondisi yang paling banyak dialami oleh berbagai daerah (titik paling padat merata secara horizontal), mulai dari Manyar, Gresik Kota, Sampang, Tuban, Ngawi, hingga Sidoarjo. Ini mengindikasikan adanya suatu **pola polusi dasar/umum** yang sering dialami oleh mayoritas daerah.
* **Anomali / Kondisi Spesifik**: **Cluster 5** terlihat sangat terisolasi dan pada grafik ini titiknya hanya muncul di daerah **Kamal, Banyuajuh**. Hal ini menjadi indikasi kuat bahwa Kamal memiliki karakteristik pergerakan polusi yang sangat unik dan spesifik pada titik observasi tersebut yang sama sekali tidak dialami oleh daerah-daerah lain dalam dataset.
* **Kesamaan Pola Minor**: Daerah seperti Cerme (Gresik) dan Widodaren (Ngawi) memiliki kesamaan karena sama-sama tercatat memiliki titik kondisi di **Cluster 3**.

### 2. Polutan CO (K = 4)

![image](https://hackmd.io/_uploads/rkG8BDaYMe.png)

Untuk polutan **CO**, pembagian klaster yang optimal (berdasarkan *Elbow Method*) adalah **4 kelompok (cluster_0 hingga cluster_3)**. Jumlah klaster yang lebih sedikit dibandingkan NO2 ini menunjukkan bahwa variasi karakteristik polusi karbon monoksida antar daerah tidak terlalu ekstrem. 

Beberapa wawasan (insight) yang bisa diambil dari plot CO:
* **Dominasi Cluster 0**: Sama seperti kasus NO2, terdapat satu cluster yang sangat mendominasi (Cluster 0). Banyak daerah yang memiliki pola fluktuasi gas CO yang serupa (seperti Kwanyar, Asemrowo, dan Jombang). Hal ini menunjukkan kondisi tren penyebaran CO paling standar di area observasi.
* **Karakteristik Spesifik Wilayah Kamal**: Sekali lagi, daerah sekitar Kamal (baik titik Banyuajuh maupun Bangkalan) memisahkan diri dan masuk ke dalam kelompok tersendiri secara terisolasi (Cluster 1 dan Cluster 2). Hal ini memperkuat dugaan bahwa wilayah Kamal memiliki aktivitas emisi lokal yang benar-benar berbeda dari wilayah lain.
* **Kesamaan Pola Minor**: Daerah seperti Cerme (Gresik), Wonoayu, dan Kalianget (Sumenep) menunjukkan kedekatan karakteristik penyebaran CO sehingga dikelompokkan ke dalam satu kelompok pinggiran yakni Cluster 3.

### 3. Polutan SO2 (K = 6)

![image](https://hackmd.io/_uploads/Bkf18wTYMl.png)

Sama halnya dengan NO2, polutan **SO2** memiliki persebaran yang cukup kompleks sehingga algoritma membaginya secara optimal menjadi **6 kelompok (cluster_0 hingga cluster_5)**. Hal ini menunjukkan tingkat variasi konsentrasi sulfur dioksida yang cukup tinggi.

Beberapa wawasan (insight) yang bisa diambil dari plot SO2:
* **Penyebaran Utama (Cluster 1 & Cluster 4)**: Sebagian besar wilayah dikelompokkan ke dalam Cluster 1 (seperti Asemrowo, Jombang, Nganjuk) dan Cluster 4 (Gresik Kota, Cerme, Banyu Ajuh). Ini menandakan adanya dua profil dasar yang dominan dalam pergerakan SO2.
* **Pemisahan Karakteristik Kamal**: Titik observasi Kamal (Banyuajuh dan Bangkalan) secara konsisten menunjukkan hasil sebagai *outlier* atau anomali dengan menempati klaster terisolasi (Cluster 2 dan Cluster 3) yang terpisah dari gerombolan mayoritas.
* **Anomali Tunggal Wilayah Wonoayu**: Berbeda dengan CO dimana Wonoayu berada di kelompok minor bersama Cerme, pada kasus SO2 ini Wonoayu sepenuhnya terisolasi dan menempati Cluster 5 sendirian. Ini mengindikasikan adanya kejadian atau tren konsentrasi SO2 yang spesifik dan tajam di wilayah tersebut.