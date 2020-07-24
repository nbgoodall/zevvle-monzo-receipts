#!/bin/bash
set -eo pipefail

rm -rf package function.zip
pip install --target ./package -r requirements.txt

cd package

zip -r9 ../function.zip .

cd ..

zip -g ./function.zip zevvle_receipts.py