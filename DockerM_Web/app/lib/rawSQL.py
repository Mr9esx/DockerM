# -*- coding:utf-8 -*-
import MySQLdb
class rawSQLControl(object):
    def __init__(self):
        self.__db = MySQLdb.connect(host='localhost',user='root',passwd='asdasd',db='dockerm',port=3306)

    def insert(self, sql):
        cur = self.__db.cursor()
        cur.execute(sql)
        self.__db.commit()
        cur.close()
        self.__db.close()

    def select(self, sql):
        cur = self.__db.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        result = cur.fetchmany(cur.execute(sql))
        cur.close()
        self.__db.close()
        return result

    def getContainerState(self, container_id, limit=360):
        result = self.select(("select id,container_id,cpu_percent,memory_usage,memory_limit,memory_percent,tx_packets,tx_bytes,tx_dropped,tx_errors,tx_speed,rx_packets,rx_bytes,rx_dropped,rx_errors,rx_speed,unix_timestamp(collect_time) as collect_time from container_state WHERE container_id='{}' group by unix_timestamp(collect_time)-unix_timestamp(collect_time) % 60 ORDER BY collect_time DESC LIMIT 0,{};").format(container_id,limit))
        return result