# -*-  encoding:utf-8 -*-
import datetime
import psycopg2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Boolean, Text, DATE

Base = declarative_base()


class AmazonProductData(Base):
    '''
    存储Amazon数据
    '''
    __tablename__ = 'amazon_product'
    id = Column(Integer, comment='amazon_product_id', primary_key=True,autoincrement=True)
    product_id = Column(String(length=100), comment='amazon_id', unique=True, nullable=False)
    product_class = Column(String(length=100), comment="商品大类", nullable=False)
    product_small_class = Column(String(length=100), comment="商品小类", nullable=False)
    product_price = Column(String(length=300), comment='价格', nullable=False)
    product_addr = Column(Text, comment='厂家地址', nullable=False)
    product_title = Column(Text, comment='商品描述', nullable=True)
    product_sale_count = Column(String(length=80), comment='售价', nullable=True)
    product_point = Column(String(length=30),comment='评分', nullable=True)
    product_update_date = Column(DATE, comment="更新时间", default=datetime.datetime.now(), nullable=False)


class AmazonVerifyData(Base):
    '''
    检查状态表
    '''
    __tablename__ = 'amazon_shop'
    id = Column(Integer, comment='amazon_id', primary_key=True, autoincrement=True)
    product_id = Column(String(length=100), comment='amazon_id', unique=True, nullable=False)
    product_class = Column(String(length=100), comment="商品大类", nullable=False)
    product_small_class = Column(String(length=100), comment="商品小类", nullable=False)
    product_page = Column(Integer, comment="获取第几页", nullable=False)
    product_update_date = Column(DATE, default=datetime.datetime.now(), comment='商品更新时间', nullable=False)


def create_database(config):
    '''
    此函数用于创建数据库链接
    :param config:
    :return:
    '''
    database_engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        config.get('database','username'), config.get('database','password'),
        config.get('database', 'host'), config.get('database','port'),
        config.get('database','database_name')), max_overflow=10)

    DBSession = sessionmaker(database_engine)
    print("start")
    # session = DBSession()
    return DBSession, database_engine


def insert_video_shop_info_table(session, meta_data):
    '''
    写入数据库
    :param session: orm 对象
    :param meta_data: 写入数据
    :return: 不返回值
    '''
    if type(meta_data) is list:
        session.add_all(meta_data)
    else:
        session.add(meta_data)
    session.commit()
    session.close()
