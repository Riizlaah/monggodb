# Instalasi
Untuk menginstal MonggoDB caranya cukup mudah, yaitu tempatkan file `monggodb.py` di dalam proyek anda.
Kemudian import MonggoDB. instalasi sudah selesai, MonggoDB akan saya usahakan tidak memakai library selain yang disediakan oleh Python Standard Library untuk portabilitas

# Koneksi Database
Untuk mempersiapkan koneksi database MonggoDB, gunakan class `MonggoDB`. Contoh :
```python
# Hanya perlu classnya saja
from monggodb import MonggoDB

# koneksi database dengan folder path relatif
# misal :
# /folder1
#   main.py <-- file saat ini
#   db4/ <-- lokasi database
#   ...
mdb = MonggoDB("db4")

# koneksi database dengan folder path absolute
# /home/user/folder1
#   main.py <-- file saat ini
#   ...
# /home/user/db1 <-- lokasi database
mdb = MonggoDB("/home/user/db1", True)


# koneksi database dengan XOR encrypt/decrypt
mdb = MonggoDB("db2", use_xor_cipher=True, key="secret123")

```

# Membuat Tabel
Untuk membuat tabel gunakan method `table()` untuk inisiasi, `col()` untuk membuat kolom, jika sudah selesai panggil method `mk_table()` untuk menyimpan tabel. Contoh :
```python
# Membuat tabel user
#              (nama tabel)
table = mdb.table("user")

# Membuat kolom
#          (1)   (2)   (3)   (4)
table.col("id", True, False, None)
# nilai default masing-masing parameter adalah (2) = False, (3) = False, (4) = None
table.col("username")
table.col("password")
# keterangan :
# (1) : nama kolom
# (2) : autoinc (autoincrement)
# (3) : nullable (maksudnya adalah "apa nilai kolom boleh kosong?")
# (4) : nilai default

# Jangan lupa untuk memanggil `mk_table()` setelah selesai membuat tabel
table.mk_table()

# Cara diatas bisa disingkat menjadi :
# mdb.table("user").col("id", autoinc=True).col("username").col("password").mk_table()
```

# Menambahkan data
Untuk menambahkan data, method yang dipakai adalah `create()`. Contoh :
```python

#       (nama tabel)
mdb.create("user", {
  'id': None,               # |
  'username': 'Alok',       # |- data yang
  'password': 'Admin#1234'  # |  harus diisi
})

```

# Mengambil Data
Untuk mengambil data kita bisa memakai method `select()` untuk memilih tabel, `where()` untuk mencari kondisi tertentu, lalu `get()` untuk mengambil data. Contoh :
```python
# Mengambil 1 data di tabel `user` dengan username = 'Alok'
user1 = mdb.select('user').where('username', 'Alok').get() # Mengembalikan None jika tidak ada

# Mengambil semua data-data user yang ada dalam bentuk `list`
users = mdb.select('user').get(True)
```
## Mengambil data dengan beberapa kolom saja
Secara default, ketika data telah diambil, data yang didapat memiliki semua kolom (seperti id, username dan password). Kita bisa memilih apa saja kolom yang dibutuhkan, contoh :
```python

# Mengambil data dengan kolom tertentu
user2 = mdb.select('user', 'id,username').where('id', '1').get()
```
## Mengambil data dengan kondisi tertentu saja
Untuk method `where()` ini cukup kompleks, karena memiliki banyak opsi. ada 4 parameter, 2 wajib dan 2 lagi opsional. 2 paramater yang wajib adalah `column` atau kolom, lalu `value` atau nilai, maksudnya adalah mencari data/baris yang berisi yang berisi `column` yang sesuai dengan `value` yang dicari. Kemudian, ada parameter `operator` untuk menentukan operator apa yang dipakai(secara default `=`), ada 3 operator yang didukung yaitu `=`(mencari PERSIS seperti `value`), `~=`(mencari yang mirip seperti `value`) dan `!=`(mencari yang tidak sama seperti `value`). Selanjutnya ada parameter `prefix`(saya bingung memberi nama apa untuk operator logika yang terletak di bagian awal) atau operator logika seperti `and` dan `or`
```python

# Mencari user dengan id = 1
user2 = mdb.select('user').where('id', '1').get()

# Mencari user dengan `username` yang mirip `alok` ('Alok', 'ALOK', 'alOk', dst... juga termasuk)
user3 = mdb.select('user').where('username', 'alok', '~=').get()

# Mencari user dengan `username` SELAIN 'alok'
user3 = mdb.select('user').where('username', 'alok', '!=').get()

# Mencari user dengan `username`=`alok` DAN `password` = `okgas500`
user4 = mdb.select('user').where('username', 'alok').where('password', 'okgas500', prefix='and').get()

# Mencari user dengan `username`=`alok` ATAU `password` = `okgas500`
user4 = mdb.select('user').where('username', 'alok').where('password', 'okgas500', prefix='or').get(True) # bisa mendapatkan user lebih dari satu karena ada kemungkinan beberapa user memiliki password yang sama
```

# Mengubah Data
Mengubah data bisa dilakukan dengan method `update()` dengan tambahan `select()` dan `where()`. Contoh :
```python
# Mengubah username milik user `olak` yang awalnya `olak` menjadi `alok`
mdb.select('user').where('username', 'olak').update({
  'username': 'alok'
})

# Kode di bawah akan menghasilkan error karena tidak tahu mana yang harus di-update/diubah
# mdb.update({'username': 'omke'})

# Berhati-hatilah jika meng-update data tanpa method `where()`, karena bisa mengubah semua data sekaligus, secara default jika parameter `force` = False dan anda tidak memakai method `where()` maka MonggoDB akan mengeluarkan peringatan. Jika anda memang ingin mengubah semua data maka set parameter `force` menjadi `True` seperti berikut
# mdb.select('user').update({'role': 'user'}, True) <-- tambahan True untuk meng-update semua data secara paksa
```
# Menghapus Data
Untuk menghapus data anda bisa memakai method `delete()`. Penggunaannya sama seperti method `update()` yaitu memerlukan method `select()` dan `where()`. Contoh :
```python
# Menghapus user dengan `id` = 2
mdb.select('user').where('id', '2').delete()

# Hampir sama seperti update(), kdoe di bawah akan menghasilkan error
# mdb.delete()

# Hati-hati, jangan sampai anda tidak sengaja menghapus semua data yang ada. Sama seperti `update()`, method tersebut akan menghasilkan peringatan jika method where() tidak dipakai dalam penghapusan dan `force` adalah False.

```
