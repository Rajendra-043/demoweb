import os, sys, django
sys.path.insert(0, r"C:\Users\my pc\web page\backend")
os.environ["DJANGO_SETTINGS_MODULE"] = "tecno.settings"
django.setup()
import django as dj
print("django", dj.get_version(), "| python", sys.version.split()[0])

from copy import copy
from django.template.context import RequestContext, Context
from django.test import RequestFactory

rf = RequestFactory()
req = rf.get("/")
rc = RequestContext(req)
try:
    c = copy(rc)
    print("copy(RequestContext) -> OK", type(c))
except Exception as e:
    print("copy(RequestContext) -> FAILS:", type(e).__name__, e)

try:
    c = copy(Context({"a": 1}))
    print("copy(Context)        -> OK", type(c))
except Exception as e:
    print("copy(Context)        -> FAILS:", type(e).__name__, e)
