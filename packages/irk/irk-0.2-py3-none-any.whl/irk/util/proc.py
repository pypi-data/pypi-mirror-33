import subprocess
import click
import sys


def run(args, shell=False):
    proc = subprocess.Popen(args, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    all_stdout = ""
    while proc.poll() is None:
        new_content = proc.stdout.read(16)
        all_stdout += new_content
        print(new_content, end="")
    return proc.returncode, all_stdout


def elevate():
    arg_str = ["/usr/bin/env", "sudo", *sys.argv]
    if click.confirm(f"Elevate with {' '.join(arg_str)}?"):
        exit(subprocess.run(arg_str).returncode)
