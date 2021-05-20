# Django auto-serializer
Django app that automates objects tree serialization recursively, without any declarations.

Define new classes for every Object serialization could sound a bit boring, I coded this app to do the things automagically.
Django-auto-serializer will do for you:

- Json serialization (export);
- recursively serialize all FK childrens;
- can ignore some children if you tell him how they are named (see examples above);
- M2M auto serialization;
- ignore or not autofields import/export (auto_now_add...);
- regenerates unique if needed, the same for slugfields (change_uniques = True,);
- Import a serialized Object tree, it will build up everything as before;

## Setup
````
pip install git+https://github.com/peppelinux/django-auto-serializer.git
````

## Usage Example
````
from cms.menus.models import *

# get an object
menu = NavigationBar.objects.first()

# object serialization
# A single object duplication
si = SerializableInstance(menu)

#si.serialize_obj()
si.serialize_tree()
si.remove_duplicates()
# pprint(si.dict)

# Serialized entire tree, main object with childrens
si = SerializableInstance(menu,
                          excluded_fields=['created', 'modified'],
                          excluded_childrens = ['pagemenu'],
                          auto_fields = False,
                          change_uniques = True,
                          duplicate = True)
si.serialize_tree()
si.remove_duplicates()
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
            si.serialize_tree()
            si.remove_duplicates()
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
{'source_pk': 83,
 'app_name': 'cmsmenus',
 'model_name': 'NavigationBar',
 'object': {'created_by': 2,
  'created_by_id': 2,
  'modified_by': 2,
  'modified_by_id': 2,
  'is_active': True,
  'name': 'mio menu copia test'},
 'm2m': [],
 'childrens': [{'source_pk': 896,
   'app_name': 'cmsmenus',
   'model_name': 'NavigationBarItem',
   'object': {'created_by': 2,
    'created_by_id': 2,
    'modified_by': 2,
    'modified_by_id': 2,
    'order': 1,
    'is_active': True,
    'name': 'child 1',
    'parent': 895,
    'parent_id': 895,
    'url': 'None'},
   'm2m': [],
   'childrens': [{'source_pk': 897,
     'app_name': 'cmsmenus',
     'model_name': 'NavigationBarItem',
     'object': {'created_by': 2,
      'created_by_id': 2,
      'modified_by': 2,
      'modified_by_id': 2,
      'order': 2,
      'is_active': True,
      'menu': 83,
      'menu_id': 83,
      'name': 'child 2',
      'url': 'None'},
     'm2m': [],
     'childrens': [],
     'depth': 2,
     'save': False,
     'related_field': 'parent'}],
   'depth': 1,
   'save': False,
   'related_field': 'menu'},
  {'source_pk': 897,
   'app_name': 'cmsmenus',
   'model_name': 'NavigationBarItem',
   'object': {'created_by': 2,
    'created_by_id': 2,
    'modified_by': 2,
    'modified_by_id': 2,
    'order': 2,
    'is_active': True,
    'name': 'child 2',
    'parent': 896,
    'parent_id': 896,
    'url': 'None'},
   'm2m': [],
   'childrens': [],
   'depth': 1,
   'save': False,
   'related_field': 'menu'},
  {'source_pk': 895,
   'app_name': 'cmsmenus',
   'model_name': 'NavigationBarItem',
   'object': {'created_by': 2,
    'created_by_id': 2,
    'modified_by': 2,
    'modified_by_id': 2,
    'order': 10,
    'is_active': True,
    'name': 'parent',
    'url': 'None'},
   'm2m': [],
   'childrens': [{'source_pk': 896,
     'app_name': 'cmsmenus',
     'model_name': 'NavigationBarItem',
     'object': {'created_by': 2,
      'created_by_id': 2,
      'modified_by': 2,
      'modified_by_id': 2,
      'order': 1,
      'is_active': True,
      'menu': 83,
      'menu_id': 83,
      'name': 'child 1',
      'url': 'None'},
     'm2m': [],
     'childrens': [{'source_pk': 897,
       'app_name': 'cmsmenus',
       'model_name': 'NavigationBarItem',
       'object': {'created_by': 2,
        'created_by_id': 2,
        'modified_by': 2,
        'modified_by_id': 2,
        'order': 2,
        'is_active': True,
        'menu': 83,
        'menu_id': 83,
        'name': 'child 2',
        'url': 'None'},
       'm2m': [],
       'childrens': [],
       'depth': 3,
       'save': True,
       'related_field': 'parent'}],
     'depth': 2,
     'save': True,
     'related_field': 'parent'}],
   'depth': 1,
   'save': True,
   'related_field': 'menu'}],
 'depth': 0,
 'save': True}
````
