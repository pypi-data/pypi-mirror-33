import os
import re
import subprocess
import sys
import zipfile

DEFAULT_DRIVER_FILES = [
    'datamodel',
    'main.py',
    'install_driver.bat',
    'driver_exe_template',
    'requirements.txt',
    'version.txt'
]


def zip_driver(driver_path, driver_zip_file, files):
    with zipfile.ZipFile(driver_zip_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for name in files:
            _append_files(os.path.join(driver_path, name), zip_file)


def _append_files(path, zip_file):
    if os.path.isfile(path):
        rel_path = os.path.relpath(path, os.path.join(path, os.path.pardir, os.path.pardir))
        zip_file.write(path, rel_path)
    else:
        for root, dirs, files in os.walk(path):
            for file_or_dir in files + dirs:
                if not file_or_dir.endswith('.pyc'):
                    full_path = os.path.join(root, file_or_dir)
                    rel_path = os.path.relpath(full_path, os.path.join(path, os.path.pardir, os.path.pardir))
                    zip_file.write(full_path, rel_path)


def download_packages(packages_path, requirements):
    subprocess.call(['pip', 'download', '-r', requirements, '-d', packages_path, '-q'])


def _print_help():
    message = """Usage: build_driver [OPTIONS]

Options:
    -h, --help  Show this message and exit.
    -i, --ignore-packages  Do not collect driver dependencies
    """
    print(message)


def build(args=None):
    if not args:
        args = sys.argv

    if '--help' in args[1:] or '-h' in args[1:]:
        _print_help()
        sys.exit(0)

    # driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    driver_path = os.getcwd()

    with open(os.path.join(driver_path, 'version.txt')) as ver_file:
        version = ver_file.read().strip()

    driver_folder_name = os.path.basename(driver_path)
    driver_name = re.sub('cloudshell-L1-', '', driver_folder_name, flags=re.IGNORECASE)
    driver_name = re.sub('-', '_', driver_name)
    if os.path.exists(os.path.join(driver_path, driver_name)):
        DEFAULT_DRIVER_FILES.append(driver_name)
    else:
        print('Cannot find driver src folder {}'.format(driver_name))
        sys.exit(1)
    driver_folder_name_ver = '{}-{}'.format(driver_folder_name, version)
    dist_path = os.path.join(driver_path, 'dist')
    driver_zip_path = os.path.join(dist_path, driver_folder_name_ver + '.zip')

    if not os.path.exists(dist_path):
        os.mkdir(dist_path)

    if '--ignore-packages' not in args[1:] and '-i' not in args[1:]:
        packages_path = os.path.join(driver_path, 'packages')
        requirements_path = os.path.join(driver_path, 'requirements.txt')

        if not os.path.exists(packages_path):
            os.mkdir(packages_path)

        download_packages(packages_path, requirements_path)
        DEFAULT_DRIVER_FILES.append('packages')

    zip_driver(driver_path, driver_zip_path, DEFAULT_DRIVER_FILES)


if __name__ == '__main__':
    build()
