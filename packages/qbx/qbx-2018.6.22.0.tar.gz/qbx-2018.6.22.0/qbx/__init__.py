import logging
import os
import sys

help_doc = """
usage: qbx [--help] 
           <command> [<args>]

These are some qbx commands:
    auth_wrapper
    register_kong
    register-kong
    register_ws
    watch_git
    watch_git_http
    pull
    haproxy
    uproxy
"""


def print_help():
    print(help_doc)


def run():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    print('argv---', sys.argv)
    if len(sys.argv) == 1:
        print_help()
    else:
        if sys.argv[1] == 'register-kong':
            from .register_kong import register_kong
            register_kong(sys.argv[2:])
        elif sys.argv[1] == 'register_kong':
            logging.warning('use register-kong instead')
            from .register_kong import register_kong
            register_kong(sys.argv[2:])
        elif sys.argv[1] == 'register_ws':
            from .register_ws import register_ws
            register_ws(sys.argv[2:])
        elif sys.argv[1] == 'watch_git':
            from .watchgit import watch_git
            watch_git(sys.argv[2:])
        elif sys.argv[1] == 'watch_git_http':
            from .watchgit import watch_git_http
            watch_git_http(sys.argv[2:])
        elif sys.argv[1] == 'haproxy':
            from .haproxy import haproxy
            haproxy(sys.argv[2:])
        elif sys.argv[1] == 'pull':
            from .pull import pull
            pull(sys.argv[2:])
        elif sys.argv[1] == 'uproxy':
            from .uproxy import uproxy
            uproxy(sys.argv[2:])
        elif sys.argv[1] == 'auth_wrapper':
            from .auth_wrapper import auth_wrapper
            auth_wrapper(sys.argv[2:])
        elif sys.argv[1] == 'kube-start':
            from . import kube_start
            kube_start.start()
        elif sys.argv[1] == 'upload':
            from .upload import upload
            upload(sys.argv[2:])
        else:
            if sys.argv[1] != 'help' and sys.argv[1] != '--help':
                logging.warning('method not regognize')
            print_help()


def qbs():
    print(sys.argv)
    print(os.environ)
    run_cmdline_when_cond(sys.argv[1:])


def run_cmdline_when_cond(cmdline):
    print('cmdline: ', cmdline)
    import subprocess
    import time
    import arrow
    process = subprocess.Popen(cmdline)
    while True:
        if process.poll() is None:
            time.sleep(1)
        else:
            print('program exit itself')
            break
    print('end at', arrow.now(), 'sleep 30s before exit')
    time.sleep(30)


if __name__ == '__main__':
    # from .watchgit import watch_git
    # watch_git(['git+ssh://git@github.com/qbtrade/quantlib.git', 'log_rpc.py'])
    from . import kube_start

    kube_start.start()
