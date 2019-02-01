# Django auto-serializer
Django app that automates objects tree serialization recursively, without any declaration.

Define new classes for every Object serialization could sound a bit boring, I coded this way to do the things automagically. 
Django-auto-serializer will do for you:

- Json serialization (export);
- recursively serialize all FK childrens;
- can ignore some child if you tell him how they are called (see examples above);
- M2M auto serialization;
- ignore or not autofields import/export (auto_now_add, slugfields...);
- Import a serialized Object tree, it will build up everything as before;


## Usage Example
````
from gestione_peo.models import *

# get an object
bando = Bando.objects.first()

# object serialization
# A single object duplication
si = SerializableInstance(bando)

#si.serialize_obj()
st = si.serialize_tree()
# pprint(st)

# Serialized entire tree, main object with childrens
sit = SerializableInstanceTree(bando, excluded_fields=['created', 'modified'],
                               excluded_childrens = ['domandabando',
                                                     'modulodomandabando',
                                                     'abilitazionebandodipendente'],
                               auto_fields = False,
                               change_uniques = True,
                               duplicate = True)
sit.serialize_tree()
````

## Some coding hints
````
import pprint
# all the fields
bando._meta._forward_fields_map

# childrens here
bando._meta.fields_map
bando._meta.related_objects

# another way with NestedObjects
from django.contrib.admin.utils import NestedObjects
from django.db import DEFAULT_DB_ALIAS

# get json with pk and autofilled fields as they are
from django.core import serializers
serializers.serialize('json', [bando], ensure_ascii=False)

# serializers.serialize() relies on
model_to_dict(bando)

pprint(sit.dict)
for i in sit.dict['childrens']:
    if i['model_name'] == 'IndicatorePonderato':
        pprint(i)
        
tree_to_str = json.dumps(si.dict, indent=2)
jsonstr_to_dict = json.loads(tree_to_str)
pprint(jsonstr_to_dict )
````

## Import dump
````
isi = ImportableSerializedInstance(si.dict)
isi.save()
print(isi.json())
````

## A simple view to import a json dump
````
@user_passes_test(lambda u:u.is_staff)
def import_file(request):
    file_to_import = request.FILES.get('file_to_import')
    # content here
    url = reverse('admin:gestione_peo_bando_changelist')
    if not file_to_import:
        return HttpResponseRedirect(url)
    if not file_to_import:
        # scrivi un messaggio di errore
        pass
    jcont = json.loads(request.FILES['file_to_import'].read().decode(settings.DEFAULT_CHARSET))
    isi = ImportableSerializedInstance(jcont)
    isi.save()
    return HttpResponseRedirect(url)
````

## Django admin action to duplicate or export an entire tree
````
import io
import json

from django.apps import apps
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponse

from .models import *
from django_auto_serializer.auto_serializer import (SerializableInstance,
                                                    ImportableSerializedInstance)


def duplica_bando(modeladmin, request, queryset):
    for bando in queryset:
        try:
            si = SerializableInstance(bando)
            st = si.serialize_tree()
        except Exception as e:
            msg = '{} duplicazione fallita: {}'
            messages.add_message(request, messages.WARNING,
                                 msg.format(bando, e))
        try:
            isi = ImportableSerializedInstance(si.dict)
            isi.save()
        except Exception as e:
            msg = '{} duplicazione fallita: {}'
            messages.add_message(request, messages.WARNING,
                                 msg.format(bando, e))

        msg = '{} correttamente duplicato.'
        messages.add_message(request, messages.INFO,
                             msg.format(bando))
duplica_bando.short_description = "Duplica il Bando e la sua Configurazione"


def scarica_template_bando(modeladmin, request, queryset):
    iofile = io.StringIO()
    bandi_labels = []
    for bando in queryset:
        try:
            si = SerializableInstance(bando)
            st = si.serialize_tree()
            iofile.write(json.dumps(si.dict, indent=2))
        except Exception as e:
            msg = '{} duplicazione fallita: {}'
            messages.add_message(request, messages.WARNING,
                                 msg.format(bando, e))
        bandi_labels.append(bando.slug)
    file_name = 'peo_template_bando_{}.json'.format('_'.join(bandi_labels))
    iofile.seek(0)
    response = HttpResponse(iofile.read())
    response['content_type'] = 'application/force-download'
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    response['X-Sendfile'] = file_name
    return response
scarica_template_bando.short_description = "Scarica Template Bando"
````

## Result
````
{
  "m2m": [],
  "model_name": "Bando",
  "app_name": "gestione_peo",
  "childrens": [
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo": 30,
        "punteggio": 1,
        "titolo_id": 30
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_id": 20,
        "ordinamento": 1,
        "titolo": 20,
        "punteggio": 2
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_id": 19,
        "ordinamento": 2,
        "titolo": 19,
        "punteggio": 3
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_id": 18,
        "ordinamento": 3,
        "titolo": 18,
        "punteggio": 2
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "ClausoleBando",
      "childrens": [],
      "object": {
        "is_active": true,
        "titolo": "Modalit\u00e0 della presentazione dei titoli e veridicit\u00e0 delle dichiarazioni",
        "corpo_del_testo": "I titoli valutabili  di cui all'art. 7 del bando  dovranno essere dichiarati attraverso questa piattaforma ed avranno valore di dichiarazione sostitutiva di certificazione e di atto di notoriet\u00e0 di cui al DPR 28 dicembre 2000, n. 445. Qualora nella fase di controllo dovesse emergere la non veridicit\u00e0 del contenuto delle dichiarazioni, il dichiarante decade dai benefici conseguiti sulla basa della dichiarazione non veritiera, ferma restando l'attivazione di procedure disciplinari nonch\u00e9 l'applicazione delle disposizioni dell'art.  76 del suddetto DPR 445/2000, in merito alle sanzioni previste dal codice penale e dalle leggi speciali in materia."
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "ClausoleBando",
      "childrens": [],
      "object": {
        "ordinamento": 1,
        "is_active": true,
        "titolo": "Sanzioni disciplinari",
        "corpo_del_testo": "Il sottoscritto dichiara di non essere incorso, negli ultimi due anni, in sanzioni disciplinari pi\u00f9 gravi del rimprovero scritto."
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "ClausoleBando",
      "childrens": [],
      "object": {
        "ordinamento": 2,
        "is_active": true,
        "titolo": "Privacy",
        "corpo_del_testo": "Il sottoscritto esprime il proprio consenso affinch\u00e9 i dati personali forniti possano essere trattati, nel rispetto del Regolamento UE 2016/679, per gli adempimenti connessi alla presente selezione."
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "IndicatorePonderato",
      "childrens": [
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 2,
            "posizione_economica_id": 2,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 3,
            "posizione_economica_id": 3,
            "punteggio_max": 15
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 4,
            "posizione_economica_id": 4,
            "punteggio_max": 15
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 5,
            "posizione_economica_id": 5,
            "punteggio_max": 10
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "x",
                "durata_minima": 1,
                "durata_massima": 1000,
                "nome": "Punteggio per durata temporale",
                "unita_temporale": "m",
                "punteggio": 0.016666667
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Ente presso cui si \u00e8 svolto il servizio",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Data",
                "is_required": true,
                "ordinamento": 1,
                "tipo": "DateOutOfRangeComplexField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            }
          ],
          "object": {
            "id_code": "Da",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Il servizio deve riferirsi a lavoro dipendente",
            "nome": "Servizio prestato in maniera continuativa presso una P.A. compresi gli anni prestati come Servizio Militare e/o Civile"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "x",
                "durata_minima": 1,
                "durata_massima": 1000,
                "nome": "punteggio Consorzi Universitari",
                "unita_temporale": "m",
                "punteggio": 0.0083333333
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Consorzio Universitario presso cui si \u00e8 svolto il servizio",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Durata",
                "is_required": true,
                "ordinamento": 1,
                "tipo": "DateOutOfRangeComplexField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            }
          ],
          "object": {
            "id_code": "Db",
            "numero_inserimenti": 1,
            "nome": "Servizio prestato presso Consorzi Universitari",
            "calcolo_punteggio_automatico": true
          }
        }
      ],
      "object": {
        "id_code": "D",
        "add_punteggio_anzianita": true,
        "ordinamento": 3,
        "note": "A cura dell'Area Risorse Umane",
        "nome": "Anzianit\u00e0 di servizio prestato senza essere incorsi negli ultimi due anni in sanzioni disciplinari pi\u00f9 gravi del rimprovero scritto"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "IndicatorePonderato",
      "childrens": [
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 2,
            "posizione_economica_id": 2,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 3,
            "posizione_economica_id": 3,
            "punteggio_max": 25
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 4,
            "posizione_economica_id": 4,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 5,
            "posizione_economica_id": 5,
            "punteggio_max": 15
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Valutazione",
                "is_required": true,
                "tipo": "PunteggioFloatField",
                "aiuto": "inserire punteggio attribuito dal responsabile di struttura"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomFileField",
                "nome": "Scheda di arricchimento professionale"
              }
            }
          ],
          "object": {
            "id_code": "Ba",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "is_required": true,
            "note": "Inserire il punteggio riportato nella scheda di arricchimento professionale (Tabella 1 allegata al Bando di Selezione)",
            "nome": "Valutazione scheda"
          }
        }
      ],
      "object": {
        "id_code": "B",
        "ordinamento": 1,
        "nome": "Arricchimento professionale"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "IndicatorePonderato",
      "childrens": [
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 2,
            "posizione_economica_id": 2,
            "punteggio_max": 25
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 3,
            "posizione_economica_id": 3,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 4,
            "posizione_economica_id": 4,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 5,
            "posizione_economica_id": 5,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 13.0
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 10.0,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 10.0,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 10.0,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 1,
                "durata_massima": 4,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.15
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 5,
                "durata_massima": 8,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 9,
                "durata_massima": 16,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 17,
                "durata_massima": 10000,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.6
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Titolo Corso",
                "is_required": true,
                "tipo": "CustomCharField",
                "aiuto": "inserire il titolo del corso come riportato sull'attestato"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Ente Erogatore",
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "aiuto": "inserire il nome dell'ente erogatore"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Durata",
                "is_required": true,
                "ordinamento": 2,
                "tipo": "DateInRangeComplexField",
                "aiuto": "inserire data inizio e fine del corso di formazione nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Numero ore",
                "is_required": true,
                "ordinamento": 3,
                "tipo": "DurataComeInteroField",
                "aiuto": "durata complessiva del corso in ore"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 4,
                "tipo": "CustomCharField",
                "nome": "Valutazione"
              }
            }
          ],
          "object": {
            "id_code": "Aa",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Inserire solo i corsi di formazione che prevedono il superamento di un esame finale con relativa valutazione.\r\n\r\n- test1\r\n- test2\r\n- ciao\r\n\r\neppoi ciao.",
            "nome": "Corsi di formazione certificati con superamento di esame finale"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 12.0
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 10.0,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 10.0,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 10.0,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 1,
                "durata_massima": 4,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.1
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 5,
                "durata_massima": 8,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.2
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 9,
                "durata_massima": 16,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore_TimeDelta",
              "childrens": [],
              "object": {
                "operatore": "a",
                "durata_minima": 17,
                "durata_massima": 10000,
                "nome": "Durata corso (ore)",
                "unita_temporale": "h",
                "punteggio": 0.4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Titolo Corso",
                "is_required": true,
                "tipo": "CustomCharField",
                "aiuto": "inserire il titolo del corso come riportato sull'attestato"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Ente Erogatore",
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "aiuto": "inserire il nome dell'ente erogatore"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Durata",
                "is_required": true,
                "ordinamento": 2,
                "tipo": "DateInRangeComplexField",
                "aiuto": "inserire data inizio e fine del corso di formazione nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Numero ore",
                "is_required": true,
                "ordinamento": 3,
                "tipo": "DurataComeInteroField",
                "aiuto": "durata complessiva del corso in ore"
              }
            }
          ],
          "object": {
            "id_code": "Ab",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Inserire solo i corsi di formazione che non hanno previsto il superamento di un esame finale",
            "nome": "Corsi di formazione certificati senza superamento di esame finale"
          }
        }
      ],
      "object": {
        "id_code": "A",
        "nome": "Formazione certificata e pertinente"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "IndicatorePonderato",
      "childrens": [
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 2,
            "posizione_economica_id": 2,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 3,
            "posizione_economica_id": 3,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 4,
            "posizione_economica_id": 4,
            "punteggio_max": 25
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 5,
            "posizione_economica_id": 5,
            "punteggio_max": 25
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Valutazione",
                "is_required": true,
                "tipo": "PunteggioFloatField",
                "aiuto": "inserire punteggio attribuito dal responsabile di struttura"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomFileField",
                "nome": "Scheda di qualit\u00e0 delle prestazioni individuali"
              }
            }
          ],
          "object": {
            "id_code": "Ca",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "is_required": true,
            "note": "Inserire il punteggio riportato nella scheda di valutazione della qualit\u00e0 delle prestazioni individuali (Tabella 2 allegata al Bando di Selezione)",
            "nome": "Valutazione scheda"
          }
        }
      ],
      "object": {
        "id_code": "C",
        "ordinamento": 2,
        "nome": "Qualit\u00e0 delle prestazioni individuali"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "IndicatorePonderato",
      "childrens": [
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 2,
            "posizione_economica_id": 2,
            "punteggio_max": 15
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 3,
            "posizione_economica_id": 3,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 4,
            "posizione_economica_id": 4,
            "punteggio_max": 20
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "PunteggioMax_IndicatorePonderato_PosEconomica",
          "childrens": [],
          "object": {
            "posizione_economica": 5,
            "posizione_economica_id": 5,
            "punteggio_max": 30
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 3.6
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 3.6,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 3.6,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 3.6,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Nome e Cognome degli autori",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Tipologia"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "CustomCharField",
                "nome": "Titolo della pubblicazione"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 3,
                "tipo": "CustomCharField",
                "nome": "Pubblicato su"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 4,
                "tipo": "AnnoInRangeOfCarrieraField",
                "nome": "Anno pubblicazione"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "nome": "Max per inserimento singolo",
                "punteggio": 0.2
              }
            }
          ],
          "object": {
            "id_code": "Ea",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Il sottoscritto dichiara che per le pubblicazioni di cui all'art.7 punto E), lett. a), sono stati adempiuti, ove richiesti, gli obblighi previsti dal DPR 03/05/2006 n.252.",
            "nome": "Pubblicazioni pertinenti alle attivit\u00e0 dell'Ufficio"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "TitoloStudioField",
                "nome": "Titolo di studio",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Rilasciato da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "PositiveIntegerField",
                "nome": "Anno di conseguimento"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 3,
                "tipo": "CustomCharField",
                "nome": "Voto"
              }
            }
          ],
          "object": {
            "id_code": "Eb",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Inserire un titolo di studio superiore rispetto a quello richiesto per l'accesso dall'esterno per la categoria di appartenenza",
            "nome": "Ulteriore titolo di studio"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 1.0
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 1.0,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 1.0,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 1.0,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Descrizione corso",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Rilasciato da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "PositiveIntegerField",
                "nome": "Anno di conseguimento"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "nome": "punteggio",
                "punteggio": 0.5
              }
            }
          ],
          "object": {
            "id_code": "Ec",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Inserire esclusivamente titoli rilasciati ai sensi delle disposizioni dell'Ordinamento Universitario",
            "nome": "Corsi di perfezionamento o specializzazione"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Descrizione",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Rilasciato da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "PositiveIntegerField",
                "nome": "Anno di conseguimento"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "nome": "punteggio",
                "punteggio": 2.0
              }
            }
          ],
          "object": {
            "id_code": "Ed",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Inserire il dottorato di ricerca pertinente al lavoro svolto",
            "nome": "Dottorato di ricerca"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 2.0
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 2.0,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 2.0,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": -1.0,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Descrizione Master",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Rilasciato da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Data inizio",
                "is_required": true,
                "ordinamento": 2,
                "tipo": "BaseDateField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Data fine",
                "is_required": true,
                "ordinamento": 3,
                "tipo": "BaseDateField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 4,
                "tipo": "CustomCharField",
                "nome": "Valutazione finale"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "nome": "punteggio",
                "punteggio": 1.0
              }
            }
          ],
          "object": {
            "id_code": "Ee",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Inserire Master pertinenti al lavoro svolto",
            "nome": "Master"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Descrizione",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Conseguita il",
                "is_required": true,
                "ordinamento": 1,
                "tipo": "BaseDateField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "CustomCharField",
                "nome": "Tirocinio effettuato negli anni"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "nome": "punteggio",
                "punteggio": 2.0
              }
            }
          ],
          "object": {
            "id_code": "Ef",
            "numero_inserimenti": 1,
            "nome": "Abilitazione professionale con 2 anni di tirocinio pertinente al lavoro svolto e con certificazione finale",
            "calcolo_punteggio_automatico": true
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Descrizione",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Conseguita il",
                "is_required": true,
                "ordinamento": 1,
                "tipo": "BaseDateField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "Punteggio_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "nome": "punteggio",
                "punteggio": 1.0
              }
            }
          ],
          "object": {
            "id_code": "Eg",
            "numero_inserimenti": 1,
            "nome": "Abilitazione professionale pertinente al lavoro svolto",
            "calcolo_punteggio_automatico": true
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 6.0
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 6.0,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 6.0,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 6.0,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 1000,
                    "nome": "punteggio per anno",
                    "unita_temporale": "m",
                    "punteggio": 0.166666667
                  }
                }
              ],
              "object": {
                "id_code": "Ea-1",
                "nome": "Responsabilit\u00e0 di Aree"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 10000,
                    "nome": "punteggio per mese",
                    "unita_temporale": "m",
                    "punteggio": 0.125
                  }
                }
              ],
              "object": {
                "id_code": "Eh-2",
                "nome": "Responsabilit\u00e0 di Unit\u00e0 Strategiche / Unit\u00e0 Organizzative Complesse / Unit\u00e0 Organizzative Speciali / Avvocatura"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 10000,
                    "nome": "punteggio per mese",
                    "unita_temporale": "m",
                    "punteggio": 0.0833333333
                  }
                }
              ],
              "object": {
                "id_code": "Eh-3",
                "nome": "Responsabilit\u00e0 di Settori, di Servizi, di Centri, di Biblioteche nonch\u00e9 incarichi di Segretari di Dipartimento, Liaison Office"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 100000,
                    "nome": "punteggio per mese",
                    "unita_temporale": "m",
                    "punteggio": 0.0625
                  }
                }
              ],
              "object": {
                "id_code": "Eh-4",
                "nome": "Responsabilit\u00e0 di Laboratori"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 100000,
                    "nome": "punteggio per mese",
                    "unita_temporale": "m",
                    "punteggio": 0.041666667
                  }
                }
              ],
              "object": {
                "id_code": "Eh-5",
                "nome": "Responsabilit\u00e0 di Uffici"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 100000,
                    "nome": "punteggio per mese",
                    "unita_temporale": "m",
                    "punteggio": 0.083
                  }
                }
              ],
              "object": {
                "id_code": "Eh-6",
                "nome": "Responsabilit\u00e0 di Unit\u00e0 Tecniche Centro ICT"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore_TimeDelta",
                  "childrens": [],
                  "object": {
                    "operatore": "x",
                    "durata_minima": 1,
                    "durata_massima": 100000,
                    "nome": "punteggio per mese",
                    "unita_temporale": "m",
                    "punteggio": 0.042
                  }
                }
              ],
              "object": {
                "id_code": "Eh-7",
                "nome": "Responsabilit\u00e0 di Uffici Centro ICT"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Area o Struttura",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "SubDescrizioneIndicatoreField",
                "nome": "Tipo di incarico"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "CustomCharField",
                "nome": "Conferito da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 3,
                "tipo": "ProtocolloField",
                "nome": "Estremi dell\u2019atto di conferimento (protocollo/provvedimento e data)"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Ricoperto nel periodo",
                "is_required": true,
                "ordinamento": 4,
                "tipo": "DateInRangeInCorsoComplexField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            }
          ],
          "object": {
            "id_code": "Eh",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "note": "Se conferiti da altro Ateneo inserire tutte le corrispondenti informazioni",
            "nome": "Incarichi di responsabilit\u00e0 conferiti da Organi di Governo, Direttore Generale o dal Responsabile della Struttura di afferenza del dipendente"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 5.0
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 5.0,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 5.0,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 5.0,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.5
                  }
                }
              ],
              "object": {
                "id_code": "Ei-1",
                "nome": "Incarico di Responsabile Unico del Procedimento"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.2
                  }
                }
              ],
              "object": {
                "id_code": "Ei-2",
                "nome": "Incarico di progettazione"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.2
                  }
                }
              ],
              "object": {
                "id_code": "Ei-3",
                "nome": "Incarico di direzione di opere"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.2
                  }
                }
              ],
              "object": {
                "id_code": "Ei-4",
                "nome": "Altri incarichi di cui al Codice dei Contratti"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "SubDescrizioneIndicatoreField",
                "nome": "Tipo di incarico",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Area o Struttura"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "CustomCharField",
                "nome": "Descrizione incarico"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 3,
                "tipo": "CustomCharField",
                "nome": "Conferito da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 4,
                "tipo": "ProtocolloField",
                "nome": "Estremi dell\u2019atto di conferimento (protocollo e data)"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Ricoperto nel periodo",
                "is_required": true,
                "ordinamento": 5,
                "tipo": "DateInRangeInCorsoComplexField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            }
          ],
          "object": {
            "id_code": "Ei",
            "numero_inserimenti": 1,
            "nome": "Incarichi di cui al Codice dei Contratti",
            "calcolo_punteggio_automatico": true
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "posizione_economica_id": 2,
                "posizione_economica": 2,
                "punteggio_max": 4.4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 4.4,
                "ordinamento": 1,
                "posizione_economica_id": 3,
                "posizione_economica": 3
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 4.4,
                "ordinamento": 2,
                "posizione_economica_id": 4,
                "posizione_economica": 4
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "PunteggioMax_DescrizioneIndicatore_PosEconomica",
              "childrens": [],
              "object": {
                "punteggio_max": 4.4,
                "ordinamento": 3,
                "posizione_economica_id": 5,
                "posizione_economica": 5
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.5
                  }
                }
              ],
              "object": {
                "id_code": "Ej-1",
                "nome": "Amministratore di sistema"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.2
                  }
                }
              ],
              "object": {
                "id_code": "Ej-2",
                "nome": "Responsabile di procedimento amministrativo"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.1
                  }
                }
              ],
              "object": {
                "id_code": "Ej-3",
                "nome": "Componente di commissioni di concorso, di gare di appalto e commissioni elettorali"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.07
                  }
                }
              ],
              "object": {
                "id_code": "Ej-4",
                "nome": "Vigilante in commissioni di concorso, di gare di appalto e di commissioni elettorali"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.2
                  }
                }
              ],
              "object": {
                "id_code": "Ej-5",
                "nome": "Partecipazione a seminari e convegni in qualit\u00e0 di relatore"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.1
                  }
                }
              ],
              "object": {
                "id_code": "Ej-6",
                "nome": "Partecipazione a seminari e convegni in qualit\u00e0 di membro del comitato organizzatore"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.3
                  }
                }
              ],
              "object": {
                "id_code": "Ej-7",
                "nome": "Incarichi di docenza"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [
                {
                  "m2m": [],
                  "app_name": "gestione_peo",
                  "related_field": "sub_descrizione_indicatore",
                  "model_name": "Punteggio_SubDescrizioneIndicatore",
                  "childrens": [],
                  "object": {
                    "nome": "punteggio",
                    "punteggio": 0.3
                  }
                }
              ],
              "object": {
                "id_code": "Ej-8",
                "nome": "Componente di gruppo di lavoro"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "SubDescrizioneIndicatoreField",
                "nome": "Tipo di incarico",
                "is_required": true
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 1,
                "tipo": "CustomCharField",
                "nome": "Area o Struttura"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 2,
                "tipo": "CustomCharField",
                "nome": "Descrizione incarico"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 3,
                "tipo": "CustomCharField",
                "nome": "Conferito da"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "is_required": true,
                "ordinamento": 4,
                "tipo": "ProtocolloField",
                "nome": "Estremi dell\u2019atto di conferimento (protocollo e data)"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "nome": "Ricoperto nel periodo",
                "is_required": true,
                "ordinamento": 5,
                "tipo": "DateInRangeInCorsoComplexField",
                "aiuto": "inserire data nel formato dd/mm/yyyy oppure yyyy-mm-dd"
              }
            }
          ],
          "object": {
            "id_code": "Ej",
            "numero_inserimenti": 1,
            "nome": "Altri incarichi non compresi nelle precedenti tipologie",
            "calcolo_punteggio_automatico": true
          }
        }
      ],
      "object": {
        "id_code": "E",
        "ordinamento": 4,
        "nome": "Titoli culturali e professionali"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "IndicatorePonderato",
      "childrens": [
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [
                "posizione_economica"
              ],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "CategorieDisabilitate_DescrizioneIndicatore",
              "childrens": [],
              "object": {
                "posizione_economica": [
                  {
                    "m2m": [],
                    "model_name": "PosizioneEconomica",
                    "app_name": "gestione_risorse_umane",
                    "childrens": [],
                    "object": {
                      "descrizione": "Qui chiedere ai colleghi di risorse umane di inserire le caratteristiche peculiari di ogni posizione economica, cos\u00ec da visualizzarli a sistema",
                      "nome": "B"
                    }
                  },
                  {
                    "m2m": [],
                    "model_name": "PosizioneEconomica",
                    "app_name": "gestione_risorse_umane",
                    "childrens": [],
                    "object": {
                      "nome": "C"
                    }
                  }
                ]
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-1",
                "nome": "Insigniti di medaglia al valor militare"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-2",
                "nome": "Mutilati ed invalidi di guerra ex-combattenti"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-3",
                "nome": "Mutilati ed invalidi per fatto di guerra"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-4",
                "nome": "Mutilati ed invalidi per servizio nel settore pubblico e privato"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-5",
                "nome": "Orfani di guerra"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-6",
                "nome": "Orfani dei caduti per fatto di guerra"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-7",
                "nome": "Orfani dei caduti per servizio nel settore pubblico e privato"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-8",
                "nome": "Feriti in combattimento"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-9",
                "nome": "Insigniti di croce di guerra o di altra attestazione speciale di merito di guerra, nonch\u00e9 i capi di famiglia numerosa"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-10",
                "nome": "Figli dei mutilati e degli invalidi di guerra ex-combattenti"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-11",
                "nome": "Figli dei mutilati e degli invalidi per fatto di guerra"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-12",
                "nome": "Figli dei mutilati e degli invalidi per servizio nel settore pubblico e privato"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-13",
                "nome": "Genitori vedovi non risposati, coniugi non risposati e le sorelle ed i fratelli vedovi o non sposati dei caduti in guerra"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-14",
                "nome": "Genitori vedovi non risposati, coniugi non risposati e le sorelle ed i fratelli vedovi o non sposati dei caduti per fatto di guerra"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-15",
                "nome": "Genitori vedovi non risposati, coniugi non risposati e le sorelle ed i fratelli vedovi o non sposati dei caduti per servizio nel settore pubblico e privato"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-16",
                "nome": "Coloro che abbiano prestato servizio militare come combattenti"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-17",
                "nome": "Coloro che abbiano prestato lodevole servizio a qualunque titolo per non meno di un anno nell'Amministrazione che ha indetto il concorso"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-18",
                "nome": "Gli invalidi ed i mutilati civili"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "SubDescrizioneIndicatore",
              "childrens": [],
              "object": {
                "id_code": "PR-a-19",
                "nome": "Militari volontari delle Forze armate congedati senza demerito al termine della ferma o rafferma"
              }
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "SubDescrizioneIndicatoreField",
                "nome": "Titolo di preferenza",
                "is_required": true
              }
            }
          ],
          "object": {
            "id_code": "PR-a",
            "numero_inserimenti": 1,
            "nome": "Titolo di preferenza",
            "calcolo_punteggio_automatico": true
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "CategorieDisabilitate_DescrizioneIndicatore",
              "childrens": [],
              "object": {}
            },
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "PositiveIntegerField",
                "nome": "Numero dei figli a carico",
                "is_required": true
              }
            }
          ],
          "object": {
            "id_code": "PR-b",
            "numero_inserimenti": 1,
            "calcolo_punteggio_automatico": true,
            "is_required": true,
            "nome": "I coniugati e i non coniugati riguardo al numero dei figli a carico"
          }
        },
        {
          "m2m": [],
          "app_name": "gestione_peo",
          "related_field": "indicatore_ponderato",
          "model_name": "DescrizioneIndicatore",
          "childrens": [
            {
              "m2m": [],
              "app_name": "gestione_peo",
              "related_field": "descrizione_indicatore",
              "model_name": "ModuloInserimentoCampi",
              "childrens": [],
              "object": {
                "tipo": "CustomCharField",
                "nome": "Amministrazione pubblica",
                "is_required": true
              }
            }
          ],
          "object": {
            "id_code": "PR-c",
            "numero_inserimenti": 1,
            "nome": "Avere prestato lodevole servizio nelle Amministrazioni Pubbliche",
            "calcolo_punteggio_automatico": true
          }
        }
      ],
      "object": {
        "id_code": "PR",
        "nome": "Titoli di Preferenza"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_Anzianita_Servizio",
      "childrens": [],
      "object": {
        "posizione_economica_id": 2,
        "posizione_economica": 2,
        "punteggio": 0.041666667,
        "unita_temporale": "m"
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_Anzianita_Servizio",
      "childrens": [],
      "object": {
        "ordinamento": 1,
        "posizione_economica_id": 3,
        "unita_temporale": "m",
        "punteggio": 0.033333333,
        "posizione_economica": 3
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_Anzianita_Servizio",
      "childrens": [],
      "object": {
        "ordinamento": 2,
        "posizione_economica_id": 4,
        "unita_temporale": "m",
        "punteggio": 0.033333333,
        "posizione_economica": 4
      }
    },
    {
      "m2m": [],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "Punteggio_Anzianita_Servizio",
      "childrens": [],
      "object": {
        "ordinamento": 3,
        "posizione_economica_id": 5,
        "unita_temporale": "m",
        "punteggio": 0.0208333333,
        "posizione_economica": 5
      }
    },
    {
      "m2m": [
        "posizione_economica"
      ],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "CategorieDisabilitate_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_studio_id": 20,
        "titolo_studio": 20,
        "posizione_economica": [
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "D"
            }
          },
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "EP"
            }
          }
        ]
      }
    },
    {
      "m2m": [
        "posizione_economica"
      ],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "CategorieDisabilitate_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_studio_id": 19,
        "ordinamento": 1,
        "titolo_studio": 19,
        "posizione_economica": [
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "D"
            }
          },
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "EP"
            }
          }
        ]
      }
    },
    {
      "m2m": [
        "posizione_economica"
      ],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "CategorieDisabilitate_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_studio_id": 18,
        "ordinamento": 2,
        "titolo_studio": 18,
        "posizione_economica": [
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "D"
            }
          },
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "EP"
            }
          }
        ]
      }
    },
    {
      "m2m": [
        "posizione_economica"
      ],
      "app_name": "gestione_peo",
      "related_field": "bando",
      "model_name": "CategorieDisabilitate_TitoloStudio",
      "childrens": [],
      "object": {
        "titolo_studio_id": 30,
        "ordinamento": 3,
        "titolo_studio": 30,
        "posizione_economica": [
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "C"
            }
          },
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "D"
            }
          },
          {
            "m2m": [],
            "model_name": "PosizioneEconomica",
            "app_name": "gestione_risorse_umane",
            "childrens": [],
            "object": {
              "nome": "EP"
            }
          }
        ]
      }
    }
  ],
  "object": {
    "data_inizio": "2018-11-14T07:00:00+00:00",
    "data_fine_presentazione_domande": "2019-12-14T22:59:00+00:00",
    "agevolazione_fatmol": 3,
    "data_validita_titoli_fine": "2017-12-31",
    "slug": "peo-2018-97df0b61a50c4960a95b2b6c5cd26510-ab1a2d832366467ca1c4df972292fdd6",
    "agevolazione_soglia_anni": 3,
    "protocollo_required": true,
    "nome": "PEO 2018",
    "protocollo_cod_titolario": "9095",
    "bando_url": "http://www.unical.it/portale/concorsi/view_bando.cfm?Q_BAN_ID=6822&Q_COMM=",
    "priorita_titoli_studio": true,
    "email_avvenuto_completamento": true,
    "protocollo_fascicolo_numero": "3",
    "ultima_progressione": "2016-01-01",
    "pubblica_punteggio": true,
    "data_fine": "2019-12-14T22:59:00+00:00",
    "pubblicato": true,
    "accettazione_clausole_text": "None",
    "anni_servizio_minimi": 2
  }
}
````
