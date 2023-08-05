import shutil
import d4
import argparse
import sys
import yaml
import os
import subprocess

VERSION = "0.1.6"
PKG_PATH = (d4.__path__)[0]

def get_version():
    return VERSION

def init_project(project_name):
    shutil.copytree(PKG_PATH + "/data", "./" + project_name)

def get_common_params():
    common_params = {}

    if os.path.isfile("common.yaml"):
        f = open("common.yaml", "r")
        common_params = yaml.load(f)
        if common_params is None:
            common_params = {}
        f.close()
    else:
        print("ERROR: file 'common.yaml' is not found")
        sys.exit(1)

    return(common_params)

def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if line:
            yield line
        if not line and process.poll() is not None:
            break
    process.stdout.close()
    yield process.returncode

def check_params(check_file, keys_list, dict):
    for key in keys_list:
        if not key in dict:
            print("ERROR: %s do not have key '%s'" % (check_file, key))
            sys.exit(1)

def build():
    common_params = get_common_params()
    build_params = {}

    if os.path.isfile("build.yaml"):
        f = open("build.yaml", "r")
        build_params = yaml.load(f)
        if build_params is None:
            build_params = {}
        f.close()

    check_list = ["image_name", "registry_server"]
    check_params("common.yaml", check_list, common_params)

    build_args_str = ""
    if "args" in build_params:
        for key, value in build_params["args"].items():
            build_args_str += "--build-arg %s=%s " % (key, value)

    image_name = common_params["registry_server"] + "/" + common_params["image_name"]

    build_cmd = (
        "docker build . "
        "-t %s %s" % (image_name, build_args_str)
    )
    for rv in run_cmd(build_cmd):
        if type(rv) == type(0):
            return(rv)
        else:
            print(rv.decode("utf-8").rstrip())

def test():
    common_params = get_common_params()
    test_files = []

    check_list = ["image_name", "registry_server"]
    check_params("common.yaml", check_list, common_params)

    if os.path.isdir("tests"):
        test_files = os.listdir(path="tests")
    else:
        print("ERROR: directroy 'tests' is not found")
        sys.exit(1)

    if test_files == []:
        print("ERROR: directroy 'tests' has no test files")
        sys.exit(1)

    test_files_str = ""
    for file in test_files:
       test_files_str += "--config tests/%s " % file

    image_name = common_params["registry_server"] + "/" + common_params["image_name"]

    test_cmd = (
        "container-structure-test test "
        "--image %s %s" % (image_name, test_files_str)
    )
    for rv in run_cmd(test_cmd):
        if type(rv) == type(0):
            return(rv)
        else:
            print(rv.decode("utf-8").rstrip())

def login(registry_user, registry_pass):
    common_params = get_common_params()

    check_list = ["registry_server"]
    check_params("common.yaml", check_list, common_params)
    
    login_option = "-u %s -p %s " % (registry_user, registry_pass)

    login_cmd = (
        "docker login "
        "%s %s" % (login_option, common_params["registry_server"])
    )
    for rv in run_cmd(login_cmd):
        if type(rv) == type(0):
            return(rv)
        else:
            print(rv.decode("utf-8").rstrip())

def push():
    common_params = get_common_params()

    check_list = ["image_name", "registry_server"]
    check_params("common.yaml", check_list, common_params)
    
    image_name = common_params["registry_server"] + "/" + common_params["image_name"]

    push_cmd = (
        "docker push "
        "%s" % image_name
    )
    for rv in run_cmd(push_cmd):
        if type(rv) == type(0):
            return(rv)
        else:
            print(rv.decode("utf-8").rstrip())

def main():
    parser = argparse.ArgumentParser(prog='d4', description='D4: Dock to Develop Dynamic Dockerfile')
    parser.add_argument('-v', '--version', action='version', version='%s %s' % ('%(prog)s', VERSION))

    subparsers = parser.add_subparsers(title='subcommands')

    init_subparser = subparsers.add_parser('init', description='initialize project')
    init_subparser.add_argument('project_name', metavar='PROJECT', help='project name')
    init_subparser.set_defaults(func="init_project")

    build_subparser = subparsers.add_parser('build', description='build image with project resources')
    build_subparser.set_defaults(func="build")

    test_subparser = subparsers.add_parser('test', description='test image with project resources')
    test_subparser.set_defaults(func="test")

    test_subparser = subparsers.add_parser('develop', description='build and test image with project resources')
    test_subparser.set_defaults(func="develop")

    login_subparser = subparsers.add_parser('login', description='login registry server')
    login_subparser.add_argument('-u','--user', required=True, help='registry user name')
    login_subparser.add_argument('-p','--password', required=True, help='registry password')
    login_subparser.set_defaults(func="login")

    push_subparser = subparsers.add_parser('push', description='push image managed project')
    push_subparser.set_defaults(func="push")

    release_subparser = subparsers.add_parser('release', description='release image to registry')
    release_subparser.add_argument('-u','--user', help='registry user name')
    release_subparser.add_argument('-p','--password', help='registry password')
    release_subparser.set_defaults(func="release")

    args = parser.parse_args()
    if hasattr(args, "func"):
        if args.func == "init_project":
            init_project(args.project_name)
            return 0
        elif args.func == "build":
            rc = build()
            return rc
        elif args.func == "test":
            rc = test()
            return rc
        elif args.func == "develop":
            rc_build = build()
            rc_test = test()
            rc = 0 if (rc_build + rc_test) == 0 else 1
            return rc
        elif args.func == "login":
            rc = login(args.user,args.password)
            return rc
        elif args.func == "push":
            rc = push()
            return rc
        elif args.func == "release":
            if (args.user is not None) != (args.password is not None):
                print("ERROR: both -u and -p options are required together")
                return 1
            else:
                rc_build = build()
                rc_test = test()
                rc_login = 0
                if (args.user is not None) and (args.password is not None):
                    rc_login = login(args.user, args.password)
                rc_push = push()
                rc = 0 if (rc_build + rc_test + rc_login + rc_push) == 0 else 1
                return rc
    else:
      parser.print_help()

