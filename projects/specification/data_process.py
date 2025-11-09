from tables import TableConfigInventor

from database import DataBase
from data_loader import get_data_from_xl
import os


def load_data_to_db(filepath_xl: str, filepath_db: str) -> None:
    inventor_table_config = TableConfigInventor()

    data_list = get_data_from_xl(filepath=filepath_xl, inventor_table_config=inventor_table_config)
    if data_list:        
        db = DataBase(filepath_db)
        db.create_table(table=inventor_table_config)
        db.fill_table_from_data(table=inventor_table_config, data=data_list)

        list_inv_table = [table_name for table_name in db.get_list_tables() if 'inv' in table_name]


if __name__ == '__main__':
    p_db = os.path.join(os.path.dirname(__file__), 'DEBUG\\ALS.1642.4.2.01.00.00.000 СБ.db')
    p_xl = p = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.4.2.01.00.00.000 СБ - нивентор.xlsx'
    load_data_to_db(filepath_xl=p_xl, filepath_db=p_db)
