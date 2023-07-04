from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from datetime import date
from django.db.models import Q
from django.forms import inlineformset_factory
from django.forms import modelform_factory
from datetime import date
from django.forms import ModelForm
from django import forms
from .filters import *
import io 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm,mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, TableStyle, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import time
from django.templatetags.static import static
from django.core.mail import send_mail
from django.conf import settings
#dd





def loginpage(request):
  if request.user.is_authenticated:
    return redirect('main')
  else:
    if request.method == "POST":
      username = request.POST.get('username')
      password = request.POST.get('password')

      user = authenticate(request, username=username, password=password)

      if user is not None:
        login(request, user)
        return redirect('main')
      else:
        messages.info(request, 'Username or Password incorrect!')
        render(request, 'Auftraege/login.html')
    context={}
    return render(request, 'Auftraege/login.html', context)
  
@login_required(login_url='login')
def main(request):
  akt_auf = Auftrag.objects.filter(auftrag_abgeschlossen = False).order_by('-auftragsnummer_ID')
  context = {'akt_auf':akt_auf}
  return render(request, 'Auftraege/main.html', context)

def logoutuser(request):
  logout(request)
  return redirect('login')

def calc_auftragsnummer():
  try:
    auftragsnummer = Auftrag.objects.latest('auftragsnummer_ID')
  except Auftrag.DoesNotExist:
    auftragsnummer = None

  if auftragsnummer==None:
    new_auftragsnummer = "A000001"
    return new_auftragsnummer
  else:
    auftragsnummer = Auftrag.objects.latest('auftragsnummer_ID')
    str_auftragsnummer = str(auftragsnummer).replace("A","")
    new_auftragsnummer = "A" + f"{int(str_auftragsnummer)+1:06d}"
    return new_auftragsnummer
  
def calc_rechnungsnummer():
  try:
    rechnungsnummer = Rechnung.objects.latest('rechnungsnummer')
  except Rechnung.DoesNotExist:
    rechnungsnummer = None

  if rechnungsnummer==None:
    new_rechnungsnummer = "RG00001"
    return new_rechnungsnummer
  else:
    rechnungsnummer = Rechnung.objects.latest('rechnungsnummer')
    str_rechnungsnummer = str(rechnungsnummer).replace("RG","")
    new_rechnungsnummer = "RG" + f"{int(str_rechnungsnummer)+1:05d}"
    return new_rechnungsnummer

@login_required(login_url='login')
def ua10na(request):
  auftrag = calc_auftragsnummer()
  form = UA10NAForm(initial={'auftragsnummer_ID':calc_auftragsnummer(), 'auftraggeber':request.user.get_full_name(),'auftragsdatum':date.today(),'ausgeführt_bis':date.today()})
  if request.method == "POST":
    form = UA10NAForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect("/UA10NAPos/"+auftrag)
  context={'form':form}
  return render(request, 'Auftraege/UA10NA.html',context)

@login_required(login_url='login')
def ua10naedit(request,pk):
  auftrag = Auftrag.objects.get(auftragsnummer_ID=pk)
  form = UA10NAForm(request.POST or None, instance=auftrag)
  context={'auftrag':auftrag,'form':form}
  if form.is_valid():
    form.save()
    return redirect("/")
  return render(request, 'Auftraege/UA10NA.html',context)

@login_required(login_url='login')
def ua10na_pos(request,pk):
  position = inlineformset_factory(Auftrag,Auftragspositionen,fields=['id','von','nach','referenz','kostenstelle'],extra=12,widgets={'id':forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),'von':forms.Select(attrs={'class':'form-select'}),'nach':forms.Select(attrs={'class':'form-select'}),'kostenstelle':forms.TextInput(attrs={'class':'form-control'}),'referenz':forms.Textarea(attrs={'class':'form-control','rows':1})})
  auftrag = Auftrag.objects.get(auftragsnummer_ID=pk)
  formset = position(instance=auftrag)
  if request.method == "POST":
    formset = position(request.POST, instance=auftrag)
    if formset.is_valid():
      formset.save()
      send_mail(
        "Neuer Auftrag " + pk + " , Auftragsfirma:" +auftrag.auftragsfirma.firma,
        "Es ist ein neuer Auftrag zu erledigen.",
        'settings.EMAIL_HOST_USER',
        ['janni24616@gmail.com'],
        fail_silently=False)
      return redirect("/main")
  context={'formset':formset}
  return render(request,'Auftraege/UA10NAPos.html',context)
  

@login_required(login_url='login')
def ua11aa(request):
  all_auf = Auftrag.objects.order_by('-auftragsnummer_ID')
  context = {'all_auf':all_auf}
  return render(request, 'Auftraege/UA11AA.html', context)

@login_required(login_url='login')
def ua12as(request):
  all_pos = Auftragspositionen.objects.order_by('-auftragsnummer')
  myFilter1 = SearchPosition(request.GET,queryset=all_pos)
  all_pos = myFilter1.qs
  context = {'all_pos':all_pos, 'myFilter1':myFilter1}
  return render(request, 'Auftraege/UA12AS.html', context)

@login_required(login_url='login')
def ua20nr(request):
  form = UA20NRForm(initial={'rechnungsnummer':calc_rechnungsnummer(),'rechnungsdatum':date.today(),'rechnungstext':'Bitte überweisen Sie den ausstehenden Betrag innerhalb von 7 Tagen auf das unten genannte Konto.'})
  if request.method == "POST":
    form = UA20NRForm(request.POST)
    if form.is_valid():
      form.save()
      field = form.cleaned_data['auftragsnummer']
      a = Auftrag.objects.filter(auftragsnummer_ID=field).update(auftrag_abgeschlossen=True)
      return redirect("/")
  context={'form':form}
  return render(request,"Auftraege/UA20NR.html",context)

@login_required(login_url='login')
def ua21ra(request):
  all_rg = Rechnung.objects.order_by('-rechnungsnummer')
  all_pos = Auftragspositionen.objects.all()
  context = {'all_rg':all_rg, 'all_pos':all_pos}
  return render(request, 'Auftraege/UA21RA.html', context)

@login_required(login_url='login')
def position(request,pk):
  position = Auftragspositionen.objects.get(id=pk)
  form = Position(request.POST or None, instance=position)
  if form.is_valid():
    form.save()
    return redirect("/")
  context = {'position':position,'form': form}
  return render(request,"Auftraege/Position.html",context)


def help(request):
  hilfe = Help.objects.all()
  context = {'hilfe': hilfe}
  return render(request,'Auftraege/help.html',context)




@login_required(login_url='login')
def invoice(request,pk):
  a = Auftrag.objects.get(auftragsnummer_ID = pk)
  pos = Auftragspositionen.objects.filter(auftragsnummer=pk)
  rg = Rechnung.objects.get(auftragsnummer=pk)

  def pagenumber(canvas,doc):
    pagenum = canvas.getPageNumber()
    text = "Seite %s von %s" % (pagenum,doc.page)
    canvas.drawRightString(20*cm,2*cm,text)

  def generate_pdf(request):
      response = HttpResponse(content_type='application/pdf')
      response['Content-Disposition'] = 'filename="AP_Rechnung"' + rg.rechnungsnummer + "_" + str(rg.rechnungsdatum) + ".pdf"

      doc = SimpleDocTemplate(response, pagesize=A4,rightMargin=2*cm, leftMargin=2*cm, topMargin=1*cm, bottomMargin=2.5*cm, title="Rechnung")
      Title = 'Test'
      elements = []
      data = [['Pos', 'Beschreibung','Anzahl', 'Preis [€]', 'MwSt. [%]', 'Total [€]','Referenz']]
      invoice_data = []
      total_price = 0
      mw=0
      styles1 = getSampleStyleSheet()
      style1 = styles1["Normal"]
      style1.fontSize = 10
      style1.alignment = 1
      styles3 = getSampleStyleSheet()
      style3 = styles1["Normal"]
      style3.fontSize = 8
      style3.alignment = 1
      #Creating data for table


    
      for i in range(len(pos.values('id'))):
        v = Adressen.objects.get(id = pos.values('von')[i]['von'])
        n = Adressen.objects.get(id = pos.values('nach')[i]['nach'])
        #
        invoice_data += [{'pos': i+1, \
                          'beschreibung': 'Transport mit ' + pos.values('fahrzeuge')[i]['fahrzeuge'] + '\n' + '(Wartezeit: ' + str(pos.values('wartezeit')[i]['wartezeit']) + 'min' + ' , Fixpreis: ' + '{0:.{1}f}'.format(round(pos.values('pauschale')[i]['pauschale'],2), 2) + '€)\n' + 'Von: ' + v.firma + '\n' + 'Nach: ' + n.firma + '\n' + 'Kostenstelle: ' + pos.values('kostenstelle')[i]['kostenstelle'], \
                          'anzahl': pos.values('anzahl')[i]['anzahl'], \
                          'preis': '{0:.{1}f}'.format(float(round(pos.values('einzelpreis')[i]['einzelpreis'],2)), 2), \
                          'mwst': '{0:.{1}f}'.format(round(pos.values('mwst')[i]['mwst'],2),2), \
                          'total':'{0:.{1}f}'.format(round(pos.values('anzahl')[i]['anzahl']*pos.values('einzelpreis')[i]['einzelpreis']+pos.values('anzahl')[i]['anzahl']*pos.values('einzelpreis')[i]['einzelpreis']/100*pos.values('mwst')[i]['mwst']+pos.values('pauschale')[i]['pauschale']+pos.values('pauschale')[i]['pauschale']/100*pos.values('mwst')[i]['mwst'],2),2) , \
                          'referenz':pos.values('referenz')[i]['referenz'] \
                         }]
        mw += float(invoice_data[i]['total'])-float(round(pos.values('einzelpreis')[i]['einzelpreis'],2))*float(pos.values('anzahl')[i]['anzahl'])-pos.values('pauschale')[i]['pauschale']
        total_price += float(invoice_data[i]['total'])
        #mw = mw + round(float(invoice_data[i]['preis'])*float(invoice_data[i]['anzahl'])/100*float(invoice_data[i]['mwst']),2)
        
      for item in invoice_data:
          data.append([item['pos'], item['beschreibung'],int(item['anzahl']), item['preis'], item['mwst'], item['total'],Paragraph(item['referenz'],style1)])

      #Build the table 
      t=Table(data,colWidths=[0.8*cm,6.5*cm,1.1*cm,2.4*cm,1.8*cm,2*cm,3*cm])
      t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                            ('TEXTCOLOR',(0,0),(-1,0),colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('ALIGN',(1,1),(1,-1),'LEFT'),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                            ('FONTSIZE',(0,0),(-1,-1),8),
                            ('BOTTOMPADDING',(0,0),(-1,0),0),
                            ('BACKGROUND',(0,1),(-1,-1),colors.beige),
                            ('GRID',(0,0),(-1,-1),1,colors.black)]))
      

      rtext = Paragraph(rg.rechnungstext)
      im = Image('/var/task/staticfiles_build/static/LogoAP.jpg',4*cm,2*cm,hAlign='RIGHT')
      def myFirstPage(canvas, doc):
        #Draws the invoice header
        canvas.setStrokeColorRGB(0.13, 0.25, 0.27)
        canvas.setFillColorRGB(0.2, 0.2, 0.2)
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(1.7 * cm, 19 * cm, 'Rechnung')
        canvas.setFont('Helvetica', 6)
        canvas.drawString(13.8*cm,21.4*cm,'*Bitte bei Schrift- und Zahlungsverkehr angeben*')
        canvas.setFont('Helvetica', 10)
        canvas.drawString(13.8*cm,21*cm,'Rechnungsnummer: ')
        canvas.drawString(13.8*cm,20.6*cm,'Rechnungsdatum: ')
        canvas.drawString(13.8*cm,20.2*cm,'Kundennummer: ')
        canvas.drawString(13.8*cm,19.8*cm,'Auftragsnummer: ')
        canvas.drawRightString(19.1*cm,21*cm, rg.rechnungsnummer)
        canvas.drawRightString(19.1*cm,20.6*cm, str(rg.rechnungsdatum))
        canvas.drawRightString(19.1*cm,20.2*cm,f"{int(a.auftragsfirma.id):04d}")
        canvas.drawRightString(19.1*cm,19.8*cm,a.auftragsnummer_ID)

        canvas.drawString(1.7*cm,23.7*cm,rg.empfänger.firma)
        canvas.drawString(1.7*cm,23.3*cm,rg.empfänger.adresse)
        canvas.drawString(1.7*cm,22.9*cm,str(rg.empfänger.plz)+ " " + rg.empfänger.ort)
        canvas.drawString(1.7*cm,22.5*cm,rg.empfänger.land)
        canvas.drawString(1.7*cm,22.1*cm,rg.empfänger.contact)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(1.7*cm,24.05*cm,'Ali Palabiyik * Jevenstedter Straße 175 * 22547 Hamburg')

        canvas.setFont('Helvetica', 10)
        canvas.drawString(1.7*cm,18*cm,'Sehr geehrte Damen und Herren,')
        canvas.drawString(1.7*cm,17.6*cm,'ich bedanke mich für Ihren Auftrag und erlaube mir, die folgenden Leistungen in Rechnung zu stellen.')

        canvas.setLineWidth(1)
        canvas.line(0*cm,1.6*cm,21.7*cm,1.6*cm)
        canvas.saveState()
        #pagenumber(canvas,doc)

        
        styles = getSampleStyleSheet()
        data = [['Ali Palabiyik Logistik Express','Tel.: 0176/7022 1652','Targo Bank'],
                ['Inh. Ali Palabiyik','E-Mail: Alipalabiyik1@outlook.de','IBAN: DE60300209005380642927'],
                ['Jevenstedterstraße 175','','Kto.-Inh.: Ali Palabiyik'],
                ['22547 Hamburg','','Steuer-Nr.:41/178/01662 FA Hamburg']]
        table = Table(data,colWidths=[6*cm,6*cm,6*cm], rowHeights=[0.3*cm,0.3*cm,0.3*cm,0.3*cm])
        table.hAlign = 'CENTER'
        table.setStyle([('ALIGN', (0, 0),(-1, -1), 'LEFT'),
                        ('FONTSIZE',(0,0),(-1,-1),6), 
                        ('VALIGN',(0,0),(-1,-1),'BOTTOM')])
        
        w, h = table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, doc.leftMargin+0.5*cm,h-1.2*cm)
        
      data2 = [['Gesamtpreis:','{0:.{1}f}'.format(total_price,2)+"€"],['inkl. MwSt:','{0:.{1}f}'.format(round(mw,2),2)+'€']]
      table2 = Table(data2)
      table2.hAlign = 'RIGHT'
      table2.setStyle([('ALIGN', (0, 0),(0, -1), 'LEFT'),
                       ('ALIGN', (0, 1),(1, -1), 'RIGHT'),
                       ('FONTNAME',(0,0),(1,0),'Helvetica-Bold'),
                      ('FONTSIZE',(0,0),(-1,-1),10), 
                      ('VALIGN',(0,0),(-1,-1),'MIDDLE')])
      
      def second(canvas,doc):
        styles4 = getSampleStyleSheet()
        style4 = styles4["Normal"]
        style4.fontSize = 10
        canvas.setLineWidth(1)
        canvas.line(0*cm,1.6*cm,21.7*cm,1.6*cm)
        canvas.saveState()
        data = [['Ali Palabiyik Logistik Express','Tel.: 0176/7022 1652','Targo Bank'],
                ['Inh. Ali Palabiyik','E-Mail: Alipalabiyik1@outlook.de','IBAN: DE60300209005380642927'],
                ['Jevenstedterstraße 175','','Kto.-Inh.: Ali Palabiyik'],
                ['22547 Hamburg','','Steuer-Nr.:41/178/01662 FA Hamburg']]
        table = Table(data,colWidths=[6*cm,6*cm,6*cm], rowHeights=[0.3*cm,0.3*cm,0.3*cm,0.3*cm])
        table.hAlign = 'CENTER'
        table.setStyle([('ALIGN', (0, 0),(-1, -1), 'LEFT'),
                        ('FONTSIZE',(0,0),(-1,-1),6), 
                        ('VALIGN',(0,0),(-1,-1),'BOTTOM')])
        
        w, h = table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, doc.leftMargin+0.5*cm,h-1.2*cm)
        canvas.setFont('Helvetica',10)
        #pagenumber(canvas,doc)
       
      elements.append(im)
      elements.append(Spacer(21.7*cm,9.3*cm))
      elements.append(t)
      elements.append(Spacer(21.7*cm,0.5*cm))
      elements.append(table2)
      elements.append(Spacer(21.7*cm,0.5*cm))
      elements.append(rtext)
      doc.build(elements,onFirstPage=myFirstPage,onLaterPages=second,canvasmaker=NumberedCanvas)

      return response
  return generate_pdf(request)


@login_required(login_url='login')
def pod(request,pk):
  a = Auftrag.objects.get(auftragsnummer_ID = pk)
  pos = Auftragspositionen.objects.filter(auftragsnummer=pk)
  #rg = Rechnung.objects.get(auftragsnummer=pk)
  


  def generate_pdf(request):
      response = HttpResponse(content_type='application/pdf')
      response['Content-Disposition'] = 'filename="AP_Abliefernachweis"' + a.auftragsnummer_ID + "_" + str(a.auftragsdatum) + ".pdf"

      doc = SimpleDocTemplate(response, pagesize=A4,rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=2.5*cm, title="Abliefernachweis")
      Title = 'Test'
      elements = []
      data = [['Pos', 'Beschreibung','Referenz', 'Empfänger', 'Ablieferdatum','Unterschrift']]
      pod_data = []
      styles1 = getSampleStyleSheet()
      style1 = styles1["Normal"]
      style1.fontSize = 6
      total_price = 0
      mw=0
      #Creating data for table
      for i in range(len(pos.values('id'))):
        v = Adressen.objects.get(id = pos.values('von')[i]['von'])
        n = Adressen.objects.get(id = pos.values('nach')[i]['nach'])
        pod_data += [{'pos': i+1, 'beschreibung': 'Transport' + '\n' + 'Von: ' + v.firma + '\n' + 'Nach: ' + n.firma,'referenz':pos.values('referenz')[i]['referenz'],'empfänger': pos.values('empfänger')[i]['empfänger'],'datum': pos.values('unterschrift_datum')[i]['unterschrift_datum'], 'unterschrift': pos.values('unterschrift')[i]['unterschrift']}]
      for item in pod_data:
          data.append([item['pos'], item['beschreibung'],Paragraph(item['referenz'],style1), Paragraph(item['empfänger'],style1), item['datum'],Image(item['unterschrift'],2*cm,1.2*cm,hAlign='RIGHT')])

      #Build the table 
      t=Table(data,colWidths=[0.8*cm,7*cm,4*cm,2.5*cm,2.3*cm,2.2*cm])
      t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                            ('TEXTCOLOR',(0,0),(-1,0),colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('ALIGN',(1,1),(1,-1),'LEFT'),
                            ('VALIGN',(0,0),(-1,-1),'TOP'),
                            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                            ('FONTSIZE',(0,0),(-1,0),6),
                            ('FONTSIZE',(0,1),(-1,-1),6),
                            ('BOTTOMPADDING',(0,0),(-1,0),0),
                            ('BACKGROUND',(0,1),(-1,-1),colors.white),
                            ('GRID',(0,0),(-1,-1),1,colors.black)]))
      
      im = Image('/var/task/staticfiles_build/static/LogoAP.jpg',4*cm,2*cm,hAlign='RIGHT')
      def myFirstPage(canvas, doc):
        #Draws the invoice header
        canvas.setStrokeColorRGB(0.13, 0.25, 0.27)
        canvas.setFillColorRGB(0.2, 0.2, 0.2)
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(1.2 * cm, 19 * cm, 'Abliefernachweis (Proof of delivery)')
        canvas.setFont('Helvetica', 6)
        canvas.drawString(13.8*cm,20.95*cm,'*Bitte bei Schriftverkehr angeben*')
        canvas.setFont('Helvetica', 10)
        canvas.drawString(13.8*cm,19.8*cm,'Auftragsnummer: ')
        canvas.drawString(13.8*cm,20.2*cm,'Kundennummer: ')
        canvas.drawString(13.8*cm,20.6*cm,'Auftragsdatum: ')
        canvas.drawRightString(19.1*cm,19.8*cm, a.auftragsnummer_ID)
        canvas.drawRightString(19.1*cm,20.2*cm,f"{int(a.auftragsfirma.id):04d}")
        canvas.drawRightString(19.1*cm,20.6*cm, str(a.auftragsdatum))
        canvas.drawString(1.7*cm,23.7*cm,a.auftragsfirma.firma)
        canvas.drawString(1.7*cm,23.3*cm,a.auftragsfirma.adresse)
        canvas.drawString(1.7*cm,22.9*cm,str(a.auftragsfirma.plz)+ " " + a.auftragsfirma.ort)
        canvas.drawString(1.7*cm,22.5*cm,a.auftragsfirma.land)
        canvas.drawString(1.7*cm,22.1*cm,a.auftragsfirma.contact)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(1.7*cm,24.05*cm,'Ali Palabiyik * Jevenstedter Straße 175 * 22547 Hamburg')

        canvas.setLineWidth(1)
        canvas.line(0*cm,1.6*cm,21.7*cm,1.6*cm)
        canvas.saveState()
        
        styles = getSampleStyleSheet()
        data = [['Ali Palabiyik Logistik Express','Tel.: 0176/7022 1652','Targo Bank'],
                ['Inh. Ali Palabiyik','E-Mail: Alipalabiyik1@outlook.de','IBAN: DE60300209005380642927'],
                ['Jevenstedterstraße 175','','Kto.-Inh.: Ali Palabiyik'],
                ['22547 Hamburg','','Steuer-Nr.:41/178/01662 FA Hamburg']]
        table = Table(data,colWidths=[7*cm,7*cm,7*cm], rowHeights=[0.3*cm,0.3*cm,0.3*cm,0.3*cm])
        table.hAlign = 'CENTER'
        table.setStyle([('ALIGN', (0, 0),(-1, -1), 'LEFT'),
                        ('FONTSIZE',(0,0),(-1,-1),6), 
                        ('VALIGN',(0,0),(-1,-1),'BOTTOM')])
        
        w, h = table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, doc.leftMargin+0.5*cm,h-1.2*cm)
        
      def second(canvas,doc):
        styles = getSampleStyleSheet()
        canvas.setLineWidth(1)
        canvas.line(0*cm,1.6*cm,21.7*cm,1.6*cm)
        canvas.saveState()
        data = [['Ali Palabiyik Logistik Express','Tel.: 0176/7022 1652','Targo Bank'],
                ['Inh. Ali Palabiyik','E-Mail: Alipalabiyik1@outlook.de','IBAN: DE60300209005380642927'],
                ['Jevenstedterstraße 175','','Kto.-Inh.: Ali Palabiyik'],
                ['22547 Hamburg','','Steuer-Nr.:41/178/01662 FA Hamburg']]
        table = Table(data,colWidths=[6*cm,6*cm,6*cm], rowHeights=[0.3*cm,0.3*cm,0.3*cm,0.3*cm])
        table.hAlign = 'CENTER'
        table.setStyle([('ALIGN', (0, 0),(-1, -1), 'LEFT'),
                        ('FONTSIZE',(0,0),(-1,-1),6), 
                        ('VALIGN',(0,0),(-1,-1),'BOTTOM')])
        
        w, h = table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, doc.leftMargin+0.5*cm,h-1.2*cm)
      par = Paragraph('Sehr geehrte Damen und Herren, <br /> folgende Auftragspositionen wurden von der Firma "Ali Palabiyik Express Logistik" ausgeführt. Die ausgezeichneten Unterschriften wurden elektronisch aufgezeichnet und gelten als Bestätigung der Ablieferung. Dieser Abliefernachweis wurde mittels EDV automatisch erstellt und besitzt auch ohne Unterschrift seine Gültigkeit.') 

      elements.append(im)
      elements.append(Spacer(21.7*cm,7.8*cm))
      elements.append(par)
      elements.append(Spacer(21.7*cm,0.5*cm))
      elements.append(t)
      elements.append(Spacer(21.7*cm,0.5*cm))
      doc.build(elements,onFirstPage=myFirstPage,onLaterPages=second,canvasmaker=NumberedCanvas)

      return response
  return generate_pdf(request)

class NumberedCanvas(canvas.Canvas):


    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.Canvas = canvas.Canvas
        self._saved_page_states = []
 

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
 

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont('Helvetica', 10)
            self.draw_page_number(num_pages)
            self.Canvas.showPage(self)
        self.Canvas.save(self)
 
 
    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(200 * mm, 20 * mm,
                             "Seite %d von %d" % (self._pageNumber, page_count))



