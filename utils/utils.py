
# Lib
from typing import Optional

# Site

# Local


# EngravedID characters
EID_FROM_INT = {
    0:  b'\xe2\x80\x80'.decode(),   # " "
    1:  b'\xe2\x80\x81'.decode(),   # " "
    2:  b'\xe2\x80\x82'.decode(),   # " "
    3:  b'\xe2\x80\x83'.decode(),   # " "
    4:  b'\xe2\x80\x84'.decode(),   # " "
    5:  b'\xe2\x80\x85'.decode(),   # " "
    6:  b'\xe2\x80\x86'.decode(),   # " "
    7:  b'\xe2\x80\x87'.decode(),   # " "
    8:  b'\xe2\x80\x88'.decode(),   # " "
    9:  b'\xe2\x80\x89'.decode(),   # " "
    10: b'\xe2\x80\x8b'.decode()    # "​"
}
INT_FROM_EID = {
    b'\xe2\x80\x80'.decode(): 0,    # " "
    b'\xe2\x80\x81'.decode(): 1,    # " "
    b'\xe2\x80\x82'.decode(): 2,    # " "
    b'\xe2\x80\x83'.decode(): 3,    # " "
    b'\xe2\x80\x84'.decode(): 4,    # " "
    b'\xe2\x80\x85'.decode(): 5,    # " "
    b'\xe2\x80\x86'.decode(): 6,    # " "
    b'\xe2\x80\x87'.decode(): 7,    # " "
    b'\xe2\x80\x88'.decode(): 8,    # " "
    b'\xe2\x80\x89'.decode(): 9     # " "
}


def get_engraved_id_from_msg(content: str) -> Optional[int]:
    try:
        if not content.endswith(EID_FROM_INT[10]):
            raise IndexError

        msg_id_block = list(content[-19:])
        msg_id_block.pop()


        engraved_id_parts = list()
        for i in msg_id_block:
            engraved_id_parts.append(str(INT_FROM_EID[i]))

        engraved_id = ''.join(engraved_id_parts)
        engraved_id = int(engraved_id)

    except IndexError:
        return 

    else:
        return engraved_id


def create_engraved_id_from_user(u_id: int) -> Optional[str]:
    engraved_id_parts = list()

    for i in str(u_id):
        engraved_id_parts.append(EID_FROM_INT[int(i)])

    engraved_id_parts.append(EID_FROM_INT[10])
    engraved_id = ''.join(engraved_id_parts)

    return engraved_id
