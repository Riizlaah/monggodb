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
