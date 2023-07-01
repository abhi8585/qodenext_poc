
import pandas as pd


class XlsxClient:
    def __init__(self, file_path=None, sheet_name=None):
        self.file_path = file_path
        self.sheet_name = sheet_name

    def convert_df(self, data_frame):
        rows = data_frame.to_dict(orient='records')
        return rows

    def read(self,cols_list=None):  
        try:
            if cols_list is not None:
                excel_data_df = pd.read_excel(self.file_path, self.sheet_name, usecols=cols_list)
            else:
                excel_data_df = pd.read_excel(self.file_path, self.sheet_name)
            excel_data_df = excel_data_df.drop(excel_data_df.index[-1])
            df = self.convert_df(excel_data_df)
            return df
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")