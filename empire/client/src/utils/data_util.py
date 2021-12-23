import base64

def get_data_from_file(file_path: str):
    """
    Get data from file and base64 encode it
    """
    if file_path:
        with open(file_path, 'rb') as stream:
            file_data = stream.read()

        data = base64.b64encode(file_data).decode('utf-8')
        return data
