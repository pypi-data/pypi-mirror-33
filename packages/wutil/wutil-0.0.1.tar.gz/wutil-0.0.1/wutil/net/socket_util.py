import struct


def sendall(sock, msg):
    """ Send message over socket.

    Parameters
    ----------
    sock : ``socket``
        socket with open connection.
    msg : ``bytes``
        message to send.

    """
    message_size = len(msg)
    message_size_packed = struct.pack('i', message_size)
    sock.send(message_size_packed)
    sock.sendall(msg)


def recvall(sock):
    """ Receive message over socket. Sender should use :obj:`sendall` function.

    Parameters
    ----------
    sock : ``socket``
        socket with open connection.

    Returns
    -------
    b : ``bytes``
        received data

    """
    response_size_b = sock.recv(4)
    response_size = struct.unpack('i', response_size_b)[0]
    data = recvbytes(sock, response_size)
    return data


def recvbytes(sock, msg_size, buff_size=4096):
    data = b''
    while len(data) < msg_size:
        part = sock.recv(buff_size)
        data += part
    return data
