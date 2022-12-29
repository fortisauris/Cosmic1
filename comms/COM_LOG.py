import time
def log_init():
    try:
        f = open(file='com.log', mode='r', encoding='ascii')
        f.close()
    except FileNotFoundError:
        f = open(file='com.log', mode='w', encoding='ascii')
        f.write(f'LOG INIT START AT {str(time.time())} \n')
        f.close
        return



def write_on_send(raw_msg: tuple):
    '''
    Function saves message to log.
    :param msg: (time, system, receive or send, msg) tuple
    :return: Bool
    '''
    log_init()
    with open(file='com.log', mode='a', encoding='ascii') as f:
        msg = prepare_msg(raw_msg)
        f.write(msg)
    return True

def prepare_msg(msg):
    return f'AT: {msg[0]} SYSTEM: {msg[1]} \t {msg[2]}, MESSAGE: {msg[3]} \n'