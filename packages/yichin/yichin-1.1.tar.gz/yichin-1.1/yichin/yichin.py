# yichin.py
from datetime import timezone
from datetime import datetime as yichin_time
from datetime import timedelta as yichin_timedelta
from binascii import hexlify as yichin_hex
from binascii import unhexlify as yichin_unhex

YICHIN_NUMBER = 8288
YICHIN_ENCODE = "utf-8"
YICHIN_STRING = "yichin"
YICHIN_FORMAT = "%Y%m%d%H%M%S%z"
YICHIN_TIMEZONE = timezone.utc
YICHIN_TIMENUMBER = 8237

yichin_chr = lambda x: chr(x)
yichin_int = lambda x, y: int(x, y)
yichin_now = lambda x: yichin_time.now(x)
yichin_str = lambda x, y: str(x, y)
yichin_join = lambda x: ''.join(x)
yichin_bytes = lambda x, y: bytes(x, y)
yichin_split = lambda x, y, z: x.split(y)[z]
yichin_strip = lambda x, y: x.strip(y)

class YichinException(Exception): pass

def encode(yichins, days=0, hours=0, minutes=0, seconds=0):
    if type(yichins) != str or type(days) != int or type(hours) != int or type(minutes) != int or type(seconds) != int: raise YichinException('first args must be string, others must be int')
    if days < 0 or hours < 0 or minutes < 0 or seconds < 0: raise YichinException('time must be positive numbers')
    if days + hours + minutes + seconds == 0: return yichin_join([YICHIN_STRING[:3]] + [yichin_chr(yichin_int(yichin, 16) + YICHIN_NUMBER) for yichin in yichin_str(yichin_hex(yichin_bytes(yichins, YICHIN_ENCODE)), YICHIN_ENCODE)] + [YICHIN_STRING[3:]])
    else: return yichin_join([yichin_chr(YICHIN_TIMENUMBER)] + [YICHIN_STRING[:3]] + [yichin_chr(yichin_int(yichin, 16) + YICHIN_NUMBER) for yichin in yichin_str(yichin_hex(yichin_bytes(yichins, YICHIN_ENCODE)), YICHIN_ENCODE)] + [yichin_chr(YICHIN_TIMENUMBER)] + [yichin_chr(yichin_int(yichin, 16) + YICHIN_NUMBER) for yichin in yichin_str(yichin_hex(yichin_bytes((yichin_now(YICHIN_TIMEZONE) + yichin_timedelta(days=days, hours=hours, minutes=minutes)).strftime(YICHIN_FORMAT), YICHIN_ENCODE)), YICHIN_ENCODE)] + [YICHIN_STRING[3:]] + [yichin_chr(YICHIN_TIMENUMBER)])

def decode(yichins):
    if yichins[0] == yichin_chr(YICHIN_TIMENUMBER) and yichins[-1] == yichin_chr(YICHIN_TIMENUMBER):
        if yichin_now(YICHIN_TIMEZONE) <= yichin_time.strptime(yichin_str(yichin_unhex(yichin_join([hex(ord(yichin) - YICHIN_NUMBER)[2:] for yichin in yichin_split(yichin_strip(yichins[1:-1], YICHIN_STRING), yichin_chr(YICHIN_TIMENUMBER), -1)])), YICHIN_ENCODE), YICHIN_FORMAT):
            return yichin_str(yichin_unhex(yichin_join([hex(ord(yichin) - YICHIN_NUMBER)[2:] for yichin in yichin_split(yichin_strip(yichins[1:-1], YICHIN_STRING), yichin_chr(YICHIN_TIMENUMBER), 0)])), YICHIN_ENCODE)
        else: raise YichinException('You\'re out of time to see this message.')
    else: return yichin_str(yichin_unhex(yichin_join([hex(ord(yichin) - YICHIN_NUMBER)[2:] for yichin in yichin_strip(yichins, YICHIN_STRING)])), YICHIN_ENCODE)
