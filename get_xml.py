import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import *
import time

def get_treasury_curve():

    start_time = time.time()
    url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202502"
    response = requests.get(url)
    xml_content = response.text
    soup = BeautifulSoup(xml_content, "xml")
    entries = soup.find_all("entry")

    data = []
    data_limite = datetime.strptime("2025-02-10", "%Y-%m-%d")

    for entry in entries:
        properties = entry.find("m:properties")
        
        if properties:
            row_data = {}
            for field in properties.find_all():
                tag_name = field.name.split(":")[-1]
                row_data[tag_name] = field.text.strip()

            data.append(row_data)

    df = pd.DataFrame(data)
    df = df.drop(columns=['Id'])
    df = df.melt(id_vars=["NEW_DATE"], var_name="term", value_name="value")
    df["code"] = "treasury_" + df["term"].str.replace(" ", "_").str.lower()
    df["term"] = "NULL"
    df.rename(columns={"NEW_DATE": "date"}, inplace=True)
    df = df[["code", "date", "term", "value"]]
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= data_limite]
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    df['code'] = df['code'].str.replace("month", "m")
    df['code'] = df['code'].str.replace("year", "y")

    df.to_csv("treasury_yield_curve.csv", index=False)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Tempo de execução: {execution_time:.4f} segundos.")

get_treasury_curve()