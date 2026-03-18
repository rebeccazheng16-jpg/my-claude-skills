# Humanizer-ID

Menghapus jejak AI dari teks berbahasa Indonesia, membuat tulisan terdengar lebih alami dan manusiawi.

去除印尼语文本中的 AI 生成痕迹，使文字更自然、更有人味。

## Instalasi / 安装

### Metode 1: Instalasi Manual (Sudah Terinstal)

Skill ini sudah terinstal di: `~/.claude/skills/humanizer-id/`

### Metode 2: Git Clone

```bash
git clone https://github.com/[your-username]/humanizer-id.git ~/.claude/skills/humanizer-id
```

## Penggunaan / 使用方法

Dalam Claude Code, gunakan:

```
/humanizer-id

[Tempel teks yang ingin dihumanisasi]
```

Atau dalam percakapan:

```
Tolong gunakan humanizer-id untuk memperbaiki teks berikut:

[Teks Anda di sini]
```

## Pola yang Dideteksi / 检测的模式

### Pola Konten (6)
1. Penekanan berlebihan pada makna dan warisan
2. Penekanan berlebihan pada ketenaran dan liputan media
3. Analisis dangkal dengan akhiran -kan/-i
4. Bahasa promosi dan iklan
5. Atribusi samar
6. Bagian "tantangan dan prospek" yang formulaik

### Pola Bahasa (6)
7. Kosakata AI yang terlalu sering
8. Penghindaran kopula (menghindari "adalah")
9. Penggunaan negasi berlebihan
10. Aturan tiga bagian berlebihan
11. Siklus sinonim
12. Rentang palsu

### Pola Gaya (4)
13. Tanda hubung berlebihan
14. Huruf tebal berlebihan
15. Daftar vertikal dengan judul inline
16. Emoji

### Pola Komunikasi (3)
17. Jejak komunikasi kolaboratif
18. Disclaimer batas pengetahuan
19. Nada menjilat

### Frasa Pengisi (3)
20. Frasa pengisi
21. Kualifikasi berlebihan
22. Kesimpulan positif generik

### Pola Khusus Indonesia (2)
23. Kata serapan asing berlebihan
24. Struktur kalimat pasif berlebihan

## Contoh / 示例

### Sebelum (Rasa AI):
> Pembaruan software terbaru berfungsi sebagai bukti komitmen perusahaan terhadap inovasi. Selain itu, ia menawarkan pengalaman pengguna yang mulus, intuitif, dan powerful—memastikan pengguna dapat mencapai tujuan mereka secara efisien.

### Sesudah (Dihumanisasi):
> Pembaruan software menambahkan pemrosesan batch, pintasan keyboard, dan mode offline. Umpan balik awal dari pengguna uji coba positif.

## Sistem Penilaian / 评分系统

Evaluasi 5 dimensi (total 50 poin):

| Dimensi | Deskripsi |
|---------|-----------|
| Keterusterangan | Langsung vs berputar-putar |
| Ritme | Variasi panjang kalimat |
| Kepercayaan | Menghormati kecerdasan pembaca |
| Keaslian | Terdengar seperti manusia |
| Keringkasan | Tidak ada redundansi |

**Standar:**
- 45-50: Sangat baik
- 35-44: Baik
- <35: Perlu revisi

## Filosofi / 理念

> "Tool ini bukan untuk 'menipu' detektor AI, melainkan untuk benar-benar meningkatkan kualitas tulisan. Metode 'de-AI' terbaik adalah membuat tulisan memiliki pemikiran dan suara manusia yang nyata."

## Referensi / 参考

- [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [humanizer-zh](https://github.com/op7418/Humanizer-zh) (versi Cina)
- [blader/humanizer](https://github.com/blader/humanizer) (versi Inggris asli)

## Lisensi / 许可证

MIT License

---

*Dibuat untuk pasar Indonesia / 为印尼市场创建*
