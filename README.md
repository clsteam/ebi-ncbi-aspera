# Use aspera to download data from EBI or NCBI at high speed

```python

[@login ~]$ python3 main.py --h
usage: download.py [-h] [--project PROJECT] [--key KEY] [--ncbi] [--save]
                   [--exclude EXCLUDE] [--include INCLUDE]

optional arguments:
  -h, --help         show this help message and exit
  --project PROJECT  project name, such as PRJNA320473
  --key KEY          private-key file name (id_rsa) of aspera
  --ncbi             download form NCBI database, default EBI
  --save             whether save url file, default ./ftp_url.json
  --exclude EXCLUDE  The downloaded file excludes the following accession, and
                     provide the accession list file
  --include INCLUDE  The downloaded file includes the following accession, and
                     provide the accession list file
```