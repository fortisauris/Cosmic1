'''
Cosmic1  will be equipped with High Tech COM hardware and use modern protocols to transfer
Audio and video.
If Emergency occurs will be fallback to traditional low energy, low tech Simplex  Radio
communication with Morse Code via terminal in hexadecimal codes 00-ff.

!!! WARNING RUN THRU TERMINAL PROGRAM NOT PYCHARM !!!

# SCIENCE
## NASA  DTN Disruption Tolerant Networking - small relay satellites BUFFERS CODES AS DATA
## Deep Space Network - Laser Communications Relay - Infrared Laser Com
'''
import time
from COM_LOG import *



Morse = {
    "A": '.-', "B": '-...', "C": '-.-.', "D": '-..', "E": '.', "F": '..-.',
    "0": '-----', "1":'.----', "2":'..---', "3": '...--', "4": '....-',
    "5": '.....', "6": '-....', "7": '--...', "8": '---..', "9": '----.'
}

class MorseHexEncoder(object):
    '''
    Nudzova komunikacia pomocou hexadecimalnych kodov dat a errorov pomocou morseovej abecedy.
    Pocitac moze automaticky v pripade zlyhania systemov vymienat data pomocou kodov ci jednoduchej
    komunikacie.
    '''
    def __init__(self, msg: str):
        self.msg = msg.upper()
        if self.check_msg() is True:
            self.encode()

            # connect RADIO
            write_on_send(raw_msg=(str(time.time()), 'EMERGENCY_MHEX', 'SEND2EARTH', self.msg ))
            print('MSG SEND')
        else:
            print('NOT HEXADECIMAL MESSAGE - NOT SEND')


    def check_msg(self):
        '''
        Metoda kontroluje ci obsahom spravy su len znaky 0123456789ABCDEF
        :return: Bool
        '''
        for i in self.msg:
            if i not in '0123456789ABCDEF':
                return False
        return True

    def encode(self):
        encoded = ''
        for digit in self.msg:
            encoded += Morse[digit]+' '
        print(encoded)
        return encoded


if __name__ == '__main__':
    print('WARNING CHANNEL 16 IS USED ONLY IN EMERGENCY CASE HEAVY ENERGY OR COMS FAILURE. PRESS CTRL-C TO'
          'SEND MESSAGE TO EARTH.:')
    while True:
        try:
            print('WAITING ON CHANNEL 16')
            time.sleep(60)
        except KeyboardInterrupt:
            msg = input('MESSAGE HEXCODE TO EARTH :')
            obj = MorseHexEncoder(msg=msg)
        finally:
            pass
