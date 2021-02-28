"""
File:           db.py
Author:         Dibyaranjan Sathua
Created on:     20/02/21, 1:49 am
"""
from typing import Optional
import re
from collections import defaultdict
from sqlalchemy import create_engine
from config import DBCred


class DBApi:
    """ Class responsible for db operatons """
    __instance = None
    DB_URL = f"mysql+pymysql://{DBCred.USERNAME}:{DBCred.PASSWORD}@{DBCred.HOST}/{DBCred.DBNAME}"

    @classmethod
    def get_instance(cls):
        """ Return DBApi instance """
        if cls.__instance is None:
            cls.__instance = DBApi()
        return cls.__instance

    def __init__(self):
        self._engine = create_engine(DBApi.DB_URL)
        self._conn = self._engine.connect()
        self._potential_records = None
        self._filters = None

    def __del__(self):
        self._conn.close()

    def get_all_potential_records(self):
        """ Get all potential deals data """
        query = "SELECT * FROM vw_Deal ORDER BY PotentialDealID DESC"
        self._potential_records = [dict(row) for row in self._conn.execute(query).fetchall()]

    def get_potential_deal_columns(self):
        """ Get potential deal column name """
        query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'vw_Deal' " \
                "ORDER BY ORDINAL_POSITION"
        return [x[0] for x in self._conn.execute(query).fetchall()]

    def get_unique_years(self, potential_records: Optional[dict] = None):
        """ Extract year and no of vehicle in that year """
        if potential_records is None:
            potential_records = self.get_all_potential_records()
        make_model_year_col = [record["make_model_year"] for record in potential_records]
        years = defaultdict(int)
        year_regex = re.compile(r"^\s*(\d+)")
        for value in make_model_year_col:
            match_obj = year_regex.search(value)
            if match_obj is not None:
                years[match_obj.group(1)] += 1
        # List of tuple [(year, no of vehicles)]
        years = sorted(years.items(), reverse=True)
        return years

    def get_all_make_models(self):
        """ Get all the rows for make_model columns """
        query = "SELECT * FROM vauto_make_model"
        make_model_records = [dict(row) for row in self._conn.execute(query).fetchall()]
        make_model = defaultdict(list)
        for record in make_model_records:
            make_model[record["make"]].append(record["model"])
        return make_model

    def save_actions_comments(self, records):
        """ Save action and comments to db """
        # records is a list of dict with id, Action and Comment
        if len(records) == 1:
            query = f"UPDATE PotentialDeal SET Action = {records[0]['Action']}, " \
                    f"Comment = '{records[0]['Comment']}' " \
                    f"WHERE PotentialDealID = {records[0]['PotentialDealID']}"
        else:
            # Reference: https://tableplus.com/blog/2018/11/how-to-update-multiple-rows-at-once-in-mysql.html
            sub_query = ""
            first_record = records.pop(0)
            for record in records:
                sub_query += f"UNION ALL SELECT {record['PotentialDealID']}, '{record['Action']}', " \
                             f"'{record['Comment']}'\n"
            query = f"""
            UPDATE PotentialDeal pd 
            JOIN (
            SELECT {first_record['PotentialDealID']} as id, 
            '{first_record['Action']}' as new_action, 
            '{first_record['Comment']}' as new_comment 
            {sub_query}
            ) vals ON pd.PotentialDealID = vals.id
            SET Action = new_action, Comment = new_comment
            """
        transcation = self._conn.begin()
        self._conn.execute(query)
        transcation.commit()

    def save_filter(self, name, year, make, model, min_odometer, max_odometer, min_price, max_price,
                    min_offer_price, max_offer_price):
        """ Save the filter for future use """
        query = f"""
        INSERT INTO Filters(name, year, make, model, min_odometer, max_odometer, min_price, 
        max_price, min_offer_price, max_offer_price)
        VALUES ('{name}', '{year}', '{make}', '{model}', '{min_odometer}', '{max_odometer}', 
        '{min_price}', '{max_price}', '{min_offer_price}', '{max_offer_price}')
        """
        transcation = self._conn.begin()
        self._conn.execute(query)
        transcation.commit()

    def get_all_filters(self):
        """ Get all the rows for filters """
        query = "SELECT * FROM Filters"
        self._filters = [dict(row) for row in self._conn.execute(query).fetchall()]

    @property
    def potential_records(self):
        if self._potential_records is None:
            print("Getting data from db")
            self.get_all_potential_records()
        print("Returning data from cache")
        return self._potential_records

    @property
    def filters(self):
        if self._filters is None:
            self.get_all_filters()
        return self._filters


if __name__ == "__main__":
    db_api = DBApi()
    # List of sqlalchemy.engine.result.RowProxy
    results = db_api.get_all_potential_records()
    years = db_api.get_unique_years()
    make_models = db_api.get_all_make_models()
    columns = db_api.get_potential_deal_columns()
    import pdb; pdb.set_trace()
    print(results)
