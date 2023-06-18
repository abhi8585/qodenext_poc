import csv

class CsvClient:
    def __init__(self, file_path=None, sheet_name=None):
        self.file_path = file_path
        self.sheet_name = sheet_name

    def read(self):  
        try:
            with open("/Users/abhisheksharma/code/web/srctrac_backend/app/utils/csv/safexpress_data.csv", 'r') as file:
                reader = csv.DictReader(file)
                data = []
                for row in reader:
                    data.append(row)
                return data
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

# # Example usage:
# config = ConfigClient(env='dev')
# mysql_uri = config.get_value("Database", "uri")
# mysql_client = MySQLClient(mysql_uri)

# csv_reader = CsvReaderClient("instakart_data.csv")
# result = csv_reader.read()
# if result:
#     for row in result:
#         print(row)
