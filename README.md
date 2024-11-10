# MonggoDB
`MonggoDB` adalah sebuah database berbasis file-file `JSON` yang sangat sederhana yang dibuat dengan `Python`. Saya (naf'an rizkilah) membuat ini sebagai hobi. Nama `MonggoDB` sendiri berasal dari plesetan `MongoDB` (hanya beda satu huruf) 
## Fitur
- CRUD sederhana
- XOR encrypt/decrypt
## Preview
```python
from monggodb import MonggoDB

# creating and connecting to database
mdb = MonggoDB("testdb")

# creating table
mdb.table('user').col('id', autoinc=True, primary_key=True).col('username').col('password').mk_table()

# creating data (user)
mdb.create('user', {
  'id': None,
  'username': 'Primis',
  'password': 'ok500'
})
mdb.create('user', {
  'id': None,
  'username': 'Hemker',
  'password': 'ok500'
})
mdb.create('user', {
  'id': None,
  'username': 'Kadrun',
  'password': 'ok500'
})

# get single data (user)
user = mdb.select('user').where('id', '1').get()

# update data (user)
mdb.select('user').where('id', '2').update({'username': 'Omke Gams'})

# delete data (user)
mdb.select('user').where('id', '3').delete()

# get all data (user)
users = mdb.select('user').get()
```
## Dokumentasi

[DOCS.md](./DOCS.md)

## Rencana Update
1. Optimisasi
2. Menambahkan fitur `Static Type`
3. Menambahkan fitur relasi antar tabel
