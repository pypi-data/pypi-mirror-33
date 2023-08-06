import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import CONFIG
import datetime
import pytz



class DB:
    def __init__(self, user_name, password, host, dbname):
        self.dbname = dbname
        self.user_name =user_name
        self.password = password
        self.host = host

        self.base_con = psycopg2.connect(
            dbname='postgres',
            user=user_name,
            host=host,
            password=password)
        self.base_con.autocommit = True

        try:
            self.con = psycopg2.connect(
                dbname=dbname,
                user=user_name,
                host=host,
                password=password)
            self.cur = self.con.cursor()
            self.con.autocommit = True
        except psycopg2.OperationalError:
            pass

        self.base_cur = self.base_con.cursor()

    def create_db(self):
        self.base_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            self.base_cur.execute("CREATE DATABASE {}".format(self.dbname))
            self.con = psycopg2.connect(
                dbname=self.dbname,
                user=self.user_name,
                host=self.host,
                password=self.password)
            self.cur = self.con.cursor()
            self.con.autocommit = True
        except psycopg2.OperationalError:
            pass

    def create_table_users_payouts(self):
        self.cur.execute("""
                      CREATE TABLE IF NOT EXISTS users_payouts (
                      address VARCHAR(50) PRIMARY KEY,
                      payout BIGINT,
                      last_payout_blockchain_timestamp BIGINT,
                      unixt TIMESTAMP);
                      """)
        self.con.commit

    def store_payout(self, address, share, timestamp, network):
        unixt = pytz.utc.localize(datetime.datetime.fromtimestamp(CONFIG[network]["epoch"] + timestamp))

        self.cur.execute(
            """
            INSERT
            INTO
            users_payouts(address, payout, last_payout_blockchain_timestamp, unixt)
            VALUES('{address}', {payout}, {timestamp}, (TIMESTAMP '{unixt}'))
            ON CONFLICT(address)
            DO UPDATE
            SET
                payout = {payout},
                last_payout_blockchain_timestamp = {timestamp},
                unixt = (TIMESTAMP '{unixt}')
            WHERE users_payouts.address = '{address}' ;   
            """.format(
                address=address,
                payout=share,
                timestamp=timestamp,
                unixt=unixt,
            )
        )