from ftplib import FTP
import zipfile
import xmltodict
from isk17mssql import PostgreSQLSession
import pandas as pd
from tqdm import tqdm


def main():
    session = PostgreSQLSession(
        server="localhost",
        db="zakupki",
        user="postgres",
        password="password",
        port='5432'
    )

    FTP_ADDRESS = 'ftp.zakupki.gov.ru'
    USER = 'fz223free'
    PASSWORD = 'fz223free'

    PURCHASE_CONTRACT = "purchaseContract" + "/" + "daily"
    ZIP_PURCHASE_NAME = "contract.zip"

    NOTICE = "http://zakupki.gov.ru/223fz/purchase/1:purchaseContract"
    BODY = "http://zakupki.gov.ru/223fz/purchase/1:body"
    ITEM = "http://zakupki.gov.ru/223fz/purchase/1:item"
    PURCHASE_DATA = "http://zakupki.gov.ru/223fz/purchase/1:purchaseContractData"

    TENDER_REGISTRATION_NUMBER = "http://zakupki.gov.ru/223fz/purchase/1:registrationNumber"
    CONTRACT_CREATE_DATE = "http://zakupki.gov.ru/223fz/purchase/1:contractCreateDate"

    SUPPLIER = "http://zakupki.gov.ru/223fz/purchase/1:supplier"
    SUPPLIER_MAIN_INFO = "http://zakupki.gov.ru/223fz/types/1:mainInfo"
    SUPPLIER_NAME = "http://zakupki.gov.ru/223fz/types/1:name"
    SUPPLIER_INN = "http://zakupki.gov.ru/223fz/types/1:inn"
    SUPPLIER_KPP = "http://zakupki.gov.ru/223fz/types/1:kpp"
    SUPPLIER_OGRN = "http://zakupki.gov.ru/223fz/types/1:ogrn"

    with FTP(FTP_ADDRESS, user=USER, passwd=PASSWORD) as ftp:
        ftp.cwd("/out/published/")
        for region in ftp.nlst()[:5]:
            ftp.cwd(region)
            ftp.cwd(PURCHASE_CONTRACT)
            for xml_zip in tqdm(ftp.nlst()[::-1]):
                try:
                    with open(ZIP_PURCHASE_NAME, mode="wb") as f:
                        ftp.retrbinary("RETR " + xml_zip, f.write)

                    with zipfile.ZipFile(ZIP_PURCHASE_NAME) as archive:
                        for part in archive.namelist():
                            xml_data = archive.read(part)
                            contract = xmltodict.parse(xml_data, process_namespaces=True)[NOTICE][BODY][ITEM][PURCHASE_DATA]
                            supplier = contract[SUPPLIER][SUPPLIER_MAIN_INFO]
                            contract_dict = {
                                "tender_registration_number": contract[TENDER_REGISTRATION_NUMBER][:-3],
                                "create_date": contract[CONTRACT_CREATE_DATE],
                                "name": supplier[SUPPLIER_NAME],
                                "inn": supplier[SUPPLIER_INN],
                                "kpp": supplier[SUPPLIER_KPP],
                                "ogrn": supplier[SUPPLIER_OGRN]
                            }
                            contract_row = pd.DataFrame([contract_dict])
                            session.df_to_db(contract_row, "public.winners", if_exists="append")
                except:
                    continue
            ftp.cwd('../../../')
        ftp.quit()
        session.con.close()


if __name__ == "__main__":
    main()
