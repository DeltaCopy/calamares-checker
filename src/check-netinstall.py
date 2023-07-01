#!/usr/bin/env python

# This script verifies whether a package defined inside a Calamares netinstall yaml file, can be installed by Pacman

import logging
import argparse
import os
import sys
import pathlib
import subprocess

logger = logging.getLogger("logger")

logger.setLevel(logging.INFO)


# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s > %(message)s", "%Y-%m-%d %H:%M:%S"
)
# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def main():
    parser = argparse.ArgumentParser(
        description="Verify Calamares netinstall packages."
    )
    parser.add_argument("-p", "--path")

    args = parser.parse_args()

    if args.path is not None:
        path = args.path
        path = os.path.expanduser(path)

        if os.path.exists(path):
            results = process_files(path, get_pacman_output())

            if len(results) > 0:
                print(
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                )
                logger.info("Displaying results")
                print(
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                )

                for file in results:
                    if len(results[file]) > 0:
                        for pkg in results[file]:
                            get_package_info(pkg, file)

        else:
            logger.error("Path '%s' does not exist" % path)
            sys.exit(1)


def get_package_info(package, yaml_file):
    logger.info("Searching for package '%s'" % package)
    pacman_package_search = ["pacman", "-Ss", package]
    logger.info("Yaml file = %s" % yaml_file)
    output = []
    with subprocess.Popen(
        pacman_package_search,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    ) as process:
        for line in process.stdout:
            if "/" in line:
                output.append(line)

    if len(output) > 0:
        for line in output:
            print("- %s" % line.strip())

    else:
        logger.error("Package not found")

    print("=========================================================================")


def get_pacman_output():
    pacman_sync_info = ["pacman", "-Si"]
    pacman_sync_group = ["pacman", "-Sg"]
    output = []

    with subprocess.Popen(
        pacman_sync_info,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    ) as process:
        for line in process.stdout:
            if "Name            :" in line:
                output.append(line.replace(" ", "").split("Name:")[1].strip())

    with subprocess.Popen(
        pacman_sync_group,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    ) as process:
        for line in process.stdout:
            output.append(line.strip())

    return output


def process_files(path, output):
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.info("Path = %s" % path)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    results = {}
    for file in os.listdir(path):
        if "netinstall-" in file and file.endswith(".yaml"):
            filename = os.path.join(path, file)
            logger.info("Verifying file %s" % file)
            if len(filename) > 0:
                with open(filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                packages = []

                invalid_packages = []
                for line in lines:
                    if line.startswith("    - "):
                        package_name = line.split("    - ")[1]
                        packages.append(package_name.strip())

                if len(packages) > 0:
                    for package in packages:
                        if package not in output:
                            invalid_packages.append(package)

                    results[file] = invalid_packages

    return results


if __name__ == "__main__":
    main()
