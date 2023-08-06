# CamBank
# coding=utf-8

from camlib import BasicPage
from time import localtime

class CamBank (BasicPage.BasicPage):
 def __init__(self, username, data, crypt=None):
  BasicPage.BasicPage.__init__(self, 'CamBank')
  self.username = username
  self.metas['title'] = 'CamBank'
  self.metas['description'] = 'CamBank, le logiciel de compte personnel basé sur les budgets !'
  self._tree = None
  self._full_name = None
  self._id = None
  self.data = data
  self.crypt = crypt
  self.version = 5
  self.epargnes = None
  self.init_from_db()

 def get_version(self):
  return 'cambank-{} API-{} schema-{}'.format('2.2.2', self.version, self.schema_version)

 def init_from_db(self):
  self.sympass = None
  if self.data.select_one("select value from prefs where name='crypt'") == 'true':
   self.sympass = self.crypt
  del self.crypt

  self.schema_version = 0
  a = self.data.select_one("select value from prefs where name='dbversion'")
  if a:
   try:
    self.schema_version = int(a)
   except TypeError:
    pass

 def symcr(self, str):
  if self.sympass:
   return "pgp_sym_encrypt(%s,'%s')" % \
    (self.data.escape_string(str), self.sympass)
  else:
   return self.data.escape_string(str)

 def symde(self, col):
  if self.sympass:
   col = "pgp_sym_decrypt({}, '{}')".format(col, self.sympass)
  return "convert_from({}::bytea, 'utf8')".format(col)

 # crypt: boolean: do we want to crypt?
 def change_password(self, cur, new, crypt):
  def transform(col):
   newcol = col
   if self.sympass:
    if self.sympass != cur:
     raise Exception('Given password does not match Session password, please check')
    newcol = "pgp_sym_decrypt({}, '{}')".format(newcol, self.sympass)
   if crypt:
    newcol = "pgp_sym_encrypt(text({}), '{}')".format(newcol, new)
   return "{}=bytea({})".format(col, newcol)

  self.data.begin()
  if crypt is not None or self.sympass is not None:
   self.data.execute("update budgets set " + transform('bnom') + "," + transform('bcomment'))
   self.data.execute("update categories set " + transform('cnom'))
   self.data.execute("update operations set " + transform('olibelle') + ',' + transform('odetail'))
   self.data.execute("delete from prefs where name='crypt'")
   if crypt:
    self.data.execute("insert into prefs (name, value) values ('crypt', 'true')")

  if cur != new:
   self.data.execute("alter user %s with password '%s'" % (self.username, new))

  self.data.commit()

 def get_last_import_date(self, pattern):
  return self.data.select_one('select ' \
   'to_char(last_import, \'DD/MM/YYYY\') from last_import_date ' \
   'where pattern=\'%s\'' % (pattern))


 """ gestion des operations """

 def create_operation(self, date, detail, montant=0, libelle='Ajout manuel', commit=True):
  cur = self.data.execute('insert into operations ' \
   '(oid, odate, olibelle, odetail, omontant) values ' \
   '(nextval(\'cb.oid_seq\'), %s, %s, %s, %d) returning oid' %
   (self.data.escape_string(date) if date != '' else 'now()',
    self.symcr(libelle),
    self.symcr(detail),
    montant))
  oid = cur.fetchone()[0]
  if commit:
   self.data.commit()
  return int(oid)

 def get_last_operation_date(self):
  return self.data.select_one('select ' \
   'to_char(max(odate)+1, \'DD/MM/YYYY\') from operations')

 def get_pending_operations(self):
  ops = []
  for line in self.data.select_all('select oid from operations o ' \
    'where obalance<>omontant or (omontant=0 and not exists ' \
    '(select aid from actions a where a.oid=o.oid)) order by odate'):
   ops.append(Operation(self, line[0]))
  return ops

 def mask_operation(self, oid):
  op = Operation(self, oid)
  op.set_balance(op.omontant)


 """ gestion des categories """

 def create_category(self, nom, ordre):
  self.data.execute('update categories ' \
   'set corder=corder+1 where corder >= %d' % (ordre))
  self.data.execute('insert into categories ' \
   '(cnom, corder) values (%s, %d)' % \
   (self.symcr(nom), ordre))
  self.data.commit()

 def get_categories(self):
  cats = []
  for line in self.data.select_all('select cid from categories ' \
    'where cid > 0 order by corder'):
   cats.append(Category(self, line[0]))
  return cats


 """ gestion des budgets """

 def create_budget(self, nom, montant, comment, cid):
  self.data.execute('insert into budgets ' \
   '(bnom, bmontant, cid, bcomment) values (%s, %d, %d, %s)' %
   (self.symcr(nom), montant, cid,
    comment and self.symcr(comment) or 'NULL'))
  self.data.commit()

 def create_treso(self, nom, comment):
  if self.schema_version >= 2:
   try:
    _ = Category(self, 0)
   except:
    self.data.execute("insert into categories (cid,cnom,corder) values (0,'internal',0)")
   self.data.execute('insert into budgets ' \
    '(bnom, bmontant, cid, bcomment, btresorerie) values ' \
    '({}, {}, {}, {}, {})'.format(self.symcr(nom), 0, 0, self.symcr(comment), 'true'))
   self.data.commit()
  else:
   raise TypeError

 def get_budgets(self):
  buds = []
  for line in self.data.select_all('select bid from budgets order by bid'):
   buds.append(Budget(self,line[0]))
  return buds

 def get_sum_budgets(self):
  return self.data.select_one('select sum(bjauge) from budgets where bshow=true and cid<>0') or 0

 def get_sum_tresos(self):
  return self.data.select_one('select sum(bjauge)*-1 from budgets where bshow=true and cid=0') or 0

 def get_debts(self):
  return self.data.select_one('select sum(bjauge) from budgets where bshow=true and bjauge<0 and cid<>0') or 0

 def get_budgets_full(self):
  if self.schema_version >= 2:
   return self.data.select_all('select c.cid, %s, b.bid, %s, %s, bjauge, bmontant, to_char(coalesce(max(adate), \'1900-01-01\'), \'Le DD/MM/YYYY a HH24:MI:SS\'), btresorerie from budgets as b right join categories as c on (b.cid=c.cid) left outer join actions as a on (b.bid=a.bid) where bshow=true or bshow is null group by c.cid, cnom, b.bid, bnom, bcomment, bjauge, bmontant, corder order by corder, b.bid' % (self.symde('cnom'), self.symde('bnom'), self.symde('bcomment')));
  else:
   return self.data.select_all('select c.cid, %s, b.bid, %s, %s, bjauge, bmontant, to_char(coalesce(max(adate), \'1900-01-01\'), \'Le DD/MM/YYYY a HH24:MI:SS\') from budgets as b right join categories as c on (b.cid=c.cid) left outer join actions as a on (b.bid=a.bid) where bshow=true or bshow is null group by c.cid, cnom, b.bid, bnom, bcomment, bjauge, bmontant, corder order by corder, b.bid' % (self.symde('cnom'), self.symde('bnom'), self.symde('bcomment')));

 def get_budgets_summary(self):
  return self.data.select_all('select c.cid, %s, b.bid, %s, %s, bjauge, bmontant, to_char(coalesce(max(adate), \'1900-01-01\'), \'Le DD/MM/YYYY a HH24:MI:SS\') from budgets as b right join categories as c on (b.cid=c.cid) left outer join actions as a on (b.bid=a.bid) where bshow=true or bshow is null group by c.cid, cnom, b.bid, bnom, bcomment, bjauge, bmontant, corder order by corder, b.bid' % (self.symde('cnom'), self.symde('bnom'), self.symde('bcomment')));

 """ gestion des mensualites """

 def create_salary(self, bid, montant):
  self.data.execute('insert into mensualites ' \
    '(bid, mmontant) values (%d, %d)' %
    (bid, montant))
  self.data.commit()

 def get_salary(self):
  return self.data.select_all('select mid,bid,mmontant from mensualites order by mid')

 def delete_salary(self, mid):
  self.data.execute('delete from mensualites where mid=%d' % (mid))
  self.data.commit()

 def dispatch_salary(self, oid):
  sals = self.get_salary()
  for sal in sals:
   self.create_writing(self.get_action_ticket(), oid, sal[2], sal[1])


 """ gestion des epargnes """

 def create_epargne(self, nom, min, suppl, max, order):
  self.data.execute('insert into epargnes ' \
   '(ename, emin_jauge, esuppl_jauge, emax_balance, eorder) values (%s, %d, %d, %d, %d)'
   % (self.symcr(nom), min, suppl, max, order))
  self.data.commit()

 def get_epargnes(self):
  if self.epargnes == None:
   self.epargnes = []
   for e in self.data.select_all('select eid, %s, emin_jauge, ' \
     'esuppl_jauge, ebalance, ejauge, emax_balance, %s, eshow, eorder ' \
     'from epargnes order by eorder' %
     (self.symde('ename'), self.symde('ecomment'))):
    self.epargnes.append(Epargne(self, *e))
  return self.epargnes

 def get_epargne(self, eid):
  e = self.data.select_line('select eid, %s, emin_jauge, ' \
   'esuppl_jauge, ebalance, ejauge, emax_balance, %s, eshow, eorder ' \
   'from epargnes where eid=%d' %
   (self.symde('ename'), self.symde('ecomment'), int(eid)))
  return Epargne(self, *e)

 def hide_epargne(self, eid):
  self.data.execute('update epargnes set eshow=false where eid=%d' \
   % (eid))
  self.data.commit()

 def update_epargne(self, eid, nom, min, suppl, max, order):
  self.data.execute('update epargnes set ename=%s, emin_jauge=%d, esuppl_jauge=%d, emax_balance=%d, eorder=%d where eid=%d' % (self.symcr(nom), min, suppl, max, order, eid))
  self.data.commit()


 """ gestion des actions """

 def create_writing(self, aid, oid, montant, bid, epargne=0):
  if type(bid) == type('') and bid == 'auto':
   self.epargne(aid, oid, montant)
  elif type(bid) == type('') and bid[0] == 'e':
   ep = self.get_epargne(bid[1:])
   ep.bank(oid, montant, aid, epargne)
  else:
   bud = Budget(self, int(bid))
   bud.bank(oid, montant, aid)

 def check_action_ticket(self, aid):
  if aid > self.data.select_one('select greatest(0, max(aid)) from actions'):
   return self.data.select_one('select last_value from aid_seq')
  else:
   return -1

 def get_action_ticket(self):
  return self.data.select_one("select nextval('aid_seq')")

 def epargne(self, aid, oid, montant):
  def find_next():
   (eid, reste) = self.data.select_line('select eid, reste from (select ' \
    'eid, emin_jauge-ejauge as reste from epargnes where emin_jauge-ejauge' \
    ' > 0 and eshow=true order by eorder) as a limit 1') or (None, None)
   if reste and reste > 0:
    return (eid, reste)
   return (0, 0)

  def distrib_epargne(eid, combien, aid, oid):
   self.create_writing(aid, oid, combien, 'e%d' % (eid), 1)

  def dispatch(combien, aid, oid):
   init = combien
   es = self.data.select_all('select eid, round(1.0*esuppl_jauge/' \
    '(select sum(esuppl_jauge) from epargnes ' \
    'where ebalance < emax_balance and eshow=true)), ' \
    'emax_balance from epargnes where ebalance < emax_balance and ' \
    'eshow=true')
   for (eid, ratio, max) in es[0:len(es)-2]:
    allowable = min(init*ratio, max)
    distrib_epargne(eid, allowable, aid, oid)
    aid = self.get_action_ticket()
    combien -= allowable
   distrib_epargne(eid, combien, aid, oid)

  while montant > 0:
   (eid, reste) = find_next()
   if eid == 0:
    break
   distrib_epargne(eid, min(montant, reste), aid, oid)
   montant -= min(montant, reste)
   aid = self.get_action_ticket()
  if montant > 0:
   dispatch(montant, aid, oid)

 """
 treso est negatif, c'est un credit. quand on paye avec 12e :
 TX: insert into operation 0e, budget -12e, treso +12e, commit
 """
 def depense_treso(self, aid, date, tresoid, bid, montant, comment):
  if self.schema_version >= 2:
   bud = Budget(self, int(bid))
   treso = Budget(self, int(tresoid))
   oid = self.create_operation(date, comment, libelle='Depense Treso', commit=False)
   op = Operation(self, oid)
   bud.bank(op.oid, montant, aid, commit=False)
   treso.bank(op.oid, -montant, self.get_action_ticket()) # commit here
  else:
   raise TypeError

 def get_tresos(self):
  buds = []
  if self.schema_version >= 2:
   for line in self.data.select_all('select bid from budgets where btresorerie=true order by bid'):
    buds.append(Budget(self,line[0]))
  return buds


""" dans certains contextes, permet de melanger les budgets et les epargnes """

class Boite:
 def __init__(self, cb, type, id, nom, jauge, comment, show):
  self.cb = cb
  self.type = type
  self.id = id
  self.nom = nom
  self.jauge = jauge
  self.comment = comment
  self.show = show

 def get_actions(self):
  actions = []
  for line in self.cb.data.select_all('select aid from actions ' \
    'where bid=%d order by adate' % \
    self.id):
   actions.append(Action(self.cb, line[0]))
  return actions


""" budget : une boite où on peut mettre et retirer de l'argent """

class Budget(Boite):
 def __init__(self, cb, bid):
  self.bid = bid
  if cb.schema_version >= 2:
   row = cb.data.select_line('select %s, bmontant, bjauge, %s, cid, bshow, btresorerie from budgets where bid=%d' % (cb.symde('bnom'), cb.symde('bcomment'), bid))
   if row:
    (self.bnom, self.bmontant, self.bjauge, self.bcomment, self.cid, self.bshow, self.btresorerie) = row
   else:
    raise TypeError
  else:
   row = cb.data.select_line('select %s, bmontant, bjauge, %s, cid, bshow ' \
    'from budgets where bid=%d' % (cb.symde('bnom'), cb.symde('bcomment'),
    bid))
   if row:
    (self.bnom, self.bmontant, self.bjauge, self.bcomment, self.cid, self.bshow) = row
   else:
    raise TypeError
  Boite.__init__(self, cb, 'budget', bid, self.bnom, self.bjauge, self.bcomment, self.bshow)

 def get_max_adate(self):
  return localtime(self.cb.data.select_one('select extract(epoch from max(adate)) from actions ' \
   'where bid=%d and amontant > 0' % self.bid))

 def bank(self, oid, montant, aid, commit=True):
  self.cb.data.begin()
  aid = self.cb.check_action_ticket(aid)
  if aid > 0:
   op = Operation(self.cb, oid)
   self.cb.data.execute('insert into actions (aid, oid, bid, ' \
    'amontant) values (%d, %d, %d, %d)' % \
    (aid, oid, self.bid, montant))
   op.adjust_balance(montant)
   self.adjust_jauge(montant)
   if commit:
    self.cb.data.commit()
  else:
   self.cb.data.rollback()

 def set_nom(self, nom):
  self.bnom = nom
  self.cb.data.execute('update budgets set bnom=%s where bid=%d' % \
   (self.cb.symcr(nom), self.bid))
  self.cb.data.commit()

 def set_montant(self, montant):
  self.bmontant = montant
  self.cb.data.execute('update budgets set bmontant=%d where bid=%d' % \
   (montant, self.bid))
  self.cb.data.commit()

 def adjust_jauge(self, delta):
  self.bjauge += delta
  self.cb.data.execute('update budgets set bjauge=bjauge+%d where bid=%d' % (delta, self.bid))
  self.cb.data.commit()

 def set_comment(self, comment):
  if comment == '':
   self.comment = None
   self.cb.data.execute('update budgets set bcomment=NULL where bid=%d' % (self.bid))
  else:
   self.comment = comment
   self.cb.data.execute('update budgets set bcomment=%s where bid=%d' \
    % (self.cb.symcr(comment), self.bid))
  self.cb.data.commit()

 def set_category(self, cid):
  self.cid=cid
  self.cb.data.execute('update budgets set cid=%d where bid=%d' % (cid, self.bid))
  self.cb.data.commit()

 def delete(self):
  self.cb.data.execute('update budgets set bshow=false where bid=%d' % (self.bid))
  self.cb.data.commit()
  #try:
  # self.cb.data.execute('delete from budgets where bid=%d' % (self.bid))
  # self.cb.data.commit()
  #except:
  # pass

class Action:
 def __init__(self, cb, aid):
  self.cb = cb
  self.aid = aid
  (self.aid, self.adate, self.oid, self.bid, self.amontant) = \
   self.cb.data.select_line('select aid, extract(epoch from adate), oid, bid, amontant from actions where aid=%d' % (aid))
  self.adate = localtime(self.adate)

 def delete(self, commit = True):
  if commit:
   self.cb.data.begin()

  self.cb.data.execute('update operations set obalance = obalance - ' \
   '(select amontant from actions where aid=%d) ' \
   'where oid=(select oid from actions where aid=%d)' % (self.aid, self.aid))
  self.cb.data.execute('update budgets set bjauge = bjauge - ' \
   '(select amontant from actions where aid=%d) where ' \
   'bid=(select bid from actions where aid=%d)' % (self.aid, self.aid))
  self.cb.data.execute('update epargnes set ebalance = ebalance - ' \
   '(select amontant from actions where aid=%d) where ' \
   'eid=(select bid from actions where aid=%d)' % (self.aid, self.aid))
  self.cb.data.execute('delete from actions where aid=%d' % (self.aid))

  if self.cb.schema_version >= 2 and Budget(self.cb, self.bid).cid == 0:
   for act in Operation(self.cb, self.oid).get_actions():
    act.delete(commit = False)
   self.cb.data.execute('delete from operations where oid=%d' % (self.oid))

  if commit:
   self.cb.data.commit()


class Operation:
 def __init__(self, cb, oid):
  self.cb=cb
  self.oid = oid
  (self.odate, self.olibelle, self.odetail, self.omontant, \
   self.obalance, self.hint_bid) = cb.data.select_line('select extract(epoch from odate), %s, ' \
   '%s, omontant, obalance, coalesce(hint_bid, 0) from operations where oid=%d' % \
   (self.cb.symde('olibelle'), self.cb.symde('odetail'), oid))
  self.odate = localtime(self.odate)

 def set_balance(self, balance):
  self.obalance = balance
  self.cb.data.execute('update operations set obalance=%d where oid=%d' % (balance, self.oid))
  self.cb.data.commit()

 def adjust_balance(self, delta):
  self.obalance += delta
  self.cb.data.execute('update operations set obalance=obalance+%d where oid=%d' % \
   (delta, self.oid))
  self.cb.data.commit()

 def get_actions(self):
  aids = []
  for line in self.cb.data.select_all('select aid from actions where oid=%d' % (self.oid)):
   aids.append(Action(self.cb, line[0]))
  return aids

 def get_type(self):
  return {
   'CARTE': 'CARTE',
   'PAIEMENT': 'CARTE',
   'RETRAIT': 'RETRAIT',
   'VIREMENT': 'VIREMENT',
   'VIR': 'VIREMENT',
   'PRLV': 'PRELEVEMENT',
   'CHEQUE': 'CHEQUE',
   'CHQ.': 'CHEQUE',
  }.get(self.olibelle.split(' ', 1)[0], 'DIVERS')


class Category:
 def __init__(self, cb, cid):
  self.cb=cb
  self.cid=cid
  (self.cnom, self.corder) = cb.data.select_line('select %s, corder ' \
   'from categories where cid=%d' % (cb.symde('cnom'), cid))

 def set_nom(self, nom):
  if self.cid == 0:
   raise UnboundLocalError("this category has been deleted")
  self.cnom = nom
  self.cb.data.execute('update categories set cnom=%s where cid=%d' % \
   (self.cb.symcr(nom), self.cid))
  self.cb.data.commit()

 def set_order(self, order):
  if self.cid == 0:
   raise UnboundLocalError("this category has been deleted")
  if self.corder == order:
   pass
  self.cb.data.execute('update categories set corder=0 where cid=%d' % (self.cid))
  self.cb.data.execute('update categories set corder=corder-1 where corder > %d and corder <= %d' \
   % (self.corder, order))
  self.cb.data.execute('update categories set corder=corder+1 where corder < %d and corder >= %d' \
   % (self.corder, order))
  self.cb.data.execute('update categories set corder=%d where cid=%d' % (order, self.cid))
  self.corder = order
  self.cb.data.commit()

 def get_budgets(self):
  #if self.cid == 0:
  # raise UnboundLocalError("this category has been deleted")
  buds = []
  for line in self.cb.data.select_all('select bid from budgets where ' \
    'cid=%d order by bid' % self.cid):
   buds.append(Budget(self.cb, line[0]))
  return buds

 def delete(self):
  if self.cid == 0:
   pass
  # FIXME: create a Error handling mecanism and use it here and elsewhere
  #try:
  # self.cb.data.execute('delete from categories where cid=%d' % (self.cid))
  # self.cb.data.commit()
  # self.cid = 0
  # self.cnom = "deleted"
  #except:
  # pass
  self.cb.data.execute('delete from categories where cid=%d' % (self.cid))
  self.cb.data.commit()
  self.cid = 0
  self.cnom = "deleted"

class Epargne(Boite):
 def __init__(self, cb, eid, ename, emin_jauge, esuppl_jauge, ebalance, ejauge, emax_balance, ecomment, eshow, eorder):
  Boite.__init__(self, cb, 'epargne', eid, ename, ebalance, ecomment, eshow)
  self.eid = eid
  self.ename = ename
  self.emin_jauge = emin_jauge
  self.esuppl_jauge = esuppl_jauge
  self.ebalance = ebalance
  self.ejauge = ejauge
  self.emax_balance = emax_balance
  self.ecomment = ecomment or ""
  self.eshow = eshow
  self.eorder = eorder

 def bank(self, oid, montant, aid, epargne=0):
  self.cb.data.begin()
  aid = self.cb.check_action_ticket(aid)
  if aid > 0:
   op = Operation(self.cb, oid)
   self.cb.data.execute('insert into actions (aid, oid, bid, ' \
    'amontant) values (%d, %d, %d, %d)' % \
    (aid, oid, self.eid, montant))
   self.ebalance += montant
   self.cb.data.execute('update epargnes set ebalance=ebalance+%d ' \
    'where eid=%d' % (montant, self.eid))
   op.adjust_balance(montant)
   if epargne:
    self.cb.data.execute('update epargnes set ejauge=ejauge+%d ' \
     'where eid=%d' % (montant, self.eid))
    self.ejauge += montant
   self.cb.data.commit()
  else:
   self.cb.data.rollback()
