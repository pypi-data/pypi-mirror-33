import pretty_output, argparse, traceback, textwrap

from kooki.tools import read_config_file
from kooki.config import parse_document_rules
from kooki.config import get_kooki_jar_manager, get_kooki_dir_jars

from kooki.exception import KookiException
from kooki.processor import process_document
from kooki.processor.jars import jar_dependencies

from karamel.command import Command
from karamel.packages import install_packages
from karamel.exception import KaramelException



__command__ = 'bake'
__description__ = 'Bake a kooki'


class BakeCommand(Command):

    def __init__(self):
        super(BakeCommand, self).__init__(__command__, __description__)

        help_help_message = 'Show this help message and exit.'
        debug_help_message = 'Show information to help debug the bake processing'

        self.add_argument('documents', nargs='*')
        self.add_argument('--config-file', default='kooki.yaml')
        self.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                          help=help_help_message)
        self.add_argument('-d', '--debug', help=debug_help_message, action='store_true')
        self.add_argument('--no-color', help='The output has no color.', action='store_true')
        self.add_argument('--no-output', help='There is no output', action='store_true')
        self.add_argument('--update', help='Update jars.', action='store_true')

    def callback(self, args):
        try:
            pretty_output.set_output_policy(not args.no_output)
            pretty_output.set_color_policy(not args.no_color)
            pretty_output.set_debug_policy(args.debug)

            real_call(args)

        except KookiException as e:
            pretty_output.error_step('Errors')
            pretty_output.error(e)

        except Exception as e:
            pretty_output.error_step('Errors')
            pretty_output.error(traceback.format_exc()[:-1])


def real_call(args):
    config = read_config_file(args.config_file, must_exist=True)
    document_rules = parse_document_rules(config)
    do_update = args.update

    document = get_documents_to_generate(args, document_rules)

    if isinstance(document, dict):
        generate_documents(document, do_update)
    else:
        generate_document(document, do_update)

def get_documents_to_generate(args, document_rules):
    if args.documents == []:
        documents = document_rules
    else:
        documents = {}
        for document_name in args.documents:
            if document_name in document_rules:
                documents[document_name] = document_rules[document_name]
            else:
                raise Exception('Bad document')
    return documents


def generate_documents(documents, do_update):
    for name, document in documents.items():
        pretty_output.title_1(name)
        generate_document(document, do_update)
        pretty_output.title_2()


def generate_document(document, do_update):
    if do_update:
        execute_update(document)
    execute_bake(document)


def on_package_downloading(package_name):
    print('Downloading \'{}\''.format(package_name))


def on_package_installing(package_name):
    print('Installing \'{}\''.format(package_name))


def on_package_install_success(package_name):
    print('Successfully installed \'{}\''.format(package_name))


def on_package_already_installed(package):
    def callback(package_name, package_path):
        message = textwrap.dedent('''\
            {} '{}' already installed in '{}'.
            ''').format(package, package_name, package_path)
        print(message)
    return callback


def on_package_not_found(package):
    def callback(package_name):
        raise KookiException('{} not found \'{}\'.'.format(package, package_name))
    return callback


def on_package_bad_version_provided(package):
    def callback(package_name, version):
        message = textwrap.dedent('''\
            Could not find the version '{1}' for {2} '{0}'.
            ''').format(package_name, version, package)
        raise KookiException(message)
    return callback


def on_package_could_not_be_download(package):
    def callback(package_name):
        message = textwrap.dedent('''\
            {} \'{}\' could not be download.
            Without this package the document cannot be generated.
            Are you connected to the Internet ?''').format(package_name)
        raise KookiException(message.format(package, package_name))
    return callback


def execute_update(document):
    pretty_output.title_2('update')
    try:
        pretty_output.title_3('jars')
        install_jars(document.jars)
    except KaramelException as e:
        print(e)


def install_jars(jars):
    package_manager_url = get_kooki_jar_manager()
    package_install_dir = get_kooki_dir_jars()

    install_packages(package_manager_url,
                     package_install_dir,
                     jars,
                     on_package_downloading,
                     on_package_installing,
                     on_package_install_success,
                     on_package_already_installed('Jar'),
                     on_package_not_found('Jar'),
                     on_package_bad_version_provided('jar'),
                     on_package_could_not_be_download('Jar'))

    for jar in jars:
        jars = jar_dependencies(jar)
        install_jars(jars)


def execute_bake(document):
    pretty_output.title_2('bake')
    process_document(document, pretty_output.title_3)
