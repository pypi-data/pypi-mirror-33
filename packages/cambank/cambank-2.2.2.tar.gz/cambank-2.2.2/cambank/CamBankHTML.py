# CamBankHTML
# coding=utf-8

import locale
from camlib import BasicHTMLController
from cambank.CamBank import *
from cambank import QifParser
from time import strftime
import re

class HTML(BasicHTMLController.BasicHTMLController):
 def __init__(self, parent):
  BasicHTMLController.BasicHTMLController.__init__(self, parent)
  locale.setlocale(locale.LC_ALL, ('fr_FR', 'utf-8'))
  self.html_version = 2

 def get_headers(self):
  html = BasicHTMLController.BasicHTMLController.get_headers(self)
  return '''
<meta name="application-name" content="CamBank"/>
<link rel="shortcut icon" href="../images/cambank-16x16.png">
<link rel="icon" href="../images/cambank-32x32.png" sizes="32x32"/>
<link rel="icon" href="../images/cambank-48x48.png" sizes="48x48"/>''' + html

 def show_headers(self):
  return """
<div style="text-align: center; margin-top: 0" class="box">
<a href="index.cgi"><img src="../images/cambank.png" alt="CamBank Logo"/></a>
<h6 style="margin-top: 0">Le logiciel de compte personnel<br/>bas&eacute; sur les budgets&nbsp;!</h6>
<h4>
<a href="index.cgi">Accueil</a> &mdash;
<a href="index.cgi?help=1">Aide</a> &mdash;
<a href="index.cgi?prefs=1">Pr&eacute;f&eacute;rences</a> &mdash;
<a href="index.cgi?logout=1">D&eacute;connecter</a>
</h4>
<h4>
<a href="index.cgi?import=0">Importer des &eacute;critures</a> &mdash;
<!-- <a href="index.cgi?epargne=1">&Eacute;pargnes</a> &mdash; -->
<a href="index.cgi?salary=1">Mensualit&eacute;s</a>
</h4>
</div>
"""

 def get_style(self):
  style = '''
body {
 font-family: sans-serif, Arial;
 font-size: smaller;
 background-color: #EBFFEC;
}
.edit {
 font-size: smaller;
}
h2 {
 font-weight: bold;
 color: white;
 padding: 0.2em;
 padding-left: 0.8em;
 margin: 1px;
 width: 50%;
 background-color: #3C6C42;
}
input, select {
 font-family: sans-serif, Arial;
 background-color: #D4FFD9;
 border: solid 1px;
}
.box > table {
 background-color: #3C6C42;
 padding: 1px;
 margin: 0;
 margin-left: 5em;
}
.box > table td {
 padding: 0.3em 1em;
 background-color: #D4FFD9;
}
.box > table th {
 color: white;
}
.detail {
 width: 20em;
}
img {
 border: 0;
}
.box {
 margin-top: 5em;
}
.category_name {
 font-size: larger;
}
a {
 color: black;
 font-weight: bold;
/* text-decoration: none; */
}
td.number {
 text-align: right;
}
'''
  return style

 def get_cached_budgets(self):
  if 'cached_budgets' not in dir(self):
   self.cached_objects = self.cb.get_budgets_full()
  return self.cached_budgets

 def show_retour_accueil(self):
  return """
<p>
<a href="index.cgi">Revenir à la page d'accueil</a>
</p>
"""

 def show_footers(self):
  cb = self._parent
  return """
<h6 id="footer">
CamBank &copy; 2008-2018 Camille Huot.<br/>
{} HTML-{}
</h6>
""".format(cb.get_version(), self.html_version)

class Home(HTML):
 def __init__(self, cb):
  HTML.__init__(self, cb)

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.show_pending_operations()
  html += self.show_tresos()
  html += self.show_budgets()
  #html += self.show_epargnes()
  html += self.show_create_operation_form()
  html += self.show_footers()
  return html

 def show_create_operation_form(self):
  return '''
<div class="box">
<h2>Ajouter une op&eacute;ration manuelle</h2>
<form>
<table>
<tr><th align="right">Date :</th><td><input type="text" name="date"/></td></tr>
<tr><th align="right">Details :</th><td><input type="text" name="detail"/></td></tr>
<tr><th align="right">Montant :</th><td><input type="text" name="montant"/></td></tr>
<tr><th></th><td><input type="image" src="../images/valid.png" style="border: 0"/></td></tr>
</table>
</form>
</div>'''

 def print_budgets_menu(self, default = 0, exclude = -1):
  cb = self._parent
  buds = cb.get_budgets()
  budgets_item = "<select name=\"bid\">\n"
  for bud in buds:
   if bud.bshow is False:
    continue
   if bud.bid == exclude:
    continue
   if bud.bid == default:
    budgets_item += "<option value=\"%d\" selected>%s</option>\n" % \
     (bud.bid, bud.bnom)
   else:
    budgets_item += "<option value=\"%d\">%s</option>\n" % \
     (bud.bid, bud.bnom)
  budgets_item += "</select>\n"
  return budgets_item

 def show_pending_operations(self):
  cb = self._parent
  actionid = cb.get_action_ticket()
  ops = cb.get_pending_operations()
  if len(ops) == 0:
   return ''
  html = '<div class="box">'

  # montant minimum pour considerer l'operation comme un salaire
  salaire = 0
  for sal in cb.get_salary():
   salaire += sal[2]

  for optype in sorted(set([ o.get_type() for o in ops ])):
   html += "<h2>Op&eacute;rations en attente de traitement : %s</h2>\n" % (optype)
   html += "<table>\n<tr>\n"
   html += "<th>Date</th>\n"
   html += "<th>D&eacute;tails de l'op&eacute;ration</th>\n"
   html += "<th>Euros</th>\n"
   html += "<th>Allouer cette op&eacute;ration &agrave; un budget</th>\n"
   html += "<th>Supprimer</th>\n"
   html += "</tr>\n"
   myops = [ o for o in ops if o.get_type() == optype ]
   nbops=len(myops)
   for op in myops:
     salairehtml = ''
     if salaire > 0 and op.omontant-op.obalance > salaire:
      salairehtml += '<tr><td>Traiter comme un salaire (allouer automatiquement %d EUR dans les budgets predefinis)&nbsp;:</td><td>' % (salaire/100)
      salairehtml += '<a href="index.cgi?dispatchsalary=%d"><img src="../images/valid.png" style="border: 0"/></a>' % (op.oid)
      salairehtml += '</td><tr><tr><td colspan="2" style="text-align: center"><hr/></td></tr>'

     html += """
     <tr>
     <td class="date">
     %s
     </td>
     <td class="detail">
     %s
     </td>
     <td>
     %.2f
     </td>
     <td>
     <form>
     <input type="hidden" name="oid" value="%d"/>
     <input type="hidden" name="aid" value="%d"/>
     <table>%s
     <tr><td align="right">Allouer&nbsp;:</td><td>
     <input name="montant" value="%.2f" size="4" style="text-align: right;"/>&thinsp;E</td></tr>
     <tr><td align="right">Au budget&nbsp;:</td><td>
     """ % (strftime('%x', op.odate), op.odetail,
       float(op.omontant)/100, op.oid, actionid, salairehtml,
       float((op.omontant-op.obalance))/100)
     html += self.print_budgets_menu(op.hint_bid)
     html += """
     </tr>
     <tr><td></td><td><input type="image" src="../images/valid.png" style="border: 0"/></td>
     </table>
     </form>
     </td>
     <td>
     <a href="index.cgi?deloid=%d"><img src="../images/delete.png" title="Supprimer cette op&eacute;ration"/></a>
     </td>
     </tr>
     """ % (op.oid)
   html += "<tr><th colspan=\"5\">%d sur %d op&eacute;ration(s) en attente de traitement</th></tr></table>" % (len(myops), len(ops))
  html += "</div>\n"
  return html

 def show_tresos(self):
  cb = self._parent
  tresos = cb.get_tresos()
  actionid = cb.get_action_ticket()
  if len(tresos) == 0:
   return ""
  html = """
<div class="box">
<h2>Trésorerie</h2>
<table>
<tr><th><span class="category_name">Nom</span></th><th>Montant</th><th>Créer opération</th></tr>
"""
  for treso in tresos:
   if treso.bcomment:
    treso.bcomment = '<br/>(%s)' % (treso.bcomment.replace("\n", '<br/>'))
   else:
    treso.bcomment = ''
   html += '<tr><td><a href="index.cgi?histobid=%d">%s</a>%s</td>' % (treso.bid, treso.bnom, treso.bcomment)
   html += locale.format_string('<td class="number">%.2f</td>', float(-1*treso.bjauge)/100)
   html += '''<td><form>Dépense
     <input type="hidden" name="tresoid" value="{}"/>
     <input type="hidden" name="aid" value="{}"/>
     <input name="montant" size="4" style="text-align: right;"/>&thinsp;E
     pour '''.format(treso.bid, actionid)
   html += self.print_budgets_menu(exclude = treso.bid)
   html += """ - label <input name="label" size="20" style="text-align: right;"/>
     <input type="image" src="../images/valid.png" style="border: 0"/>
     </form></td></tr>"""
  html += '''
<tr><th colspan="3" class="edit"><a href="index.cgi?editcatid=0">(éditer les trésoreries)</a>
</th></tr>
</table>
<p>Total des tresos&nbsp;: %.2f Euros.</p>
</div>''' % (float(cb.get_sum_tresos())/100)
  return html

 def show_budgets(self):
  cb = self._parent
  html = """
<div class="box">
<h2>Liste des budgets</h2>
<table>
"""
  cur_cat = -1
  for (cid, cnom, bid, bnom, bcomment, bjauge, bmontant, blastdate) in cb.get_budgets_summary():
   if cid == 0:
    continue
   if cid != cur_cat:
    cur_cat = cid
    html += '<tr><th><span class="category_name">Categorie %s</span><br/><span class="edit">' \
     '<a href="index.cgi?editcatid=%d">(&eacute;diter les budgets)</a></span></th>' \
     % (cnom, cid)
    if bid is None:
     html += '<th solspan="3"></th></tr>'
     continue
    html += '<th>Montant<br/>allou&eacute;</th>' \
     '<th>Montant<br/>cible</th><th>Date du dernier d&eacute;p&ocirc;t</th></tr>'
   if bcomment:
    bcomment = '<br/>(%s)' % (bcomment.replace("\n", '<br/>'))
   else:
    bcomment = ''
   html += '<tr><td><a href="index.cgi?histobid=%d">%s</a>%s</td>' % \
    (bid, bnom, bcomment)
   html += locale.format_string('<td class="number">%.2f</td>', float(bjauge)/100)
   html += locale.format_string('<td class="number">%d</td>', float(bmontant)/100)
   html += '<td style="text-align: center">%s</td></tr>' % (blastdate and blastdate or 'Jamais')
  html += '<tr><th colspan="4" class="edit"><a href="index.cgi?editcat=1">(&eacute;diter les ' \
   "cat&eacute;gories)</a></th></tr>\n"
  html += "</table>\n"
  html += "<p>Total des budgets&nbsp;: %.2f Euros.</p>" % (float(cb.get_sum_budgets())/100)
  html += "<p>Total des dettes&nbsp;: %.2f Euros.</p>" % (float(cb.get_debts())/100)
  html += "</div>"
  return html

 def show_epargnes(self):
  cb = self._parent
  html = """
<div class="box">
<h2>Épargnes</h2>
<table>
<tr>
<th>Épargne</th>
<th>Montant<br/>allou&eacute;</th>
<th>Montant<br/>cible</th>
<th>Montant<br/>réel</th>
</tr>
"""
  for ep in cb.get_epargnes():
   if ep.eshow is False:
    continue
   if ep.ecomment:
    comment='<br/>(%s)' % (ep.ecomment.replace("\n", '<br>'))
   else:
    comment=''
   html += """
<tr>
<td><a href="index.cgi?histobid=%d">%s</a>%s</td>
<td class="number">%s</td>
<td class="number">%s</td>
<td class="number">%s</td>
</tr>
""" % (ep.eid, ep.ename, comment, locale.format_string('%.2f',
    float(ep.ejauge)/100), locale.format_string('%d',
    float(ep.emax_balance)/100),
    locale.format_string('%.2f', float(ep.ebalance)/100))
  html += """
</table>
"""
  return html


class Histo(HTML):
 def __init__(self, cb, bid):
  HTML.__init__(self, cb)
  self.bid = bid

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.show_budget_history()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def show_budget_history(self):
  not_a_budget = 0
  try:
   bud = Budget(self._parent, self.bid)
  except:
   not_a_budget = 1

  if not_a_budget:
   bud = self._parent.get_epargne(self.bid)
   if not bud:
    return 'nonono'

  html = ''
  html += """
<div class="box">
<h2>Historique de la boite %s</h2>
<table>
<tr><th>Date action</th><th>D&eacute;tails</th><th>Date op&eacute;ration</th><th>Montant</th><th>Annuler</th></tr>
""" % (bud.nom)
  for action in reversed(bud.get_actions()):
   op = Operation(self._parent, action.oid)
   html += """
<tr><td>%s</td><td><a href="index.cgi?viewoid=%d">%s</a></td><td align="right">%s</td><td align="right">%.2f</td>
 <td><a href="index.cgi?histobid=%d&amp;cancelaid=%d"><img src="../images/undo.png" alt="Annuler cette action" /></a></td></tr>
""" % (strftime('Le %x &agrave; %X', action.adate), op.oid, op.odetail, strftime('%x', op.odate), float(action.amontant)/100, self.bid, action.aid)
  html += """
<tr><th colspan="4" align="right">Montant actuel du budget</th><th>%.2f</th></tr>
</table>
</div>
""" % (float(bud.jauge)/100)
  return html

class UploadImport(HTML):
 """
 Cette page gere toute la partie IMPORTATION des ecritures bancaires dans CamBank.
 - Un texte explique brievement ce qu'il faut faire
 - Un formulaire permet d'uploader un fichier QIF
 - Une boite affiche le resultat de la lecture de ce fichier
 - Un tableau permet de selectionner quelles ecritures inserer
 - Une boite affiche le resultat de l'insertion
 """

 def __init__(self, cb):
  HTML.__init__(self, cb)
  self.file = 'NO'
  self.oids = []

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.show_upload_help()
  if self.file != 'NO':
   html += self.read_csv()
  html += self.load_operations()
  html += self.show_upload_form()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def show_upload_help(self):
  html = """
<p>
Cette page permet d'inserer dans CamBank des ecritures provenant de votre compte
bancaire.
</p>
<p>
Pour cela, vous devez telecharger depuis votre interface bancaire un export au format QIF (Money) et le chargez ici.
</p>
<p>
Vous aurez ensuite la possibilite d'inserer, ligne par ligne, les ecritures dans CamBank ou eventuellement de les supprimer.
</p>
<p>
Vous pouvez supprimer, par exemple, les transferts entre comptes, qui sont donc ni des entrees ni des sorties d'argent.
</p>
<h4>Quelques liens pour telecharger des ecritures</h4>
<table>
<tr>
<td><img src="../images/logo_ingdirect.gif"/></td>
<td><a href="https://secure.ingdirect.fr/public/displayLogin.jsf">ING Direct</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
<tr>
<td><img src="../images/logo_boursorama.gif"/></td>
<td><a href="https://clients.boursorama.com/documents/generer">Boursorama</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
<tr>
<td><img src="../images/logo_bnp.png"/></td>
<td><a href="https://mabanque.bnpparibas/fr/connexion/virements-services/telechargement-des-operations">BNP Paribas COURANT</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
<tr>
<td><img src="../images/logo_bnp.png"/></td>
<td><a href="https://mabanque.bnpparibas/fr/connexion/virements-services/telechargement-des-operations">BNP Paribas COMMUN</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
<tr>
<td><img src="../images/logo_sg.gif"/></td>
<td><a href="https://www.particuliers.societegenerale.fr/">Soci&eacute;t&eacute;G&eacute;n&eacute;rale</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
<tr>
<td><img src="../images/logo-fortuneo.gif"/></td>
<td><a href="https://www.fortuneo.fr/fr/identification.jsp">Fortuneo</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
<tr>
<td><img src="../images/logo_lcl.gif"/></td>
<td><a href="https://particuliers.secure.lcl.fr/index.html">Cr&eacute;dit Lyonnais</a></td>
<td>Chargez le releve a partir du : %s</td>
</tr>
</table>
""" % (
    self._parent.get_last_import_date('40000441192_[0-9_]*.qif') or '[aucune op&eacute;ration dans la base]',
    self._parent.get_last_import_date('00040094318_R[0-9]*.[0-9]*.qif') or '[aucune op&eacute;ration dans la base]',
    self._parent.get_last_import_date('E2900888.*qif') or '[aucune op&eacute;ration dans la base]',
    self._parent.get_last_import_date('E2903982.*qif') or '[aucune op&eacute;ration dans la base]',
    self._parent.get_last_import_date('00057693757.*.qif') or '[aucune op&eacute;ration dans la base]',
    self._parent.get_last_import_date('HistoriqueOperations_.*.qif') or '[aucune op&eacute;ration dans la base]',
    self._parent.get_last_import_date('T_cpte_.*.qif') or '[aucune op&eacute;ration dans la base]',
   )
  return html

 def read_csv(self):
  """
  Ouvre le fichier envoye par le client et extrait les lignes.
  Le fichier est actuellement traite obligatoirement comme un fichier QIF.
  Il est passe a un convertisseur CSV pour reutiliser le code existant.
  """
  db = self._parent.data
  html = ""
  html += """
<div class="box">
<h2>Lecture du fichier CSV</h2>
<p>Ouverture du fichier&nbsp;:
"""
  try:
   if self.file.filename.lower().endswith('.ofx'):
    items = QifParser.parseOfx(self.file.file)
   elif self.file.filename.lower().endswith('.qif'):
    items = QifParser.parseQif(self.file.file)
   elif self.file.filename.lower().endswith('.csv'):
    items = QifParser.parseEpaymentsCSV(self.file.file)
   else:
    html += "<strong>Fatal: unrecognised file extension (supported: .qif .ofx)</strong>"
    return html
  except Exception as e:
   html += "<strong>&Eacute;chec&nbsp;: %s</strong></p></div>" % (str(e))
   return html

  html += """
OK
</p>
<table>
<tr><th>Date</th><th>Libelle</th><th>Lecture</th></tr>
"""
  if len(items) < 1:
   html += "<tr><td colspan=\"3\">Pas d'enregistrement dans le fichier&nbsp;!?</td></tr>"
   html += "</table></div>"
   return html
  for item in items:
   line = item.getCamBankCSV()
   try:
    tab = line.split(';')
   except Exception as e:
    html += "<tr><td colspan=\"2\">%s</td><td><strong>&Eacute;chec split&nbsp;: %s</strong>" \
     "</td></tr>" % (line, str(e))
    continue
   try:
    db.execute('set DATESTYLE to European')
    db.execute('insert into raw_operations (odate,olibelle,odetail,omontant) ' \
     'values (%s,%s,%s,%s)' % (self._parent.symcr(tab[0]),
	 self._parent.symcr(tab[1]), self._parent.symcr(tab[2]),
	 self._parent.symcr(tab[3])))
    db.execute('update last_import_date set last_import=1+to_date(\'%s\',\'DD/MM/YYYY\') where last_import < to_date(\'%s\',\'DD/MM/YYYY\') and \'%s\' ~ pattern' % (tab[0], tab[0], self.file.filename))
   except Exception as e:
    html += "<tr><td>%s</td><td>%s</td><td><strong>&Eacute;chec insert&nbsp;: %s</strong>" \
     "</td></tr>" % (tab[0], line, str(e))
    continue
   html += "<tr><td>%s</td><td>%s</td><td>OK</td></tr>" % (tab[0], tab[1])
  db.commit()
  html += "</table></div>"
  return html

 def show_upload_form(self):
  return '''
<div class="box">
<h2>Importer un fichier d'ecritures %s</h2>
<form action="index.cgi" method="POST" enctype="multipart/form-data">
<table>
<tr><th align="right">Choisir un fichier CSV &agrave; importer&nbsp;:</th>
<td><input type="file" name="upload" /></td></tr>
<tr><td></td><td><input type="image" src="../images/valid.png" style="border: 0"/></td>
</table>
</form>
</div>''' % (str(type(self)))


 def load_operations(self):
  """
  Cette fonction lit et affiche la table raw_operations afin
  que l'utilisateur valide les ecritures a inserer dans la table operations.
  """
  last_date = None
  db = self._parent.data
  lines = db.select_all('select oid,%s,%s,%s,%s ' \
   'from raw_operations where onouveau=true' % (self._parent.symde('odate'),
   self._parent.symde('olibelle'), self._parent.symde('odetail'),
   self._parent.symde('omontant')))
  if len(lines) < 1:
   """
   La table est vide, on n'affiche pas le tableau.
   """
   return ''

  bid_filters={}
  for line in db.select_all('select hints, bid from budgets where hints is not null and bshow=true'):
   bid_filters[re.compile(line[0])] = line[1]
  def best_bid(msg):
   for pat in bid_filters.keys():
    if pat.search(msg):
     return bid_filters[pat]

  html = ""
  html += """
<div class="box">
<h2>Insertions des nouvelles op&eacute;rations en base de donn&eacute;es</h2>
<p>
Verifiez qu'il n'y a pas d'erreur avant de valider l'insertion des ecritures.
</p>
<table>
<form>
<tr><th>Date</th><th>Libelle</th><th>Insertion</th></tr>
"""
  for line in lines:
   # self.oids contient la liste des oid selectionnes pour etre inseres
   if self.oids and str(line[0]) in self.oids:
    # l'oid est selectione, on cherche le meilleur budget et on insere
    try:
     db.execute('set DATESTYLE to European')
     db.execute('insert into operations (oid,odate,olibelle,odetail,omontant)' \
      ' values (%d, \'%s\', %s, %s, %d)' % (line[0], line[1],
      self._parent.symcr(line[2]), self._parent.symcr(line[3]),
	  int(line[4].replace(',','').replace('.',''))))
     bb = best_bid(line[2])
     if bb:
      db.execute('update operations set hint_bid=%d where oid=%d' % (bb, line[0]))
     db.execute('update raw_operations set onouveau=false where oid=%d' % (line[0]))
     html += "<tr><td>%s</td><td>%s</td><td><strong>Insertion reussie</strong>" \
      "</td></tr>" % (line[1], line[2])
    except Exception as e:
     # erreur lors de l'insertion
     html += "<tr><td>%s</td><td>%s</td><td><strong>&Eacute;chec&nbsp;: %s</strong>" \
      "</td></tr>" % (line[1], line[2], str(e))
     continue
   else:
    # l'oid n'est pas selectione, on affiche la checkbox
    html += '<tr><td>%s</td><td>%s</td><td><input type="checkbox" name="import" ' \
     'value="%d" checked="checked"/></td></tr>' % (line[1], line[3], line[0])
  html += '<tr><th colspan="3"><input type="submit" value="Ajouter" /></th></tr>'
  html += '</form>'
  html += '</table>'
  html += '</div>'
  db.commit()
  return html

class EditCategories(HTML):
 def __init__(self, cb):
  HTML.__init__(self, cb)
  self.cats = self._parent.get_categories()

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += """
<p>
Les <strong>cat&eacute;gories</strong> permettent de classer les budgets. Par
exemple, les budgets mensuels, les budgets annuels, les autres budgets. Un
budget est obligatoirement rang&eacute; dans une cat&eacute;gorie. Il faut donc
cr&eacute;er au moins une cat&eacute;gorie avant de pouvoir cr&eacute;er un
budget, quitte &agrave; l'appeler <em>Budgets</em>.
</p>
<p>
Pour pouvoir supprimer compl&egrave;tement une cat&eacute;gorie, il faut
qu'elle ne contienne aucun budget.<!-- Sinon, elle ne sera que masqu&eacute;e.-->
</p>
"""
  html += self.show_editable_categories()
  html += self.show_empty_category()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def show_editable_categories(self):
  html = ''
  if len(self.cats) > 0:
   html += """
<div class="box">
<h2>&Eacute;diter les cat&eacute;gories</h2>
<table>
<tr><th>Nom</th><th>Ordre d'affichage</th><th></th></tr>
"""
   for cat in self.cats:
    html += """
<tr>
<form>
<td>
<input type="hidden" name="cid" value="%d"/>
<input type="text" name="cnom" value="%s"/>
</td>
<td>
<select name="corder">
%s
</select>
</td>
<td><input type="image" src="../images/valid.png" style="border: 0" title="Valider la modification"/></td>
</form>
<form>
<td>
<input type="hidden" name="delcatid" value="%d"/>
<input type="image" src="../images/delete.png" style="border: 0" title="Supprimer la categorie"/></td>
</form>
</tr>
""" % (cat.cid, cat.cnom, self.get_order_select(cat.corder), cat.cid)
   html += """
</table>
<!--
<p>
<strong>Note</strong>&nbsp;: La suppression d'une cat&eacute;gorie non-vide provoquera sa disparition
de l'&eacute;cran principal mais restera en base de donn&eacute;es.
</p>
-->
</div>
"""
  return html

 def show_empty_category(self):
  html = ''
  html += """
<div class="box">
<h2>Cr&eacute;er une nouvelle cat&eacute;gorie</h2>
<table>
<tr><th>Nom</th><th>Ordre d'affichage</th><th></th></tr>
<tr>
<form>
<td>
<input type="text" name="newcnom" value=""/>
</td>
<td>
<select name="corder">
%s
</select>
</td>
<td><input type="image" src="../images/valid.png" style="border: 0"/></td>
</form>
</tr>
</table>
</div>
""" % (self.get_order_select(10000))
  return html

 def get_order_select(self, corder):
  html = ''
  if corder != 1:
   html += '<option value="1">En premier</option>'
  for cat in self.cats:
   if cat.corder == corder-1:
    continue
   if cat.corder == corder:
    html += '<option selected="selected" value="%d">Pas de modification</option>' \
     % (cat.corder)
    continue
   if cat.corder < corder:
    html += '<option value="%d">Apr&egrave;s %s</option>' % (cat.corder+1, cat.cnom)
   else:
    html += '<option value="%d">Apr&egrave;s %s</option>' % (cat.corder, cat.cnom)
  return html

class EditCategory(HTML):
 def __init__(self, cb, cid):
  HTML.__init__(self, cb)
  self.cat = Category(cb, cid)
  self.buds = self.cat.get_budgets()
  self.cats = cb.get_categories()

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += """
<p>
Cette page permet d'ajouter, de modifier et de supprimer des
<strong>budgets</strong>.
</p>
<p>
Un budget est comparable &agrave; une boite dans laquelle on met un peu
d'argent chaque mois et on peut piocher lorsque le besoin s'en fait sentir.
</p>
<p>
Chaque budget poss&egrave;de un <strong>montant cible</strong> qui indique
quelle somme la boite devrait contenir au final.
</p>
<p>
Un <strong>commentaire</strong> permet de donner des pr&eacute;cisions sur le
fonctionnement du budget. Par exemple, s'agit-il d'un budget mensuel (facture
SFR, loyer...), d'un budget annuel (imp&ocirc;t sur le revenu, assurance
voiture...) ou un budget sans limite (r&eacute;serve au cas o&ugrave;, futur
achat de voiture...)&nbsp;? Combien faut-il placer par mois pour atteindre 400
euros par an&nbsp;? Pour quelle date est-ce que le budget de l'assurance
voiture doit-&ecirc;tre rempli&nbsp;?
</p>
<p>
Un budget se remplit d'<strong>actions</strong> au fil du temps. Un budget qui
contient des actions (donc, qui a un historique) ne peut &ecirc;tre
supprim&eacute;. En revanche, il peut &ecirc;tre d&eacute;sactiv&eacute; et
ainsi disparaitre de la page principale. Un budget d&eacute;sactiv&eacute; peut
&ecirc;tre r&eacute;activ&eacute; &agrave; tout moment &agrave; partir de cette
page.
</p>
"""
  html += self.show_editable_budgets()
  html += self.show_empty_budget()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def show_editable_budgets(self):
  html = ''
  if len(self.buds) > 0:
   html += """
<div class="box">
<h2>&Eacute;diter les budgets de la cat&eacute;gorie "%s"</h2>
<table>
<tr><th>Nom</th><th>Montant</th><th>Commentaire</th><th>D&eacute;placer vers...</th><th colspan="2"></th></tr>
<th><!-- bouton edit --></th><th><!-- bouton delete --></th></tr>
""" % (self.cat.cnom)
   for bud in self.buds:
    html += """
<tr>
<form>
<input type="hidden" name="bid" value="%d"/>
<td>
<input type="text" name="bnom" value="%s"/>
</td>
<td>
<input type="text" name="bmontant" value="%.2f" size="5"/>
</td>
<td>
<textarea name="bcomment">%s</textarea>
</td>
<td>
<select name="cid">
%s
</select>
</td>
<td><input type="image" src="../images/valid.png" style="border: 0" title="Valider la modification"/></td>
</form>
<form>
<td>
<input type="hidden" name="delbid" value="%d"/>
<input type="image" src="../images/delete.png" style="border: 0" title="Supprimer le budget"/></td>
</form>
</tr>
""" % (bud.bid, bud.bnom, float(bud.bmontant)/100, bud.bcomment or '', self.get_cat_select(bud.cid), bud.bid)
   html += """
</table>
<p>
<strong>Note</strong>&nbsp;: La suppression d'un budget non-vide provoquera sa disparition
de l'&eacute;cran principal mais restera en base de donn&eacute;es.
</p>
</div>
"""
  return html

 def show_empty_budget(self):
  html = ''
  html += """
<div class="box">
<h2>Ajouter un nouveau budget dans "%s"</h2>
<table>
<tr><th>Nom</th><th>Montant cible</th><th>Commentaire</th><th></th></tr>
<tr>
<form>
<input type="hidden" name="cid" value="%d"/>
<td>
<input type="text" name="newbnom" value=""/>
</td>
<td>
<input type="text" name="bmontant" value=""/>
</td>
<td>
<input type="text" name="bcomment" value=""/>
</td>
<td><input type="image" src="../images/valid.png" style="border: 0"/></td>
</form>
</tr>
</table>
</div>
""" % (self.cat.cnom, self.cat.cid)
  return html

 def get_cat_select(self, cid):
  html = ''
  for cat in self.cats:
   if cat.cid == cid:
    html += '<option selected="selected" value="%d">---</option>' \
     % (cat.cid)
   else:
    html += '<option value="%d">%s</option>' % (cat.cid, cat.cnom)
  return html

class Help(HTML):
 def get_body(self):
  html = ''
  html += self.show_headers()
  html += """
<h2>La gestion de compte personnel selon CamBank</h2>
<p>
<ul>
<li>Toutes les entr&eacute;es d'argent servent &agrave; alimenter des budgets.</li>
<li>Chaque sortie d'argent provoque la diminution du budget concern&eacute;.</li>
</ul>
<strong>Exemple</strong> : Chaque mois, je re&ccedil;ois mon salaire et j'alloue tant d'argent pour faire mes courses, tant d'argent pour payer le loyer, tant d'argent de c&ocirc;t&eacute; pour payer les impots en septembre, tant d'argent pour une future voiture, etc. Chaque fois que je paye, que ce soit par carte ou en liquide, la somme est retir&eacute;e au budget en question.
</p>

<p>
L'int&eacute;r&ecirc;t est de VISUALISER les d&eacute;penses.
</p>

<h2>Pour commencer</h2>

<p>
La premi&egrave;re chose &agrave; faire est de cr&eacute;er les budgets. Ils doivent forc&eacute;ment appartenir &agrave; une cat&eacute;gorie (qui ne sert qu'&agrave; organiser).
</p>

<p>
Exemple de cat&eacute;gories:
<ul>
<li>Obligatoire <em>(contiendrait les sommes qui partent tous les mois : EDF, Internet, loyer, remboursement cr&eacute;dit immobilier...)</em></li>
<li>Pr&eacute;visionnel <em>(contiendrait les diff&eacute;rentes sommes &agrave; payer annuellement : impot, assurances...)</em></li>
<li>Fonctionnement <em>(contiendrait les budgets 'Nourriture', 'Habits', 'Sorties'...)</em></li>
</ul>
Ensuite, il faut cr&eacute;er tous les budgets n&eacute;cessaires &agrave; l'organisation de son argent.
</p>

<p>
Chaque budget poss&egrave;de :
<ul>
<li>un <strong>nom</strong> qui permet de l'identifier</li>
<li>une <strong>cat&eacute;gorie</strong> qui permet de l'organiser</li>
<li>un <strong>montant cible</strong> qui permet de visualiser si le budget est plut&ocirc;t plein ou plut&ocirc;t vide <em>(exemple: le budget 'Loyer' fera la taille de mon loyer, il faut le remplir tous les mois de la m&ecirc;me somme. le budget 'impot sur le revenu' fera la taille de l'impot annuel, je peux le remplir tous les mois comme je veux, mais il doit etre rempli pour septembre !)</em></li>
<li>un <strong>commentaire</strong> qui permet de mettre des explications <em>(pour le budget 'impot sur le revenu' je mettrais en commentaire combien il faut placer de c&ocirc;t&eacute; chaque mois)</em></li>
</ul>
</p>

<p>
Toutes ces informations peuvent &ecirc;tre modifi&eacute;es plus tard.
</p>

<p>
&Agrave; propos du <strong>montant cible</strong> : c'est purement indicatif. Un budget peut d&eacute;passer son montant sans probl&egrave;me. Il peut m&ecirc;me &ecirc;tre n&eacute;gatif <em>(oups, j'avais pas pr&eacute;vu assez pour sortir ce mois-ci ! je rattraperai le mois prochain...)</em>
</p>

<p>
Il peut &ecirc;tre int&eacute;ressant d'avoir un budget "argent de c&ocirc;t&eacute;" dans lequel puiser en cas d'impr&eacute;vu, pourquoi pas.
</p>

<h2>La premi&egrave;re op&eacute;ration</h2>

<p>
Je suppose que votre compte bancaire n'est pas vide au moment o&ugrave; vous commencez &agrave; utiliser CamBank.
</p>

<p>
Admettons que vous disposiez de 1234 Euros sur votre compte. Cr&eacute;ez une <em>op&eacute;ration manuelle</em> de 1234 euros avec comme <strong>D&eacute;tails</strong> : "&nbsp;initialisation du compte&nbsp;" par exemple.
</p>

<h2>Affecter une op&eacute;ration &agrave; un budget</h2>

<p>
Les op&eacute;rations non affect&eacute;es apparaissent dans un tableau en haut de la page avant la liste des budgets.
</p>

<p>
Pour chaque op&eacute;ration, il suffit de :
<ul>
<li>choisir un budget</li>
<li>&eacute;ventuellement modifier le montant <em>(pour decouper la somme sur plusieurs budgets)</em></li>
<li>valider</li>
</ul>

<p>
Les entr&eacute;es d'argent comme celle que nous venons de cr&eacute;er et comme les salaires vont forc&eacute;ment &ecirc;tre r&eacute;parties dans diff&eacute;rents budgets. Choisissez un montant &agrave; affecter avant de valider.
</p>

<p>
<strong>Exemple</strong> : 600 euros pour le budget 'loyer', 200 euros pour 'nourriture', etc.
</p>

<p>
Lorsqu'il n'y a plus rien &agrave; allouer, l'op&eacute;ration disparait.
</p>

<h2>Importer son relev&eacute; bancaire</h2>

<p>
Ensuite, t&eacute;l&eacute;chargez sur le site de votre banque un relev&eacute; du compte au format QIF (Money de pr&eacute;f&eacute;rence). On peut ensuite envoyer ce fichier &agrave; CamBank dans la partie "Importer des &eacute;critures".
</p>

<p>
Toutes les op&eacute;rations apparaissent alors, il faut leur allouer un budget :)
</p>

<p>
Personnellement, j'essaie de le faire tous les jours puisque ma banque me permet de prendre un relev&eacute; &agrave; partir de la veille.
</p>

<h2>Historique</h2>

<p>
Chaque budget garde en m&eacute;moire la totalit&eacute; des sommes qui lui ont &eacute;t&eacute; allou&eacute;es ou retir&eacute;es (cliquez sur le nom du budget).
</p>

<h2>L'argent liquide</h2>

<p>
Les op&eacute;rations par ch&egrave;que, carte bleue, pr&eacute;l&egrave;vement ou encore virement bancaire sont automatiquement import&eacute;es depuis le compte bancaire. Mais pour les op&eacute;rations liquides, il y a un peu plus de travail.
</p>

<h3>Les sorties d'argent liquide</h3>

<p>
Lorsque je retire de l'argent au distributeur, l'op&eacute;ration bancaire de retrait apparait dans CamBank mais une seule fois (exemple : j'ai retir&eacute; 100 euros). Lorsque je d&eacute;pense cet argent, je dois affecter une partie de cette op&eacute;ration dans les bons budgets. Ainsi, tant que je n'ai pas d&eacute;pens&eacute; tout mon argent liquide, l'op&eacute;ration de retrait reste dans la liste des op&eacute;rations non affect&eacute;es.
</p>

<h3>Les entr&eacute;es d'argent liquide</h3>

<p>
Il faut les rajouter &agrave; la main gr&acirc;ce au petit formulaire en bas de la page d'accueil.
</p>

<p>
<strong>Exemple</strong> : Je re&ccedil;ois 1000 euros en liquide, je cr&eacute;e donc une op&eacute;ration manuelle de 1000 euros, avec la date et un petit texte pour savoir d'o&ugrave; &ccedil;a vient. Je peux ensuite allouer cet argent &agrave; mes budgets.
</p>

"""
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

class Upload(UploadImport):
 """
 Upload est utilise lorsqu'un fichier est envoye par le formulaire.
 """
 def __init__(self, cb, file):
  UploadImport.__init__(self, cb)
  self.file = file

class Import(UploadImport):
 """
 Import est utilise pour valider les ecritures a inserer dans la base.
 """
 def __init__(self, cb, oids):
  UploadImport.__init__(self, cb)
  self.oids = oids


class ManageSalary(HTML):
 """
 Permet de definir la liste des actions a affecter au salaire mensuel
 """
 def __init__(self, cb):
  HTML.__init__(self, cb)
  self.cb = cb

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.show_manage_salary()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def show_manage_salary(self):
  blist = "<select name=\"bid\">\n"
  for bud in self.cb.get_budgets():
   if bud.bshow is False:
    continue
   blist += "<option value=\"%d\">%s</option>\n" % \
    (bud.bid, bud.bnom)
  blist += "</select>\n"

  sallist = ''
  saltotal = 0
  for sal in self.cb.get_salary():
   sallist += "<tr><td>%d</td><td>%s</td><td>" % (sal[2]/100, Budget(self.cb, sal[1]).bnom)
   sallist += "<a href=\"index.cgi?salary=1&amp;mid=%d\"><img src=\"../images/delete.png\"" % (sal[0])
   sallist += " title=\"Supprimer cette mensualite\"/></a></td></tr>"
   saltotal += sal[2]

  html = ''
  html += """
<div class="box">
<h2>Ajouter une mensualite</h2>
<form>
<input type="hidden" name="salary" value="1"/>
<table>
<tr><th align="right">Budget :</th><td>%s</td></tr>
<tr><th align="right">Montant :</th><td><input type="text" name="montant"/></td></tr>
<tr><th></th><td><input type="image" src="../images/valid.png" style="border: 0"/></td></tr>
</table>
</form>
</div>
""" % (blist)

  if sallist:
   html += """
<div class="box">
<h2>Gerer les mensualites (%d EUR)</h2>
<table>
<tr><th>Montant</th><th>Budget</th><th>Supprimer</th></tr>
""" % (saltotal/100)
   html += sallist
   html += """
</table>
</div>
"""

  return html

class OperationDetails(HTML):
 """
 Permet de visualiser les differentes actions (et donc budgets) liees a une operation.
 """

 def __init__(self, cb, oid):
  HTML.__init__(self, cb)
  self.op = Operation(cb, oid)
  self.cb = cb

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.show_operation_details()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def show_operation_details(self):
  html = ''
  html += """
<div class="box">
<h2>D&eacute;tails de l'op&eacute;ration %d</h2>
<table>
<tr><th>Date</th><td>%s</td></tr>
<tr><th>Montant</th><td>%.2f</td></tr>
<tr><th>Allou&eacute;</th><td>%.2f</td></tr>
<tr><th>Libell&eacute;</th><td>%s</td></tr>
<tr><th>D&eacute;tails</th><td>%s</td></tr>
</table>
<p>
Liste des affectations a un budget&nbsp;:
</p>
<table>
<tr><th>Date action</th><th>Budget</th><th>Montant</th></tr>
""" % (self.op.oid, strftime('%x', self.op.odate), float(self.op.omontant)/100, float(self.op.obalance)/100, self.op.olibelle, self.op.odetail)

  buds = {}
  for action in self.op.get_actions():
   if not action.bid in buds:
    try:
     buds[action.bid] = Budget(self.cb, action.bid)
    except:
     html += """
<tr><td>%s</td><td><a href="index.cgi?histobid=%d">%s</a></td><td>%.2f</td></tr>
""" % (strftime('Le %x &agrave; %X', action.adate), action.bid, 'epargne', float(action.amontant)/100)
     continue
   html += """
<tr><td>%s</td><td><a href="index.cgi?histobid=%d">%s</a></td><td>%.2f</td></tr>
""" % (strftime('Le %x &agrave; %X', action.adate), action.bid, buds[action.bid].bnom, float(action.amontant)/100)

  html += """
</table>
</div>
"""
  return html

class Preferences(HTML):
 def __init__(self, cb):
  self.cb = cb
  HTML.__init__(self, cb)

 def show_password_box(self):
  return '''
<h2>
Chiffrage des données et mot de passe CamBank
</h2>

<ul>
<li>
Toutes vos données textuelles peuvent être chiffrées avec votre mot de passe
que vous seul connaissez.
</li>
<li>
Les nombres ne sont pas chiffrés. Ceci afin de pouvoir faire des calculs sans
devoir tout décoder à chaque fois.
</li>
<li>
Un piratage de la base de données obtiendrait ainsi une liste d'enregistrements
incompréhensibles avec de vraies valeurs qui seront quasiment impossibles à
utiliser.
</li>
<li>
Cette page permet d'activer ou de désactiver le chiffrement. La clef de
chiffrement est votre mot de passe CamBank.
</li>
<li>
Changer le mot de passe implique un recodage complet de toutes vos données et
peut prendre plusieurs secondes de calcul.
</li>
<li>
En cas d'échec de la procédure, la transaction complète sera annulée et le mot de passe ne sera pas changé.
</li>
<li>
Il n'y a <strong>pas de possibilité de récupérer les données chiffrées si vous perdez le mot de passe</strong>.
</li>
</ul>

<div class="box">
<table>
<form>
<input type="hidden" name="setpass" value="1"/>
<tr>
<th>
<label for="crypt">Chiffrement</label>
</th>
<td>
<input type="radio" name="crypt" value="n" {}>non</input><br/>
<input type="radio" name="crypt" value="y" {}>oui</input>
</td>
</tr>
<tr>
<th>
<label for="curpass">Mot de passe actuel</label>
</th>
<td>
<input type="text" name="curpass" />
</td>
</tr>
<tr>
<th>
<label for="newpass">Nouveau mot de passe</label>
</th>
<td>
<input type="text" name="newpass"/>
</td>
</tr>
<tr>
<th>
Procéder à la modification
</th>
<td>
<input type="submit" value="Go"/>
</td>
</tr>
</form>
</table>
</div>
'''.format(self.cb.sympass is None and 'checked="checked"' or ' ', self.cb.sympass is None and ' ' or 'checked="checked"')

 def get_body(self):
  return \
     self.show_headers() \
   + self.show_password_box() \
   + self.show_retour_accueil() \
   + self.show_footers()

class Epargne(HTML):
 def __init__(self, cb):
  self.cb = cb
  HTML.__init__(self, cb)

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.help_epargne()
  html += self.list_epargnes()
  html += self.add_epargne_box()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def add_epargne_box(self):
  html = """
<div class="box">
<h2>Créer une épargne</h2>
<form>
<input type="hidden" name="epargne" value="1"/>
<table>
<tr>
<th>
Nom de l'épargne :
</th>
<td>
<input type="text" name="nom"/>
</td>
</tr>
<tr>
<th>
Ordre d'allocation :
</th>
<td>
<input type="text" name="order"/>
</td>
</tr>
<tr>
<th>
Minimum annuel à épargner :
</th>
<td>
<input type="text" name="min"/>
</td>
</tr>
<tr>
<th>
Répartition du surplus :
</th>
<td>
<input type="text" name="suppl"/>
</td>
</tr>
<tr>
<th>
Montant maximum de l'épargne :
</th>
<td>
<input type="text" name="max"/>
</td>
</tr>
<tr>
<th>
</th>
<td>
<input type="image" src="../images/valid.png" style="border: 0"/>
</td>
</tr>
</table>
</form>
</div>

"""
  return html

 def help_epargne(self):
  return """
<h3>
Fonctionnement des épargnes
</h3>
<p>
Une fonction permet d'allouer des revenus à l'épargne, soit
«&nbsp;épargner&nbsp;». La fonction d'épargne allouera automatiquement l'argent
en fonction des montants que vous avez saisis dans les cases suivantes. Voici
l'algorithme :
</p>
<ol>
<li>
En début d'année, remise à zéro des jauges des épargnes.
</li>
<li>
Alloue l'argent à chaque épargne, dans l'ordre, jusqu'à ce que la jauge atteigne
la somme «&nbsp;Minimum annuel&nbsp;» et passe au suivant.
</li>
<li>
Une fois que toutes les jauges ont atteint leur minimum annuel, l'argent à
épargner est distribué dans toutes les épargnes dont le montant total n'a pas
dépassé le «&nbsp;Montant maximum&nbsp;». Un pourcentage est calculé en
fonction de la valeur renseignée dans «&nbsp;Surplus annuel&nbsp;» et l'argent
est distribué en fonction.
</li>
</ol>
<p>
Hormis cette fonctionnalité, une épargne fonctionne comme un budget : une
opération peut y attribuer de l'argent et en retirer.
</p>
"""

 def list_epargnes(self):
  html = ""

  if len(self.cb.get_epargnes()) > 0:
   html += """
<div class="box">
<h2>Gérer les épargnes</h2>
<table>
<tr>
<th>Nom</th>
<th>Minimum annuel<br/>à allouer à l'épargne</th>
<th>Répartition<br/>du surplus</th>
<th>Montant maximum<br/>de l'épargne</th>
<th>Balance<br/>(montant total alloué)</th>
<th>Jauge<br/>(montant alloué cette année)</th>
<th>Modifier</th>
<th>Cacher</th>
</tr>
"""
   for ep in self.cb.get_epargnes():
    if ep.eshow is False:
     continue
    html += """
<tr>
<td align="center">%d. %s</td>
<td align="center">%d</td>
<td align="center">%d</td>
<td align="center">%d</td>
<td align="right">%.2f</td>
<td align="right">%.2f</td>
<td align="center"><a href="index.cgi?editeid=%d"><img src="../images/modify.png" title="Modifier cette épargne"/></a></td>
<td align="center"><a href="index.cgi?hideeid=%d"><img src="../images/delete.png" title="Cacher cette épargne"/></a></td>
</tr>
""" % (ep.eorder or 0, ep.ecomment is not None and ep.ename or ep.ename+' ('+ep.ecomment+')',
     ep.emin_jauge/100, ep.esuppl_jauge/100, ep.emax_balance/100, ep.ebalance/100.0, ep.ejauge/100.0, ep.eid, ep.eid)
   html += """
</table>
</div>
"""

  return html


class EditEpargne(Epargne):
 def __init__(self, cb, eid):
  self.cb = cb
  Epargne.__init__(self, cb)
  self.epargne = self.cb.get_epargne(eid)

 def get_body(self):
  html = ''
  html += self.show_headers()
  html += self.help_epargne()
  html += self.edit_epargne_box()
  html += self.show_retour_accueil()
  html += self.show_footers()
  return html

 def edit_epargne_box(self):
  html = """
<div class="box">
<h2>Modifer l'épargne : %s</h2>
<form>
<input type="hidden" name="seteid" value="%d"/>
<table>
<tr>
<th>
Ordre d'allocation :
</th>
<td>
<input type="text" name="order" value="%d"/>
</td>
</tr>
<tr>
<th>
Nom de l'épargne :
</th>
<td>
<input type="text" name="nom" value="%s"/>
</td>
</tr>
<tr>
<th>
Minimum annuel à épargner :
</th>
<td>
<input type="text" name="min" value="%d"/>
</td>
</tr>
<tr>
<th>
Répartition du surplus :
</th>
<td>
<input type="text" name="suppl" value="%d"/>
</td>
</tr>
<tr>
<th>
Montant maximum de l'épargne :
</th>
<td>
<input type="text" name="max" value="%d"/>
</td>
</tr>
<tr>
<th>
</th>
<td>
<input type="image" src="../images/valid.png" style="border: 0"/>
</td>
</tr>
</table>
</form>
</div>

""" % (self.epargne.ename, self.epargne.eid, self.epargne.eorder or 0, self.epargne.ename, self.epargne.emin_jauge/100, self.epargne.esuppl_jauge/100, self.epargne.emax_balance/100)
  return html
