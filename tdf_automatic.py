import os
import pandas as pd
import os
import gspread
import datetime

def unzipTDF(fileName):
    import zipfile
    
    print("Descomprimiendo archivo ...")
    with zipfile.ZipFile(fileName,"r") as zip_ref:
        zip_ref.extractall()

    # Specify the path of the file to be deleted
    file_path = fileName
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file {file_path} has been deleted.")
    else:
        print(f"The file {file_path} does not exist.")
    filenNameXLS = fileName[0:fileName.index(".")]
    filenNameXLS = filenNameXLS + ".xls"        
    return filenNameXLS

def getTDF():
    import imaplib
    import email

    user = 'mrodriguezcheroky'
    password = 'ozyl qbah amca yvot'
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    server.login(user, password)
    server.select('TDF')

    fileName = ''
    detach_dir = '.'
    #if 'attachments' not in os.listdir(detach_dir):
    #    os.mkdir('attachments')

    print("Iniciando proceso de recupercion de mail ...")
        
    typ, data = server.search(None, 'UNSEEN SUBJECT "TDF"')
    if data[0]:
        for msgId in data[0].split():
            typ, messageParts = server.fetch(msgId, '(RFC822)')
            emailBody = messageParts[0][1]
            raw_email_string = emailBody.decode('utf-8')
            mail = email.message_from_string(raw_email_string)#
            print('emailbody complete ...')
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    #print(part.as_string()) QUITAR?
                    continue
                if part.get('Content-Disposition') is None:
                    #print(part.as_string()) QUITAR?
                    continue
                fileName = part.get_filename()
                print('file names processed ...')
                if bool(fileName):
                    filePath = os.path.join(detach_dir, fileName)
                    if not os.path.isfile(filePath):
                        print("Archivo adjunto: ", fileName) # QUITAR?
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        print('fp closed ...')
    server.close()
    server.logout()
    return fileName

def TDFtoGSheet(fileNameXLS, worksheet):

    print("Importando datos a Google Sheets ...")
    datos_excel = pd.read_html(fileNameXLS)[0]
    datos_excel.columns = datos_excel.iloc[0]
    datos_excel = datos_excel.drop(0)

    file_path = fileNameXLS
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file {file_path} has been deleted.")
    else:
        print(f"The file {file_path} does not exist.")

    for i, col in enumerate(datos_excel.columns):
        if i == 0 :
            continue
        else :
            datos_excel[col] = datos_excel[col].map(int)
    worksheet.clear()
    worksheet.update([datos_excel.columns.values.tolist()] + datos_excel.values.tolist())
    return datos_excel

def getGSheet(googleSheetId):
    from oauth2client.service_account import ServiceAccountCredentials

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

fileName = getTDF()
if fileName :
    filenNameXLS = unzipTDF(fileName)
    gs = getGSheet("16XHtpBjy0jSb8QfHwkRJy86-4h3wNv_YeiQygxYp-R4")
    df = TDFtoGSheet(filenNameXLS, gs.worksheet("TDF"))

    ws = gs.worksheet("SaldosATMs")
    fechaHoraActual = datetime.datetime.now()
    cadena_formato = "%d/%m/%Y %H:%M:%S"
    fecha_hora_str = fechaHoraActual.strftime(cadena_formato)
    ws.update_cell(1, 3, fecha_hora_str)

    print("Registros insertados!!")
else:
    print("No hay TDF disponible")