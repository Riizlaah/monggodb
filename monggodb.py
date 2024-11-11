import json, os, re, base64

class MonggoDB:
  def __init__(self, dbpath = "mydb", abs_path = False, use_xor_cipher = False, key = 'monggodb') -> None:
    dbpath = dbpath.removesuffix("/")
    if not abs_path: dbpath = os.path.dirname(__file__) + "/" + dbpath
    self._dbpath = dbpath
    self._tmp_info = {}
    self._select_info = {}
    self._where_info = []
    self._use_xor_cipher = use_xor_cipher
    self._key = key

    if not os.path.exists(dbpath): os.mkdir(dbpath)
    if not os.path.exists(dbpath+"/tables.info"): 
      self._writef(dbpath+"/tables.info", r"{}")
      self._tb_info = {}
    else:
      self._tb_info = json.loads(self._readf(dbpath+"/tables.info"))

  def show_tb(self, name):
    return self._tb_info.get(name)
  
  def get_rows(self, name):
    tb = self._tb_info.get(name)
    if tb != None: return tb['rows']
    return None

  def table(self, name: str):
    if re.match(r"^[a-zA-Z_]+\d*$", name) == None: raise Exception("'"+name+"' can't be used because not following the rules \n(allowed chars: a-zA-Z_0-9 \nmust begin with a-z or '_', not begin with digit)")
    self._tmp_info = {'name': name}
    self._tmp_info['cols'] = []
    self._tmp_info['nullable'] = []
    self._tmp_info['autoinc'] = []
    self._tmp_info['defaults'] = {}
    # self._tmp_info['primary_key'] = []
    return self
  
  def col(self, name: str, autoinc: bool = False, nullable: bool = False, default = None):
    if re.match(r"^[a-zA-Z_]+\d*$", name) == None: raise Exception("'"+name+"' can't be used because not following the rules \n(allowed chars: a-zA-Z_0-9 \nmust begin with a-z or '_', not begin with digit)")
    if name not in self._tmp_info['cols']: self._tmp_info['cols'].append(name)
    if nullable and name not in self._tmp_info['nullable']:
      self._tmp_info['nullable'].append(name)
    if not nullable and name in self._tmp_info['nullable']:
      self._tmp_info['nullable'].remove(name)
    if autoinc and name not in self._tmp_info['autoinc']:
      self._tmp_info['autoinc'].append(name)
    if not autoinc and name in self._tmp_info['autoinc']:
      self._tmp_info['autoinc'].remove(name)
    if default != None:
      self._tmp_info['defaults'][name] = default
    if default == None and self._tmp_info['defaults'].get(name) != None:
      del self._tmp_info['defaults'][name]
    return self
  
  def mk_table(self):
    name = self._tmp_info['name']
    rows = 0 if self._tb_info.get(name) == None else self._tb_info[name]['rows']
    lastid = 0 if self._tb_info.get(name) == None else self._tb_info[name]['lastid']
    self._tb_info[name] = {
      'columns': self._tmp_info['cols'],
      'rows': rows,
      'rows_file': self._dbpath + "/" + name + "_rows",
      'lastid': lastid,
      'nullable': self._tmp_info['nullable'],
      'autoinc': self._tmp_info['autoinc'],
      'defaults': self._tmp_info['defaults']
      # 'primary_key': self._tmp_info['primary_key']
    }
    self._writef(self._dbpath+"/"+name+"_rows", r"[]")
    self._update_tables_info()
    self._tmp_info = {}

  def create(self, table_name: str, data: dict):
    if self._tb_info.get(table_name) == None: raise Exception("Table '"+table_name+"' doesn't exist")
    tb_info = self._tb_info[table_name]
    if self._tb_info.get(table_name) == None:
      raise Exception("Table '"+table_name+"' not exist!")
    for k in tb_info['columns']:
      if ((k not in tb_info['nullable']) and (k not in tb_info['autoinc'])) and (tb_info['defaults'].get(k) == None) and data.get(k) == None: raise Exception("Column '"+k+"' isn't nullable!")
      if (k in tb_info['autoinc']) and (tb_info['defaults'].get(k) == None) and data.get(k) == None:
        lastid = tb_info['lastid'] + 1
        data[k] = lastid
        self._setlastid(table_name, lastid)
      if (k not in tb_info['autoinc']) and (tb_info['defaults'].get(k) != None) and (data.get(k) == None):
        data[k] = tb_info['defaults'][k]
    rows = json.loads(self._readf(tb_info['rows_file']))
    rows.append(data)
    self._writef(tb_info['rows_file'], json.dumps(rows))
    tb_info['rows'] += 1
    self._update_tables_info()
    
  def _setlastid(self, table_name, n):
    self._tb_info[table_name]['lastid'] = n
    self._update_tables_info()
  
  def _update_tables_info(self):
    self._writef(self._dbpath + "/tables.info", json.dumps(self._tb_info))

  def select(self, table_name: str, cols: str = ''):
    if cols == '': cols = '*'
    self._select_info['table'] = table_name
    self._select_info['cols'] = cols
    return self

  def where(self, col: str, val, op = '=', prefix = ''):
    # print(self._tb_info)
    if col not in self._tb_info[self._select_info['table']]['columns']: raise Exception("Column '"+col+"' not exist in table "+self._select_info['table'])
    if op not in ['=', '!=', '~=']: raise Exception("Operator not allowed '"+op+"'. Allowed : =, !=, ~=")
    if prefix not in ['or', 'and', '']: raise Exception("Logical operator not allowed : '"+prefix+"'. Allowed : and, or")
    self._where_info.append([col, val, op, prefix])
    return self
  
  def get(self, multiple = False):
    tb_info = self._tb_info[self._select_info['table']]
    rows = []
    ret = []
    rows = json.loads(self._readf(tb_info['rows_file']))
    re_exps = self._compile_where_cond()
    res = []
    for row in rows:
      passed = True
      for k in re_exps:
        is_match = (re.match(re_exps[k][0], str(row[k])) != None) if not re_exps[k][1] else (re.match(re_exps[k][0], str(row[k]), re.IGNORECASE) != None)
        if is_match and re_exps[k][2] == '': passed = True
        elif (is_match and passed) and re_exps[k][2] == 'and': passed = True
        elif (is_match or passed) and re_exps[k][2] == 'or': passed = True
        else: passed = False
      if passed:
        res.append(row)
    for row in res:
      if self._select_info['cols'] == '*':
        ret.append(row)
      else:
        row1 = {}
        for col in self._select_info['cols'].replace(' ', '').split(','):
          row1[col] = row[col]
        ret.append(row1)
    self._select_info = {}
    self._where_info = []
    if multiple: return ret
    else: return ret[0] if len(ret) > 0 else None

  def _compile_where_cond(self):
    re_exps = {}
    for where_cond in self._where_info:
      val = str(where_cond[1])
      if where_cond[2] == '=':
        re_exps[where_cond[0]] = [r"^"+val+"$"]
        re_exps[where_cond[0]].append(False)
      elif where_cond[2] == '~=':
        re_exps[where_cond[0]] = [r""+val]
        re_exps[where_cond[0]].append(True)
      else:
        re_exps[where_cond[0]] = [r"^(?!.*?"+val+").*"]
        re_exps[where_cond[0]].append(False)
      re_exps[where_cond[0]].append(where_cond[3])
    return re_exps

  def update(self, data: dict, force = False):
    if len(self._where_info) == 0 and not force: raise Exception('Warning : updating ALL data without where condition')
    where_info = self._where_info.copy()
    table_name = self._select_info['table']
    rows = self.select(table_name).get(True)
    rows2 = json.loads(self._readf(self._tb_info[table_name]['rows_file']))
    if rows == None: return
    for i in range(len(rows)):
      for k in data.keys():
        if k not in self._tb_info[table_name]['columns']: raise Exception("No columns named '"+k+"' in table '"+table_name+"'")
        rows[i][k] = data[k]
    self._where_info = where_info
    re_exps = self._compile_where_cond()
    self._where_info = []
    for i in range(len(rows2)):
      row = rows2[i]
      passed = True
      for k in re_exps:
        is_match = (re.match(re_exps[k][0], str(row[k])) != None) if not re_exps[k][1] else (re.match(re_exps[k][0], str(row[k]), re.IGNORECASE) != None)
        if is_match and re_exps[k][2] == '': passed = True
        elif (is_match and passed) and re_exps[k][2] == 'and': passed = True
        elif (is_match or passed) and re_exps[k][2] == 'or': passed = True
        else: passed = False
      if passed:
        rows2[i] = rows.pop(0)
    self._writef(self._tb_info[table_name]['rows_file'], json.dumps(rows2))
    self._select_info = {}
    self._where_info = []
    return True
  
  def delete(self, force = False):
    if len(self._where_info) == 0 and not force: raise Exception('Warning : deleting ALL data without where condition')
    rows2 = self._readf(self._tb_info[self._select_info['table']]['rows_file'])
    re_exps = self._compile_where_cond()
    self._where_info = []
    rows = []
    for i in range(len(rows2)):
      row = rows2[i]
      passed = True
      for k in re_exps:
        is_match = (re.match(re_exps[k][0], str(row[k])) != None) if not re_exps[k][1] else (re.match(re_exps[k][0], str(row[k]), re.IGNORECASE) != None)
        if is_match and re_exps[k][2] == '': passed = True
        elif (is_match and passed) and re_exps[k][2] == 'and': passed = True
        elif (is_match or passed) and re_exps[k][2] == 'or': passed = True
        else: passed = False
      if not passed:
        rows.append(row)
    self._writef(self._tb_info[self._select_info['table']]['rows_file'], json.dumps(rows))
    self._tb_info[self._select_info['table']]['rows'] -= 1
    self._update_tables_info()
    self._select_info = {}
    self._where_info = []
    return True
  
  def _readf(self, path: str) -> str:
    f = open(path)
    res = f.read()
    f.close()
    if self._use_xor_cipher:
      res = self.xor_cipher(res, self._key, False)
      return res
    return res
  
  def _writef(self, path, ctn) -> None:
    f = open(path, "w")
    if self._use_xor_cipher: ctn = self.xor_cipher(ctn, self._key)
    f.write(ctn)
    f.close()
    
  def xor_cipher(self, text: str, key: str, encode = True):
    if not encode: text = base64.b64decode(text).decode()
    text2 = ''
    for i, c in enumerate(text):
      text2 += chr(ord(c) ^ ord(key[i % len(key)]))
    if encode: return base64.b64encode(text2.encode()).decode()
    else: return text2
    