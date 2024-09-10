import os
import datetime
import logging
import zipfile
import imaplib
import email
import configparser
import pandas as pd
import gspread
import pytz
from oauth2client.service_account import ServiceAccountCredentials

def unzipTDF(fileName):

    logging.info("Descomprimiendo archivo %s...", fileName)
    with zipfile.ZipFile(fileName, "r") as zip_ref:
        zip_ref.extractall()

    # Check if the file exists before attempting to delete it
    if os.path.exists(fileName):
        os.remove(fileName)
        logging.info(f"The file {fileName} has been deleted.")
    else:
        logging.info(f"The file {fileName} does not exist.")
    filenNameXLS = fileName[0:fileName.index(".")]
    filenNameXLS = filenNameXLS + ".xls"
    return filenNameXLS


def getCredentials():
    config_obj = configparser.ConfigParser()
    #Read config.ini file
    config_obj.read("gmailCredentials.ini")
    credParam = config_obj["gmail"]
    user = credParam["user"]
    password = credParam["password"]
    credentials = (user, password)
    return credentials

def getTDF():

    server = imaplib.IMAP4_SSL('imap.gmail.com')
    server.login(*getCredentials())
    server.select('TDF')

    fileName = ''
    detach_dir = '.'
    # if 'attachments' not in os.listdir(detach_dir):
    #    os.mkdir('attachments')

    logging.info("Iniciando proceso de recupercion de mail ...")

    typ, data = server.search(None, 'UNSEEN SUBJECT "TDF"')
    if data[0]:
        for msgId in data[0].split():
            typ, messageParts = server.fetch(msgId, '(RFC822)')
            emailBody = messageParts[0][1]
            raw_email_string = emailBody.decode('utf-8')
            mail = email.message_from_string(raw_email_string)
            logging.info('emailbody complete ...')
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    # print(part.as_string()) QUITAR?
                    continue
                if part.get('Content-Disposition') is None:
                    # print(part.as_string()) QUITAR?
                    continue
                fileName = part.get_filename()
                logging.info('file names processed ...')
                if bool(fileName):
                    filePath = os.path.join(detach_dir, fileName)
                    if not os.path.isfile(filePath):
                        logging.info("Archivo adjunto: %s",
                                     fileName)  # QUITAR?
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        logging.info('fp closed ...')
    server.close()
    server.logout()
    return fileName


def TDFtoGSheet(fileNameXLS, worksheet):

    logging.info("Importando datos a Google Sheets ...")
    datos_excel = pd.read_html(fileNameXLS)[0]
    datos_excel.columns = datos_excel.iloc[0]
    datos_excel = datos_excel.drop(0)

    file_path = fileNameXLS
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"The file {file_path} has been deleted.")
    else:
        logging.info(f"The file {file_path} does not exist.")

    for i, col in enumerate(datos_excel.columns):
        if i == 0:
            continue
        else:
            datos_excel[col] = datos_excel[col].map(int)
    worksheet.clear()
    worksheet.update([datos_excel.columns.values.tolist()] +
                     datos_excel.values.tolist())
    return datos_excel


def getGSheet(googleSheetId):
    # Define the scope
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive']
    # Define the credentials file path
    creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
    # Authorize the client
    client = gspread.authorize(creds)
    # Open the spreadsheet
    gsheet = client.open_by_key(googleSheetId)
    return gsheet


################### MAIN #################
logging.basicConfig(filename='tdf_automatic.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileName = getTDF()
if fileName:
    filenNameXLS = unzipTDF(fileName)
    gs = getGSheet("16XHtpBjy0jSb8QfHwkRJy86-4h3wNv_YeiQygxYp-R4")
    df = TDFtoGSheet(filenNameXLS, gs.worksheet("TDF"))

    ws = gs.worksheet("SaldosATMs")

    fechaHoraActual = datetime.datetime.now(
        pytz.timezone('America/Argentina/Buenos_Aires'))
    cadena_formato = "%d/%m/%Y %H:%M:%S"
    fecha_hora_str = fechaHoraActual.strftime(cadena_formato)
    ws.update_cell(1, 3, fecha_hora_str)
    ws.update_cell(1, 5, fileName)

    logging.info("Registros insertados!!")
else:
    logging.info("No hay TDF disponible")
