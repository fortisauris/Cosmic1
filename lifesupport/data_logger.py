import time
from constructor import power, modules, doors, crew_members


def sensor_log_init():
    f = open(file='sensors_log.txt', mode='w', encoding='utf8')
    msg = 'LIFE SUPPORT SYSTEMS ONLINE  ' + str(time.time()) + '\nBEGIN LOG \n'
    msg = msg + 'SPACESHIP: ' + power.name + '\n'
    msg = msg + 'Raw weight: {:.2f}'.format(power.m_weight) + 't \t' + 'Total weight: {:.2f}'.format(power.t_weight) + 't\n'
    f.write(msg)
    f.close()
    return


def sensor_log_append():

    with open(file='sensors_log.txt', mode='a', encoding='utf8') as f:
        msg = "__________________________________" + '\n'
        for i in range(len(modules)):
                msg = msg + 'Module no.' + str(i) + '  ' + modules[i].name + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(0)) + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(1)) + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(2)) + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(3)) + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(4)) + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(5)) + ', '
                msg = msg + '{:.2f}'.format(modules[i].air_sensors(6)) + ', '
                if modules[i].fire_sensors():
                    msg = msg + "FAC status: FIRE !!!" + '\n'
                else:
                    msg = msg + "FAC status: OK" + '\n'
        for l in doors:
            msg = msg + 'Door no.' + str(l.door_id) + ' ' + l.belongs_to + '/' + l.adjacent_to + ' -> ' + \
            str(l.status) + ', ' + str(l.connection_status) + '\n'
        f.write(msg)
    return


def prepare_msg(msg):
    return f'AT: {msg[0]} SYSTEM: {msg[1]} \t {msg[2]}, MESSAGE: {msg[3]} \n'
