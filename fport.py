import time
import serial

FPORT_FRAME_MARKER = 0x7e
FPORT_ESCAPE_CHAR = 0x7d
FPORT_ESCAPE_MASK = 0x20

def to_hex_str(data) -> str:
    return ' '.join(f'{x:02x}' for x in data)

def to_binary_str(data) -> str:
    return ' '.join(f'{x:02b}' for x in data)

def channels_to_str(channels) -> str:
    return ' '.join(f'{x:04d}' for x in channels)

def get_fport_data(ser: serial.Serial) -> list:
    data = []
    frame_position = 0
    escaped_character = False
    while True:
        val = ser.read()[0]
        if val == FPORT_FRAME_MARKER:
            frame_position = 1
            escaped_character = False
            if len(data) > 0:
                break
        elif frame_position > 0:
            if escaped_character:
                val = val ^ FPORT_ESCAPE_MASK
                escaped_character = False
            elif val == FPORT_ESCAPE_CHAR:
                escaped_character = True
                continue
            data.append(val)
            frame_position += 1
    return data

def get_channels(ser: serial.Serial, adjust_values: bool = True):
    while True:
        data = get_fport_data(ser)
        if data[1] == 0x00:
            break

    data = data[1:]
    channels = [0] * 16
    channels[0] = data[1] | data[2] << 8 & 0x07FF
    channels[1] = data[2] >> 3 | data[3] << 5 & 0x07FF
    channels[2] = data[3] >> 6 | data[4] << 2 | data[5] << 10 & 0x07FF
    channels[3] = data[5] >> 1 | data[6] << 7 & 0x07ff
    channels[4] = data[6] >> 4 | data[7] << 4 & 0x07FF
    channels[5] = data[7] >> 7 | data[8] << 1 | data[9] << 9 & 0x07FF
    channels[6] = data[9] >> 2 | data[10] << 6 & 0x07FF
    channels[7] = data[10] >> 5 | data[11] << 3 & 0x07FF
    channels[8] = data[12] | data[13] << 8 & 0x07FF
    channels[9] = data[13] >> 3 | data[14] << 5 & 0x07FF
    channels[10] = data[14] >> 6 | data[15] << 2 | data[16] << 10 & 0x07FF
    channels[11] = data[16] >> 1 | data[17] << 7 & 0x07FF
    channels[12] = data[17] >> 4 | data[18] << 4 & 0x07FF
    channels[13] = data[18] >> 7 | data[19] << 1 | data[20] << 9 & 0x07FF
    channels[14] = data[20] >> 2 | data[21] << 6 & 0x07FF
    channels[15] = data[21] >> 5 | data[22] << 3 & 0x07FF

    if adjust_values:
        channels = [(5 * ch // 8) + 880 for ch in channels]
    return channels

def get_channel_1(data):
    # return data[2]
    # val = data[2] + ((data[3] & 0b11100000) << 3)
    # val = (data[2] << 3) + ((data[3] & 0b11100000) >> 5)
    val = data[2] | data[3] << 8 & 0x07ff
    return f'{val}'

ser = serial.Serial('/dev/ttyS0', baudrate=115200)

# start_time = time.time()
try:
    while True:
        data = get_channels(ser)
        # hex_str = to_hex_str(data)
        # print('Length:', len(data), 'Sum:', sum(data))
        # print('\r', hex_str, end='')
        # print(get_channel_1(data))
        # print('\r', data[2], end='')
        print('\r', channels_to_str(data), end='')
except KeyboardInterrupt:
    pass
finally:
# end_time = time.time()
    ser.close()
# print('Avg Rate:', 10 / (end_time - start_time))
