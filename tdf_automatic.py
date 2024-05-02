def getTDF():
    import imaplib
    import email
    import os

    user = 'mrodriguezcheroky'
    password = 'ozyl qbah amca yvot'
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    server.login(user, password)
    server.select('inbox')

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

def TDFtoDB(fileNameXLS, conexion):
    import pandas as pd
    print("Importando datos a la DB ...")
    datos_excel = pd.read_html(fileNameXLS)[0]
    datos_excel.columns = datos_excel.iloc[0]
    datos_excel = datos_excel.drop(0)
    retorno = datos_excel.to_sql(name="tdf", con=conexion, if_exists="replace", index=False, index_label="ATM")
    return retorno

def unzipTDF(fileName):
    import zipfile
    print("Descomprimiendo archivo ...")
    with zipfile.ZipFile(fileName,"r") as zip_ref:
        zip_ref.extractall()
    return fileName

def connectDb():
    from sqlalchemy import create_engine
    motor = create_engine('mysql+mysqlconnector://root:Nub3Cosmic4@localhost/tdf_automatic')
    return motor


fileName = getTDF()
unzipTDF(fileName)
filenNameXLS = fileName[0:fileName.index(".")]
filenNameXLS = filenNameXLS + ".xls"
conexion = connectDb()
retorno = TDFtoDB(filenNameXLS, conexion)
print("Cantidad de registros insertados: ",retorno)