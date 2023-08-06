# -*- encoding: utf-8 -*-
from py3o.formats import Formats, FORMAT_PDF
from py3o.renderers.juno import start_jvm, Convertor
from datetime import datetime as dt

start_jvm(
    "/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/server/libjvm.so",
    "/usr/lib/libreoffice",
    "/usr/share",
    140)
c = Convertor("127.0.0.1", "8997")

t1 = dt.now()
c.convert(
    "py3o_example.odt",
    "py3o_example.pdf",
    Formats().get_format(FORMAT_PDF).odfname,
)
t2 = dt.now()
print("rendered in", t2 - t1)
