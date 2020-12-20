from ftplib import FTP
import zipfile
import xmltodict
from isk17mssql import PostgreSQLSession
import pandas as pd
import xml
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

    PURCHASE_NOTICE = "purchaseNotice" + "/" + "daily"
    ZIP_PURCHASE_NAME = "purchase.zip"

    NOTICE = "http://zakupki.gov.ru/223fz/purchase/1:purchaseNotice"
    BODY = "http://zakupki.gov.ru/223fz/purchase/1:body"
    ITEM = "http://zakupki.gov.ru/223fz/purchase/1:item"
    PURCHASE_DATA = "http://zakupki.gov.ru/223fz/purchase/1:purchaseNoticeData"

    TENDER_CREATEDATE = "http://zakupki.gov.ru/223fz/purchase/1:createDateTime"
    TENDER_REGISTRATION_NUMBER = "http://zakupki.gov.ru/223fz/purchase/1:registrationNumber"
    TENDER_NAME = "http://zakupki.gov.ru/223fz/purchase/1:name"

    CUSTOMER = "http://zakupki.gov.ru/223fz/purchase/1:customer"
    CUSTOMER_MAIN_INFO = "http://zakupki.gov.ru/223fz/types/1:mainInfo"
    CUSTOMER_SHORT_NAME = "http://zakupki.gov.ru/223fz/types/1:shortName"
    CUSTOMER_INN = "http://zakupki.gov.ru/223fz/types/1:inn"
    CUSTOMER_KPP = "http://zakupki.gov.ru/223fz/types/1:kpp"
    CUSTOMER_OGRN = "http://zakupki.gov.ru/223fz/types/1:ogrn"
    CUSTOMER_LEGAL_ADDRESS = "http://zakupki.gov.ru/223fz/types/1:legalAddress"

    with FTP(FTP_ADDRESS, user=USER, passwd=PASSWORD) as ftp:
        ftp.cwd("/out/published/")
        for region in tqdm(ftp.nlst()[:5]):
            ftp.cwd(region)
            ftp.cwd(PURCHASE_NOTICE)
            for xml_zip in tqdm(ftp.nlst()[::-1], leave=False):
                try:
                    with open(ZIP_PURCHASE_NAME, mode="wb") as f:
                        ftp.retrbinary("RETR " + xml_zip, f.write)

                    with zipfile.ZipFile(ZIP_PURCHASE_NAME) as archive:
                        for part in archive.namelist():
                            xml_data = archive.read(part)
                            tender = xmltodict.parse(xml_data, process_namespaces=True)[NOTICE][BODY][ITEM][PURCHASE_DATA]
                            tender_dict = {
                                "registration_number": tender[TENDER_REGISTRATION_NUMBER],
                                "create_date": tender[TENDER_CREATEDATE],
                                "name": tender[TENDER_NAME]
                            }
                            customer = tender[CUSTOMER][CUSTOMER_MAIN_INFO]
                            customer_dict = {
                                "tender_registration_number": tender[TENDER_REGISTRATION_NUMBER],
                                "short_name": customer[CUSTOMER_SHORT_NAME],
                                "inn": customer[CUSTOMER_INN],
                                "kpp": customer[CUSTOMER_KPP],
                                "ogrn": customer[CUSTOMER_OGRN],
                                "legal_address": customer[CUSTOMER_LEGAL_ADDRESS]
                            }
                            tender_row = pd.DataFrame([tender_dict])
                            session.df_to_db(tender_row, "public.tenders", if_exists="append")
                            customer_row = pd.DataFrame([customer_dict])
                            session.df_to_db(customer_row, "public.customers", if_exists="append")
                except:
                    continue
            ftp.cwd('../../../')
        ftp.quit()
        session.con.close()


if __name__ == "__main__":
    main()
