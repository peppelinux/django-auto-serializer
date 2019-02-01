# django-auto-serializer
Django app that automates objects tree serialization recursively, wihtout any declaration.

Define new classes for every Object serialization could sound a bit boring, so I coded this way to do the things.
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

# all the fields
# bando._meta._forward_fields_map

# childrens here
# bando._meta.fields_map
## bando._meta.related_objects

# another way with NestedObjects
# from django.contrib.admin.utils import NestedObjects
# from django.db import DEFAULT_DB_ALIAS

# get json with pk and autofilled fields as they are
# from django.core import serializers
# serializers.serialize('json', [bando], ensure_ascii=False)

# serializers.serialize() relies on it
# model_to_dict(bando)

#pprint(sit.dict)
# for i in sit.dict['childrens']:
    # if i['model_name'] == 'IndicatorePonderato':
        # pprint(i)
        
# tree_to_str = json.dumps(si.dict, indent=2)
# jsonstr_to_dict = json.loads(tree_to_str)
# pprint(jsonstr_to_dict )

isi = ImportableSerializedInstance(si.dict)
isi.save()
# print(isi.json())
````
