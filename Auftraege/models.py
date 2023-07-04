from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models
from datetime import date
from django.contrib.auth.models import User
##### Consignee 
# Create your models here.


class Adressen(models.Model):
    id = models.AutoField(primary_key=True,unique=True,blank=False)
    firma = models.CharField(max_length=120, blank=False)
    adresse = models.CharField(max_length=200, blank=False)
    plz = models.CharField(max_length=20, blank=False)
    ort = models.CharField(max_length=100, blank=False)
    land = models.CharField(max_length=100, blank=False)
    contact = models.CharField(max_length=100, blank = True)
    phone = models.CharField(max_length=30, blank = True)
    additional = models.CharField(max_length=200, blank = True)
    date_added = models.DateTimeField(auto_now_add = True, blank = False)
    date_modified = models.DateTimeField(auto_now = True, blank = False)

    def __str__(self):
        return str(self.firma) + ", " + str(self.adresse)
    
class Rechnungsempfaenger(models.Model):
    id = models.AutoField(primary_key=True,unique=True,blank=False)
    firma = models.CharField(max_length=120, blank=False)
    adresse = models.CharField(max_length=200, blank=False)
    plz = models.CharField(max_length=20, blank=False)
    ort = models.CharField(max_length=100, blank=False)
    land = models.CharField(max_length=100, blank=False)
    contact = models.CharField(max_length=100, blank = True)
    phone = models.CharField(max_length=30, blank = True)
    additional = models.CharField(max_length=200, blank = True)
    date_added = models.DateTimeField(auto_now_add = True, blank = False)
    date_modified = models.DateTimeField(auto_now = True, blank = False)

    def __str__(self):
        return str(self.firma)
    

class Fahrer(models.Model):
    id = models.AutoField(primary_key=True,unique=True,blank=False)
    vorname = models.CharField(max_length=100,blank=False)
    nachname = models.CharField(max_length=100,blank=False)
    tel = models.CharField(max_length=25, blank=True)
    def __str__(self):
        return str(self.vorname)+" "+str(self.nachname)



        
class Auftrag(models.Model):
    auftragsnummer_ID = models.CharField(primary_key=True, unique=True, max_length=7, blank=True)
    auftraggeber = models.CharField(max_length=120, blank=False)
    auftragsdatum = models.DateField(blank=False, null=True)
    ausgeführt_bis = models.DateField(blank=False,null=True)
    auftragsfirma = models.ForeignKey(Adressen, on_delete=models.PROTECT, blank=False, null=True)
    auftragstext=models.TextField(blank=True,null=True)
    date_added = models.DateTimeField(auto_now_add = True, blank = False)
    date_modified = models.DateTimeField(auto_now = True, blank = False)
    fahrer = models.ForeignKey(Fahrer,blank=False, on_delete=models.PROTECT)
    angenommen = models.BooleanField(blank=True, null=True, default=False)
    auftrag_abgeschlossen = models.BooleanField(blank=True,null=True, default=False)
    def __str__(self):
        return self.auftragsnummer_ID
    

        
class Auftragspositionen(models.Model):
    BUS = "Bus"
    PKW = "Pkw"
    VEHICLE_CHOICES = ((BUS,"Bus"),(PKW,"Pkw"))


    auftragsnummer = models.ForeignKey(Auftrag,on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True,unique=True)
    von = models.ForeignKey(Adressen,null=True,blank=True,on_delete=models.PROTECT, related_name='von')
    nach = models.ForeignKey(Adressen, null=True,blank=True,on_delete=models.PROTECT, related_name='nach')
    kostenstelle = models.CharField(max_length=20,blank=True,null=True)
    referenz = models.TextField(blank=True,null=True)
    einzelpreis = models.FloatField(blank=True, null=True,default=0)
    mwst = models.IntegerField(blank=True,null=True,default=19)
    anzahl = models.FloatField(blank=True, null=True, default=1) 
    fahrzeuge = models.CharField(choices=VEHICLE_CHOICES,default=BUS,blank=True,null=True,max_length=10)
    pauschale = models.FloatField(blank=True, null=True,default=0)
    wartezeit = models.IntegerField(blank=True,null=True,default=0)
    position_abgeschlossen = models.BooleanField( blank=True,null=True)
    unterschrift = models.TextField(blank=True, null=True, default="-")
    unterschrift_datum = models.DateField(blank=True, null=True, auto_now_add = True)
    empfänger = models.CharField(max_length=120,blank=True, null=True,'-')
    date_added = models.DateTimeField(auto_now_add = True, blank = True, null=True)
    date_modified = models.DateTimeField(auto_now = True, blank = True, null=True)

    @property
    def gesamtpreis(self):
        gesamt = self.einzelpreis*self.anzahl
        return gesamt
    
    @property
    def total(self):
        tot = self.einzelpreis*self.anzahl + self.einzelpreis*self.anzahl/100*self.mwst
        return tot

    def __str__(self):
        return str(self.id)
    
class Rechnung(models.Model):
    auftragsnummer = models.ForeignKey(Auftrag,on_delete=models.PROTECT)
    empfänger = models.ForeignKey(Rechnungsempfaenger,on_delete=models.PROTECT, blank=False)
    rechnungsnummer = models.CharField(blank=False,max_length=7)
    rechnungsdatum = models.DateField(blank=False)
    rechnungstext = models.TextField(blank=True)
    rechnungspreis = models.FloatField(blank=True,null=True)
    date_added = models.DateTimeField(auto_now_add = True, blank = False)
    date_modified = models.DateTimeField(auto_now = True, blank = False)

    def __str__(self):
        return str(self.rechnungsnummer)


class Help(models.Model):
    frage = models.TextField(blank=False)
    antwort = models.TextField(blank=False)
    


