# coding=utf-8
from camlib import InputController
from cambank import CamBank, CamBankHTML

class Input(InputController.InputController):
 def __init__(self, page, form):
  self._page = page
  self._form = form

 def process_input(self):
  page = self._page
  form = self._form

  if 'tresoid' in form and 'aid' in form and 'montant' in form and 'bid' in form:
   tresoid = int(form['tresoid'].value)
   if 'label' in form:
    label = form['label'].value
   else:
    treso = CamBank.Budget(page, tresoid)
    label = 'Depense de tresorerie {}'.format(treso.bnom)
   page.depense_treso(int(form['aid'].value), '', tresoid,
     int(form['bid'].value), float(form['montant'].value.replace(',', '.'))*-100,
     label)
   return "index.cgi"

  if 'setpass' in form and 'curpass' in form and \
    'newpass' in form and 'crypt' in form:
   page.change_password(form['curpass'].value, form['newpass'].value, form['crypt'].value == 'y' and True or False)
   return "index.cgi"

  if 'deloid' in form:
   page.mask_operation(int(form['deloid'].value))
   return "index.cgi"

  if 'dispatchsalary' in form:
   page.dispatch_salary(int(form['dispatchsalary'].value))
   return "index.cgi"

  if 'aid' in form and 'oid' in form and 'montant' in form \
    and 'bid' in form:
   page.create_writing(int(form['aid'].value), int(form['oid'].value),
    int("%.0f" % (float(form['montant'].value.replace(',','.'))*100)),
    form['bid'].value)
   return "index.cgi"

  if 'date' in form and 'detail' in form \
    and 'montant' in form:
   page.create_operation(form['date'].value, form['detail'].value,
    int(float(form['montant'].value)*100))
   return "index.cgi"

  if 'newcnom' in form and 'corder' in form:
   page.create_category(form['newcnom'].value, int(form['corder'].value))
   return "index.cgi?editcat=1"

  if 'cid' in form and 'cnom' in form and 'corder' in form:
   cat = CamBank.Category(page, int(form['cid'].value))
   cat.set_nom(form['cnom'].value)
   cat.set_order(int(form['corder'].value))
   return "index.cgi?editcat=1"

  if 'delcatid' in form:
   cat = CamBank.Category(page, int(form['delcatid'].value))
   cat.delete()
   return "index.cgi?editcat=1"

  if 'newbnom' in form and 'cid' in form: # and 'bmontant' in form:
   if form['cid'].value == '0':
    page.create_treso(form['newbnom'].value, form['bcomment'].value if 'bcomment' in form else '')
   elif 'bmontant' in form:
    page.create_budget(form['newbnom'].value, int(float(form['bmontant'].value)*100),
    'bcomment' in form and form['bcomment'].value or '', int(form['cid'].value))
   return "index.cgi?editcatid=%d" % (int(form['cid'].value))

  if 'bnom' in form and 'cid' in form and 'bid' in form and 'bmontant' in form:
   bud = CamBank.Budget(page, int(form['bid'].value))
   cid = bud.cid+0
   bud.set_nom(form['bnom'].value)
   bud.set_category(int(form['cid'].value))
   bud.set_comment('bcomment' in form and form['bcomment'].value or '')
   bud.set_montant(int(float(form['bmontant'].value)*100))
   return "index.cgi?editcatid=%d" % (cid)

  if 'delbid' in form:
   bud = CamBank.Budget(page, int(form['delbid'].value))
   cid = bud.cid
   bud.delete()
   return "index.cgi?editcatid=%d" % (cid)

  if 'cancelaid' in form:
   act = CamBank.Action(page, int(form['cancelaid'].value))
   act.delete()
   if 'histobid' in form:
    return "index.cgi?histobid=%d" % (int(form['histobid'].value))
   else:
    return "index.cgi"

  if 'salary' in form and 'bid' in form and 'montant' in form:
   page.create_salary(int(form['bid'].value), int(float(form['montant'].value)*100))
   return "index.cgi?salary=1"

  if 'salary' in form and 'mid' in form:
   page.delete_salary(int(form['mid'].value))
   return "index.cgi?salary=1"

  if 'epargne' in form and 'nom' in form and 'min' in form \
    and 'max' in form and 'suppl' in form and 'order' in form:
   page.create_epargne(form['nom'].value, int(form['min'].value)*100,
    int(form['suppl'].value)*100, int(form['max'].value)*100,
    int(form['order'].value))
   return "index.cgi?epargne=1"

  if 'hideeid' in form:
   page.hide_epargne(int(form['hideeid'].value))
   return "index.cgi?epargne=1"

  if 'seteid' in form and 'nom' in form and 'min' in form \
    and 'max' in form and 'suppl' in form and 'order' in form:
   page.update_epargne(int(form['seteid'].value), form['nom'].value,
    int(form['min'].value)*100, int(form['suppl'].value)*100,
    int(form['max'].value)*100, int(form['order'].value))
   return "index.cgi?epargne=1"
