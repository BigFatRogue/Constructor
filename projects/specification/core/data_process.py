from projects.specification.config.table_config import TableConfigInventor

from projects.specification.core.database import DataBase
from projects.specification.core.data_loader import get_data_from_xl
import os


def load_data_to_db(database: DataBase, filepath_xl: str, filepath_db: str) -> TableConfigInventor:
    inventor_table_config = TableConfigInventor()

    # data_list = get_data_from_xl(filepath=filepath_xl, inventor_table_config=inventor_table_config)
    # if data_list:        
    #     database.create_table(table=inventor_table_config)
    #     database.fill_table_from_data(table=inventor_table_config, data=data_list)

        # list_inv_table = [table_name for table_name in database.get_list_tables() if 'inv' in table_name]
    
    print(inventor_table_config)

if __name__ == '__main__':
    p_db = os.path.join(os.path.dirname(__file__), 'DEBUG\\ALS.1642.4.2.01.00.00.000 СБ.spec')
    p_xl = os.path.join(os.path.dirname(__file__), 'DEBUG\\ALS.1648.8.2.01.Из инвентора.xlsx')

    db = DataBase()
    db.set_path(p_db)
    db.connect()

    load_data_to_db(database=db, filepath_xl=p_xl, filepath_db=p_db)
