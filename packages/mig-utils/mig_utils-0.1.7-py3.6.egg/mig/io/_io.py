import fs
import six
import socket
from abc import ABCMeta, abstractmethod
from fs.errors import ResourceNotFound
from ssh2.session import Session
from ssh2.sftp import LIBSSH2_FXF_READ, LIBSSH2_FXF_WRITE, LIBSSH2_FXF_CREAT, \
    LIBSSH2_SFTP_S_IRUSR, LIBSSH2_SFTP_S_IWUSR, LIBSSH2_SFTP_S_IRGRP, \
    LIBSSH2_SFTP_S_IROTH, LIBSSH2_FXF_APPEND


@six.add_metaclass(ABCMeta)
class DataStore():
    _client = None

    def __init__(self, client):
        """
        :param client:
        This is the sshfs client instance,
        that is used to access the datastore
        """
        self._client = client

    @abstractmethod
    def open(self, path, flag='r'):
        pass

    @abstractmethod
    def list(self, path):
        pass

    @abstractmethod
    def remove(self, path):
        pass

    @abstractmethod
    def close(self):
        pass


@six.add_metaclass(ABCMeta)
class FileHandle():

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def close(self):
        pass


class SSHFSStore(DataStore):

    def __init__(self, host=None, username=None, password=None):
        assert host is not None
        assert username is not None
        assert password is not None
        client = fs.open_fs(
            "ssh://" + username + ":" + password + host)
        super(SSHFSStore, self).__init__(client)

    def geturl(self, path):
        return self._client.geturl(path)

    def open(self, path, flag='r'):
        """
        Used to get a python filehandler object
        :param path:
        the name of the file to be opened
        :param flag:
        which mode should the file be opened in
        :return:
        a _io.TextIOWrapper object with utf-8 encoding
        """
        return self._client.open(six.text_type(path), flag)

    def list(self, path='.'):
        """
        :param path:
        file system path which items will be returned
        :return:
        A list of items in the path.
        There is no distinction between files and dirs
        """
        return self._client._sftp.listdir(six.text_type(path))

    def read(self, path):
        """
        :param file:
        File to be read
        :return:
        a string of the content within file
        """
        with self._client.open(six.text_type(path)) as open_file:
            return open_file.read()

    def write(self, path, data, flag='a'):
        """
        :param path:
        path to the file being written
        :param data: data to being written
        :param flag: write flag, defaults to append
        :return:
        """
        with self.open(six.text_type(path), flag) as fh:
            fh.write(data)

    def remove(self, path):
        """
        :param path:
        path to the file that should be removed
        :return:
        Bool, whether a file was removed or not
        """
        try:
            self._client.remove(six.text_type(path))
            return True
        except ResourceNotFound:
            return False

    def list_attr(self, path='.'):
        """
        :param path:
        directory path to be listed
        :return:
        A list of .SFTPAttributes objects
        """
        return self._client._sftp.listdir_attr(six.text_type(path))

    def read_binary(self, path):
        """
        :param path:
        File to be read
        :return:
        a binary of the content within file
        """
        with self._client.openbin(six.text_type(path)) as open_file:
            return open_file.read()

    def removedir(self, path):
        """
        :param path:
        path the dir that should be removed
        :return:
        Bool, whether a dir was removed or not
        """
        try:
            self._client.removedir(six.text_type(path))
            return True
        except ResourceNotFound:
            return False

    def close(self):
        self._client.close()


class SFTPFileHandle(FileHandle):

    def __init__(self, fh, name, flag):
        """
        :param fh: Expects a PySFTPHandle
        """
        self.fh = fh
        self.name = name
        self.flag = flag

    def __iter__(self):
        return self

    def __next__(self):
        return self.read()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Close the passed PySFTPHandles
        :return:
        """
        self.fh.close()

    def read(self, n=-1):
        """
        :param n: amount of bytes to be read, defaults to the entire file
        :return: the content of path, decoded to utf-8 string
        """
        assert 'r' in self.flag
        if 'b' in self.flag:
            return self.read_binary(n)
        else:
            result = self.read_binary(n).decode('utf-8')
            return result

    def write(self, data):
        """
        :param path: path to the file that should be created/written to
        :param data: data that should be written to the file, expects binary or str
        :param flag: write mode
        :return:
        """
        assert 'w' in self.flag or 'a' in self.flag
        if type(data) == bytes:
            self.fh.write(data)
        elif type(data) == str:
            self.fh.write(six.b(data))
        else:
            self.fh.write(six.b(str(data)))

    def seek(self, offset):
        """ Seek file to a given offset
        :param offset: amount of bytes to skip
        :return: None
        """
        self.fh.seek64(offset)

    def read_binary(self, n=-1):
        """
        :param n: amount of bytes to be read
        :return: a binary string of the content within in file
        """
        data = []
        if n != -1:
            # 1, because pysftphandle returns an array -> 1 = data
            data.append(self.fh.read(n)[1])
        else:
            for size, chunk in self.fh:
                data.append(chunk)
        return b"".join(data)

    def tell(self):
        """ Get the current file handle offset
        :return: int
        """
        return self.fh.tell64()


class SFTPStore(DataStore):

    def __init__(self, host=None, username=None, password=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, 22))
        s = Session()
        s.handshake(sock)
        s.userauth_password(username, password)
        s.open_session()
        client = s.sftp_init()
        super(SFTPStore, self).__init__(client=client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self, path, flag='r'):
        """
        :param path: path to file on the sftp end
        :param flag: open mode, either 'r'=read, 'w'=write, 'a'=append
        'rb'=read binary, 'wb'=write binary or 'ab'= append binary
        :return: SFTPHandle, https://github.com/ParallelSSH/ssh2-python
        /blob/master/ssh2/sftp_handle.pyx
        """
        if flag == 'r' or flag == 'rb':
            fh = self._client.open(six.text_type(path), LIBSSH2_FXF_READ,
                                   LIBSSH2_SFTP_S_IWUSR)
        else:
            w_flags = None
            if flag == 'w' or flag == 'wb':
                w_flags = LIBSSH2_FXF_CREAT | LIBSSH2_FXF_WRITE
            elif flag == 'a' or flag == 'ab':
                w_flags = LIBSSH2_FXF_CREAT | LIBSSH2_FXF_WRITE | LIBSSH2_FXF_APPEND
            mode = LIBSSH2_SFTP_S_IRUSR | LIBSSH2_SFTP_S_IWUSR | LIBSSH2_SFTP_S_IRGRP |\
                LIBSSH2_SFTP_S_IROTH
            fh = self._client.open(six.text_type(path), w_flags, mode)
        assert fh is not None
        handle = SFTPFileHandle(fh, path, flag)
        return handle

    def list(self, path='.'):
        """
        :param path: path to the directory which content should be listed
        :return: list of str, of items in the path directory
        """
        with self._client.opendir(six.text_type(path)) as fh:
            return [name.decode('utf-8') for size, name, attrs in fh.readdir()]

    def remove(self, path):
        """
        :param path: path to the file that should be removed
        """
        self._client.unlink(six.text_type(path))

    def close(self):
        self._client = None


class ERDA:
    url = "io.erda.dk"


class IDMC:
    url = "io.idmc.dk"


class ERDASftpShare(SFTPStore):

    def __init__(self, username=None, password=None):
        super(ERDASftpShare, self).__init__(ERDA.url, username, password)


# TODO -> cleanup duplication
class ERDASSHFSShare(SSHFSStore):

    def __init__(self, share_link):
        """
        :param share_link:
        This is the sharelink ID that is used to access the datastore,
        an overview over your sharelinks can be found at
        https://erda.dk/wsgi-bin/sharelink.py.
        """
        host = "@" + ERDA.url + "/"
        super(ERDASSHFSShare, self).__init__(host=host, username=share_link,
                                             password=share_link)


class ERDAShare(ERDASftpShare):

    def __init__(self, share_link):
        """
        :param share_link:
        This is the sharelink ID that is used to access the datastore,
        an overview over your sharelinks can be found at
        https://erda.dk/wsgi-bin/sharelink.py.
        """
        super(ERDAShare, self).__init__(share_link, share_link)


# TODO -> cleanup duplication
class IDMCSSHFSShare(SSHFSStore):

    def __init__(self, share_link):
        """
        :param share_link:
        This is the sharelink ID that is used to access the datastore,
        an overview over your sharelinks can be found at,
        https://erda.dk/wsgi-bin/sharelink.py.
        """
        host = "@" + IDMC.url + "/"
        super(IDMCSSHFSShare, self).__init__(host=host, username=share_link,
                                             password=share_link)


class IDMCSftpShare(SFTPStore):

    def __init__(self, username=None, password=None):
        super(IDMCSftpShare, self).__init__(IDMC.url, username, password)


class IDMCShare(IDMCSftpShare):

    def __init__(self, share_link):
        super(IDMCShare, self).__init__(share_link, share_link)

# class ErdaHome(DataStore):
#     _target = ERDA.url
#
#     # TODO -> switch over to checking the OPENID session instead of username/password
#     def __init__(self, username, password):
#         """
#         :param username:
#         The username to the users ERDA home directory,
#         as can be found at https://erda.dk/wsgi-bin/settings.py?topic=sftp
#         :param password:
#         Same as user but the speficied password instead
#         """
#         client = SSHFS(ErdaHome._target, user=username, passwd=password)
#         super(ErdaHome, self).__init__(client=client)
