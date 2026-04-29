import sys

def error_message_detail(error, error_detail: sys):
    """
    Extracts detailed error information from the Python runtime environment.
    """
    # exc_info() returns (type, value, traceback). We only need the traceback.
    _, _, exc_tb = error_detail.exc_info()
    
    # Extract the file name and line number where the error occurred
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    
    # Format a highly readable error string
    error_message = "Error occurred in python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name, line_number, str(error)
    )
    
    return error_message

class CustomException(Exception):
    """
    Custom exception class to handle and format errors cleanly.
    """
    def __init__(self, error_message, error_detail: sys):
        # Call the base Exception class
        super().__init__(error_message)
        
        # Override the error message with our highly detailed custom format
        self.error_message = error_message_detail(error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message