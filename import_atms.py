def connectDb():
    from sqlalchemy import create_engine
    motor = create_engine('mysql+mysqlconnector://root:xxxxxx@localhost/tdf_automatic')
    return motor

import pandas as pd
print("Importando datos de ATMs a la DB ...")
datos_excel = pd.read_excel("ATMsOperativosMacro.xlsx")
retorno = datos_excel.to_sql(name="atms", con=connectDb(), if_exists="replace", index=False, index_label="ATM")
print(retorno)