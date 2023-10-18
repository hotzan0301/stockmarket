import csv
import boto3
import pandas as pd
import numpy as np
from io import BytesIO
import pymysql
from sqlalchemy.sql import text
import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

S3BUCKET = 'YOUR_S3_BUCKET_NAME'
SUMMARYCSVFILES = ['PATH_YOUR_CSV_FILES_IN_S3',]

HOST = 'HOST_NAME'
USER = 'USER_NAME'
PASSWORD = 'YOUR PASSWORD'

# Read CSV files and returns a dataframe
def getSummariesDataFrame():
    s3 = boto3.client('s3')
    combined_df = pd.DataFrame()
    for file in SUMMARYCSVFILES:
        response  = s3.get_object(Bucket=S3BUCKET, Key=file)
        content = response['Body'].read()
        df = pd.read_csv(BytesIO(content))
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

# Converts a string value to a float value
# If a value is nan then store a NULL value
def convertToFloatOrNull(list):

    try:
        price = float(list[0])
    except:
        price = 'NULL'

    try:
        marketCap = list[1]
        if marketCap[-1] == 'B':
            newValue = float(marketCap.replace("B",""))
            newValue = newValue * 1000000000
            marketCap = newValue
        elif marketCap[-1] == 'T':
            newValue = float(marketCap.replace("T",""))
            newValue = newValue * 1000000000000
            marketCap = newValue
        else:
            marketCap = float(marketCap)

    except:
        marketCap = 'NULL'

    try:
        beta = float(list[2])
    except:
        beta = 'NULL'

    try:
        peRatio = float(list[3])
    except:
        peRatio = 'NULL'

    try:
        eps = float(list[4])
    except:
        eps = 'NULL'

    return price, marketCap, beta, peRatio, eps

def writeSummariesToDatabase():
    try:

        engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}")
        print("MYSQL SERVER CONNECTED")

        engine.execute("USE stockmarket")

        createTableSql = """
        CREATE TABLE IF NOT EXISTS summary(
        summary_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
        date DATE NOT NULL,
        company_id INT NOT NULL,
        company_ticker VARCHAR(50) NOT NULL,
        price NUMERIC(10,3),
        market_cap NUMERIC(20),
        beta NUMERIC(10,3),
        pe_ratio NUMERIC(10,3),
        eps NUMERIC(10,3),
        FOREIGN KEY (company_id) REFERENCES company(company_id));
        """
        engine.execute(createTableSql)
        print("TABLE summary CREATED OR ALREADY EXISTS")

        db_config = {
            'host': HOST,
            'user': USER,
            'password': PASSWORD,
            'database': 'stockmarket',
        }

        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        today = datetime.date.today().strftime("%Y-%m-%d")
        df = getSummariesDataFrame()
        df.fillna(value='NULL', inplace=True)
        for index, row in df.iterrows():
            ticker = row['ticker']
            query = f"SELECT company_id FROM company WHERE company_ticker = '{ticker}'"
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                companyId = result[0]
                price, marketCap, beta, peRatio, eps = convertToFloatOrNull([row['price'], row['marketCap'], row['beta'], row['peRatio'], row['eps']])
                query = f"SELECT * FROM summary WHERE company_id = {companyId} AND date = '{today}'"
                cursor.execute(query)
                existing_summary = cursor.fetchone()
                if existing_summary:
                    update_query = f"""
                        UPDATE summary
                        SET
                            price = {price},
                            market_cap = {marketCap},
                            beta = {beta},
                            pe_ratio = {peRatio},
                            eps = {eps}
                        WHERE
                            company_id = {companyId}
                        AND
                            date = '{today}'
                    """
                    cursor.execute(update_query)
                else:
                    insert_query = f"""
                        INSERT INTO summary (date, company_id, company_ticker, price, market_cap, beta, pe_ratio, eps)
                        VALUES ('{today}', {companyId}, '{ticker}', {price}, {marketCap}, {beta}, {peRatio}, {eps})
                    """
                    cursor.execute(insert_query)
        conn.commit()
    except Exception as e:
        print("Error ocurred", str(e))

