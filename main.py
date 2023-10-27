#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import uuid
import argparse

def print_err(msg):
    print("\033[31m%s\033[0m" % msg, file=sys.stderr)

def process_auth_hook(domain, validation, remaining_challenges):
    err_code = 0
    hook_args = "HOOK_DOMAIN={} HOOK_VALIDATION={} HOOK_REMAINING_CHALLENGES={} HOOK_ALL_DOMAINS={} {}".format(domain, validation, remaining_challenges, all_domains, os.path.abspath(auth_hook))

    result = subprocess.run(hook_args, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    outStr = result.stdout.decode('utf-8').rstrip()
    errStr = result.stderr.decode('utf-8').rstrip()

    if len(outStr) > 0:
        print("Hook '--auth-hook' for %s ran with output:" % domain)
        print(outStr)

    if len(errStr) > 0:
        err_code = 1
        print_err("Hook '--auth-hook' for %s ran with error output:" % domain)
        print_err(errStr)

    return err_code

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth-hook", required=True)
    parser.add_argument("-d", "--domain", action="append", required=True)
    args = parser.parse_args()

    auth_hook = args.auth_hook
    domain_list = args.domain
    all_domains = ",".join(domain_list)
    domain_list2 = all_domains.split(",")
    domain_num = len(domain_list2)

    domain_str = domain_list2[0]
    if domain_num == 2:
        domain_str = "%s and %s" % (domain_list2[0], domain_list2[1])
    if domain_num > 2:
        domain_str = "%s and 2 more domains" % domain_list2[0]
    print("Learning hook process for %s" % domain_str)

    if not os.path.exists(auth_hook):
        print_err("Unable to find auth-hook command %s in the PATH." % auth_hook)
        print_err("(PATH is %s)" % os.getenv("PATH"))
        sys.exit(0)

    if not os.access(auth_hook, os.X_OK):
        print_err("auth-hook command %s exists, but is not executable." % auth_hook)
        sys.exit(0)

    err_total = 0

    for i, domain in enumerate(domain_list2):
        validation = uuid.uuid4()
        remaining_challenges = domain_num - i - 1
        err_total += process_auth_hook(domain, validation, remaining_challenges)

    if err_total == 0:
        print("The result was successful.")
