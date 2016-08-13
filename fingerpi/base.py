
### Considering getting rid of duplicates

def _fp_command(val):
    __fp_command = {
        'Open': 0x01,
        'Close': 0x02,
        
    }

def _fp_response(val):
    __response_key = {
        'ACK': 0x30,
        'NACK': 0x31
    }
    # __response_val = {
    #     0x30: 'ACK',
    #     0x31: 'NACK'
    # }

    if type(val) == str:
        return __response_key.get(val, None)
    # elif type(val) == int:      
    #     return __response_val.get(val, None)
    else:
        raise TypeError("Input should be of type 'str' or 'int'!")
    
