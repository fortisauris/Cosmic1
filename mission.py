from comms.config import COMMS

MISSION_STATUS = 'PREPARATION'
# COMMS


if __name__ == '__main__':
    if MISSION_STATUS == 'EMERGENCY' and COMMS is False:
        print('WARNING - COMMS ARE FALLBACK TO EMERGENCY Morse_HEX Simplex Radio !!!')


