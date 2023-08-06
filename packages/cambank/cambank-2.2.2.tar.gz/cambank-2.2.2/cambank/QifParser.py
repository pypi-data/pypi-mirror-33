# coding=utf-8
from __future__ import print_function
import sys, datetime, re

class BankItem:
 def __init__(self):
  self.date = None
  self.amount = None
  self.cleared = None
  self.num = None
  self.payee = None
  self.memo = None
  self.address = None
  self.category = None
  self.categoryInSplit = None
  self.memoInSplit = None
  self.amountOfSplit = None
  self.checkNumber = None

 def getCamBankCSV(self):
  return "%s;%s;%s;%s;%s" % (self.date, self.payee or self.memo, self.memo or self.payee, self.amount, 'EUR')

class QifItem(BankItem):
 pass

def parseQif(infile):
 """
 Parse a qif file and return a list of entries.
 infile should be open file-like object (supporting readline() ).
 """

 inItem = False
 englishDateFormat = False

 items = []
 curItem = QifItem()

 content = infile.read()
 if 'decode' in dir(content):
  content = content.decode()
 for line in re.split('\n|\r|\n\r', content)[1:]:
  if line == '': # blank line
   pass
  elif line[0] == '^': # end of item
   # save the item
   items.append(curItem)
   curItem = QifItem()
  elif line[0] == 'D':
   curItem.date = line[1:]
   # try to detect english Date Format if month > 12 or if date is in the future
   (d, m, y) = curItem.date.split('/')
   if int(m) > 12 or datetime.date(int(y), int(m), int(d)) > datetime.date.today():
    englishDateFormat = True
   # correct YY to YYYY
   if int(y) < 2000:
    curItem.date = d+'/'+m+'/20'+y
  elif line[0] == 'T':
   curItem.amount = line[1:]
  elif line[0] == 'C':
   curItem.cleared = line[1:]
  elif line[0] == 'P':
   curItem.payee = line[1:]
  elif line[0] == 'N':
   curItem.checkNumber = line[1:]
  elif line[0] == 'M':
   curItem.memo = line[1:]
  elif line[0] == 'A':
   curItem.address = line[1:]
  elif line[0] == 'L':
   curItem.category = line[1:]
  elif line[0] == 'S':
   try:
    curItem.categoryInSplit.append(";" + line[1:])
   except AttributeError:
    curItem.categoryInSplit = line[1:]
  elif line[0] == 'E':
   try:
    curItem.memoInSplit.append(";" + line[1:])
   except AttributeError:
    curItem.memoInSplit = line[1:]
  elif line[0] == '$':
   try:
    curItem.amountInSplit.append(";" + line[1:])
   except AttributeError:
    curItem.amountInSplit = line[1:]
  else:
   # don't recognise this line; ignore it
   print("Skipping unknown line:\n{}".format(line), file=sys.stderr)

  line = infile.readline()
  if "decode" in dir(line):
   line = line.decode()

 # reverting to european dates if needed
 if englishDateFormat:
  ii = []
  for item in items:
   (m, d, y) = item.date.split('/')
   item.date = d+'/'+m+'/'+y
   ii.append(item)
  return ii
 return items





class OfxItem(BankItem):
 pass

def parseOfx(infile):
 """
 Parse an OFXv1 file and return a list of entries.
 infile should be open file-like object (supporting readline() ).
 """
 items = []
 from ofxtools import OFXTree
 tree = OFXTree()
 tree.parse(infile)
 response = tree.convert()
 for st in response.statements:
  for tr in st.transactions:
   curItem = OfxItem()
   curItem.date = tr.dtposted.strftime('%d/%m/%Y')
   curItem.amount = str(tr.trnamt)
   curItem.payee = tr.name
   curItem.memo = tr.memo
   # save the item
   items.append(curItem)
 return items



def parseEpaymentsCSV(infile):
 """
 parse a CSV file downloaded at epayments.com. returns the typical list of Bankitem
 """
 items = []
 content = infile.read()
 if 'decode' in dir(content):
  content = content.decode()
 for line in re.split('\n|\r|\n\r', content)[1:]:
  if line == '':
   continue
  row = line.split(';')
  curItem = BankItem()
  curItem.date = datetime.datetime.strptime(row[0].split(' ')[0], '%m/%d/%Y').strftime('%d/%m/%Y')
  curItem.amount = row[4]
  curItem.payee = 'CARTE ' + re.compile('  *').sub(' ', row[3].replace('\\', ' '))
  curItem.memo = curItem.payee
  items.append(curItem)
 return items


if __name__ == "__main__":
 # open and read arg1 and write CSV to stdout
 with open(sys.argv[1]) as f:
  items = parseEpaymentsCSV(f)
  #items = parseOfx(f)
  #print repr(items[0])
  for item in items:
   print(item.getCamBankCSV())
