# Errors.py

_errors_list = []
_errors_detected = 0
def error(message, lineno=None):
    global _errors_detected
    global _errors_list
    if lineno:
        print(f'LexerError: {message} in line {lineno}.')
        _errors_list.append(f'LexerError: {message} in line {lineno}.')
    else:
        print(message)
        _errors_list.append(message)
    _errors_detected += 1

def errors_detected():
    return _errors_detected

def errors_list():
    return _errors_list

def clear_errors():
    global _errors_detected
    global _errors_list
    _errors_detected = 0
    _errors_list = []