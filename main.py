#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author  : Yao

""" Title

This file(script) can also be imported as a module and contains the following
functions:

    * main - the main function of the script
    * function - returns the column headers of the file
"""

# Standard library
import os
import glob
import requests
import json
import argparse
import subprocess

# Third party library

# Private module

message = """
Your private-key file name (id_rsa) of aspera:
    {key}
"""


def main():
    # arguments passed
    parser = argparse.ArgumentParser()

    # optional
    parser.add_argument("--project", help="project name, such as PRJNA320473")
    parser.add_argument("--sra", help="list file of sra name")
    parser.add_argument("--key", help="private-key file name (id_rsa) of aspera", default="~/.aspera/connect/etc/asperaweb_id_dsa.openssh")
    parser.add_argument("--ncbi", help="download form NCBI database, default EBI", action='store_true')
    # parser.add_argument("--ncbi", help="download form NCBI database", action='store_true')
    parser.add_argument("--save", help="whether save url file, default ./ftp_url.json[useful for --project]", action='store_true')
    parser.add_argument("--exclude", help="The downloaded file excludes the following accession, and provide the accession list file")
    parser.add_argument("--include",help="The downloaded file includes the following accession, and provide the accession list file")

    args = parser.parse_args()

    print(message.format(key=args.key), flush=True)

    if args.ncbi:
        # NCBI
        print("Sorry, this option is not currently supported.", flush=True)
        quit()

    if args.sra:
        with open(args.sra, "r") as handle:
            for line in handle:
                accession = line.strip().split(".", 1)[0]
                url = "https://www.ebi.ac.uk/ena/portal/api/filereport?accession={accession}&result=read_run&fields=study_accession,sample_accession,experiment_accession,run_accession,tax_id,scientific_name,fastq_ftp,submitted_ftp,sra_ftp&format=json&download=true".format(
                    accession=accession)
                download(url, args)
    elif args.project:
        url = "https://www.ebi.ac.uk/ena/portal/api/filereport?accession={accession}&result=read_run&fields=study_accession,sample_accession,experiment_accession,run_accession,tax_id,scientific_name,fastq_ftp,submitted_ftp,sra_ftp&format=json&download=true".format(
            accession=args.project)
        download(url, args)
    else:
        print("parameters of project or sra need one at least.")
        quit()



def download(url, args):
    if args.exclude:
        with open(args.exclude, "r") as handle:
            exclude = [x.strip() for x in handle.readlines()]
    else:
        exclude = []
    if args.include:
        with open(args.include, "r") as handle:
            include = [x.strip() for x in handle.readlines()]

    for ftp_url in require_download_ftp_url(url, save=args.save):
        ftp_suffix = ftp_url.split("/", 1)[1]
        file_name = os.path.basename(ftp_url)
        accession = file_name.split(".")[0].split("_")[0]
        # include, exclude
        if "include" not in locals():
            include = [accession]
        if accession in exclude or accession not in include:
            continue
        cmd = "ascp -QT -l 300m -P33001 -i {key} era-fasp@fasp.sra.ebi.ac.uk:/{ftp_suffix} .".format(key=args.key, ftp_suffix=ftp_suffix)
        print("download {0}...".format(file_name), flush=True)
        subprocess.call(cmd, shell=True)


def require_download_ftp_url(url: str, save=False, ftp_key="fastq_ftp") -> iter:
    class ResponseException(Exception):
        pass
    save_file = "ftp_url.json"
    if os.path.exists(save_file):
        print(" ftp_url uses the '{0}' in the current folder by default, delete this file to retrieve the latest ftp_url".format("ftp_url.json"), flush=True)
        for item in json.load(open(save_file), encoding='utf-8'):
            for url in item.get(ftp_key).split(";"):
                yield url
    response = requests.get(url)
    if response.status_code == 200:
        print("The ftp link has been successfully obtained!", flush=True)
        result = json.loads(response.content.decode('utf-8'), encoding='utf-8')
        if save:
            with open(save_file, "w") as handle:
                json.dump(result, handle)
        for item in result:
            for url in item.get(ftp_key).split(";"):
                yield url
        return result
    else:
        raise ResponseException("code={0}".format(response.status_code))


if __name__ == '__main__':
    main()