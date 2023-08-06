import jpype
from jpype import startJVM
from jpype import JPackage

import os
import json
import platform
import logging
import pkg_resources

log = logging.getLogger(__name__)

# define some hard coded jar resource we will try to find when starting the JVM
ureitems = [
    "juh.jar",
    "jurt.jar",
    "ridl.jar",
    "unoloader.jar",
    "java_uno.jar",
    "gson.jar",
    ]
basisitems = ["unoil.jar"]


def get_oo_context():
    """returns a dict with the java_classpath_sep, ure_subpath
    and oooclasses_subpath key pointing the (hopefully) correct sub paths
    for the current running plateform. The implementer still needs
    to provide the real base path for his plateform elsewhere in its
    code though...

    @param office_version: the version number of the desired
    OpenOffice/LibreOffice
    @type office_version: string
    """

    context = dict()

    if os.name in ('nt', 'os2', 'ce'):  # Windows
        context['java_classpath_sep'] = ";"
        context['ure_subpath'] = os.path.join('URE', 'java')
        context['oooclasses_subpath'] = os.path.join(
            "Basis", "program", "classes"
        )
    else:
        context['java_classpath_sep'] = ":"
        context['oooclasses_subpath'] = os.path.join("program", "classes")

        # TODO: add more platforms
        if os.name == 'posix' and platform.dist()[0] in ('Ubuntu', 'debian'):
            context['ure_subpath'] = 'java'
        else:
            context['ure_subpath'] = os.path.join('ure', 'share', 'java')

    return context


def start_jvm(jvm, oobase, urebase, max_mem):
    """this small function should be called only once. At the beginning
    of your program.
    It takes care of starting the JVM that will be used by our
    convertor library with our requirements in terms of
    classpath and memory usage

    returns nothing

    @param jvm: the jvm path to use :
    ie c:/Program Files/Java/jre1.5.0_05/bin/client/jvm.dll
    @type jvm: string

    @param oobase: the base directory where we will find the
    program/classes/unoil.jar package
    @type oobase: string

    @param urebase: the base directory where we will find ure/share/java inside
    which we should find java_uno.jar, juh.jar, jurt.jar, unoloader.jar
    @type oobase: string

    @param max_mem: the maximum amount of mega bytes to allocate to
    our JVM
    @type max_mem: integer
    """

    context = get_oo_context()
    java_classpath_sep = context.get('java_classpath_sep')
    ure_subpath = context.get('ure_subpath')
    oooclasses_subpath = context.get('oooclasses_subpath')

    # this is our internally compiled java class
    jar = pkg_resources.resource_filename(
        'py3o.renderers.juno', 'py3oconverter.jar'
    )
    oojars = list()

    for ureitem in ureitems:
        oojars.append(os.path.join(urebase, ure_subpath, ureitem))

    for basisitem in basisitems:
        oojars.append(os.path.join(oobase, oooclasses_subpath, basisitem))

    convertor_lib = os.path.abspath(jar)
    java_classpath = '-Djava.class.path=%s' % (convertor_lib)

    for oojar in oojars:
        java_classpath += "%s%s" % (java_classpath_sep, oojar)

    # -Xms is initial memory for java, -Xmx is maximum memory for java
    # java_initmem = "-Xms%sM" % max_mem
    java_maxmem = "-Xmx%sM" % max_mem
    jvm_abs = os.path.abspath(jvm)
    logging.debug('Starting JVM: %s with options: %s %s' % (
        jvm_abs, java_classpath, java_maxmem))
    startJVM(jvm_abs, java_classpath, java_maxmem)


class Convertor(object):

    def __init__(self, host, port):
        """init our java lib with the host and port for the open office server
        """
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

        jconvertor_package = JPackage('py3oconverter').Convertor
        self.jconvertor = jconvertor_package(host, port)

    def convert(self, infilename, outfilename, filtername, pdf_options):
        """convert the input file using a certain filter produce a result
        in outputfile.

        :param infilename: a file name that must exist and be readable,
        containing the input document to be converted
        :type infilename: string

        :param outfilename: a filename that must exit and be writeable,
        inside which the convertor will save the result
        :type outfilename: string

        :param filtername: a LibreOffice filter name to use for conversion
        :type filtername: string

        :param pdf_options: a dict with PDF export options
        :type pdf_options: dict

        :returns: nothing
        :raises: jpype._jexception
        """
        if not pdf_options:
            pdf_options = {}
        log.debug('pdf_options=%s', pdf_options)
        pdf_options_types = {}
        pdf_options_fullstr = {}
        for option_name, option_val in pdf_options.items():
            if not isinstance(option_name, (str, unicode)):
                log.error(
                    'The keys of the pdf_options dict must be strings.'
                    '(wrong key: %s type %s', option_name, type(option_name))
                continue
            if isinstance(option_val, bool):
                pdf_options_types[option_name] = 'boolean'
                pdf_options_fullstr[option_name] = str(option_val).lower()
            elif isinstance(option_val, (int, long)):
                pdf_options_types[option_name] = 'integer'
                pdf_options_fullstr[option_name] = str(option_val)
            elif isinstance(option_val, (str, unicode)):
                pdf_options_types[option_name] = 'string'
                pdf_options_fullstr[option_name] = option_val
            else:
                log.error(
                    'Unsupported option type: %s type %s',
                    option_name, type(option_val))
        pdf_options_json = json.dumps(pdf_options_fullstr)
        pdf_options_types_json = json.dumps(pdf_options_types)
        log.debug('pdf_options_json=%s', pdf_options_json)
        log.debug('pdf_options_types_json=%s', pdf_options_types_json)
        # use our java lib...
        self.jconvertor.convert(
            infilename,
            outfilename,
            filtername,
            pdf_options_json,
            pdf_options_types_json)
