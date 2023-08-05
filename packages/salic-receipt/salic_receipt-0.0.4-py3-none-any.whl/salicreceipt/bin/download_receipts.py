import os
import re
import csv
import sys
import click
import pickle
import requests

from salicreceipt.paths import RECEIPTS_CSV_PATH, RECEIPTS_PICKLE_PATH


def get_id_arquivos():
    id_arquivos = get_id_arquivos_from_pickle()

    return id_arquivos


def get_id_arquivos_from_csv():
    with open(RECEIPTS_CSV_PATH, 'r') as csv_data_file:
        csv_reader = csv.reader(csv_data_file)

        id_arquivos = [row[10] for row in csv_reader]

    return id_arquivos[1:]


def get_id_arquivos_from_pickle():
    id_arquivos = []

    if os.path.isfile(RECEIPTS_PICKLE_PATH):
        with open(RECEIPTS_PICKLE_PATH, 'rb') as receipts_pickle_file:
            id_arquivos = pickle.load(receipts_pickle_file)

    return id_arquivos


def save_id_arquivos_on_pickle(id_arquivos):
    os.makedirs(os.path.dirname(RECEIPTS_PICKLE_PATH), exist_ok=True)

    with open(RECEIPTS_PICKLE_PATH, 'wb') as receipts_pickle_file:
        pickle.dump(id_arquivos, receipts_pickle_file, pickle.HIGHEST_PROTOCOL)


def download_receipt_file(id_arquivo, receipt_file_folder):
    DOWNLOAD_LINK = 'http://salic.cultura.gov.br/verprojetos/abrir?id={}'

    url = DOWNLOAD_LINK.format(id_arquivo)

    response = requests.get(url)
    content_disposition = response.headers['content-disposition']

    receipt_content = response.content
    receipt_file_name = re.findall('filename="(.+)"', content_disposition)[0]
    receipt_file_path = os.path.join(receipt_file_folder, receipt_file_name)

    with open(receipt_file_path, 'wb') as receipt_file:
        receipt_file.write(receipt_content)


def print_download_percentage(downloaded_receipts, len_receipts):
    progress = int(50 * downloaded_receipts / len_receipts)
    fill_progress = '=' * progress
    empty_progress = ' ' * (50 - progress)
    percentage_progress = (downloaded_receipts * 100 / len_receipts)

    message = "\r[%s%s] %d / %d  [%d%%]" % (
        fill_progress,
        empty_progress,
        downloaded_receipts,
        len_receipts,
        percentage_progress
    )

    sys.stdout.write(message)
    sys.stdout.flush()

@click.command()
@click.argument('output_folder', type = str)
@click.argument('limit', type = int)
@click.argument('offset', type = int, default = 0)
def download_receipt_files(limit, offset, output_folder):
    downloaded_receipts = 0
    id_arquivos = get_id_arquivos()[offset:offset+limit]
    len_receipts = len(id_arquivos)

    print_download_percentage(downloaded_receipts, len_receipts)

    os.makedirs(output_folder, exist_ok=True)

    for id_arquivo in id_arquivos:
        download_receipt_file(id_arquivo, output_folder)

        downloaded_receipts += 1
        print_download_percentage(downloaded_receipts, len_receipts)

    print("")
    print("Download completed!")


def main():
    download_receipt_files()


if __name__ == '__main__':
    main()
