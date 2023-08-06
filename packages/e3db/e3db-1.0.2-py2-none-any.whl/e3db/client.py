from auth import E3DBAuth
from crypto import Crypto
from config import Config
from types import ClientDetails, ClientInfo, IncomingSharingPolicy, OutgoingSharingPolicy, Meta, QueryResult, Query, Record, GrantedAuthorizerPolicy, ProxyAuthorizerPolicy
from exceptions import APIError, LookupError, CryptoError, QueryError, ConflictError
import requests
import uuid

class Client:
    """
    Client to perform E3DB operations with.

    The client is able to read, write, query, and many other methods to
    interact with data being stored and retrieved from E3DB.
    """
    DEFAULT_QUERY_COUNT = 100
    DEFAULT_API_URL = "https://api.e3db.com"

    def __init__(self, config):
        """
        Initialize the Client class.

        Parameters
        ----------
        config : dict
            JSON-style dictionary with config elements.

        Returns
        -------
        None
        """
        self.api_url = config['api_url']
        self.api_key_id = config['api_key_id']
        self.api_secret = config['api_secret']
        self.client_id = config['client_id']
        self.client_email = config['client_email']
        self.public_key = config['public_key']
        self.private_key = config['private_key']
        self.e3db_auth = E3DBAuth(self.api_key_id, self.api_secret, self.api_url)
        self.ak_cache = {}

    @classmethod
    def __response_check(self, response):
        """
        Raises errors based on response HTTP status code.

        Parameters
        ----------
        response : requests.models.Response
            Response object to get status code from.

        Returns
        -------
        None
        """

        # Map of HTTP error codes to exception messages
        errors = {
            400: APIError('Invalid request: HTTP 400'),
            401: APIError('Unauthenticated: HTTP 401'),
            403: APIError('Unauthorized: HTTP 403'),
            404: APIError('Requested item not found: HTTP 404'),
            409: ConflictError('Existing item cannot be modified: HTTP 409')
        }

        # Lookup type of error we should throw, and do so if needed.
        if response.status_code in errors:
            raise errors[response.status_code]

    def __decrypt_record(self, record):
        """
        Private method for record decryption setup.

        Obtains the ak needed to decrypt the data, as well as calling
        `__decrypt_record_with_key` to decrypt each individual field.

        Parameters
        ----------
        record : e3db.Record
            Encrypted record

        Returns
        -------
        e3db.Record
            Decrypted record
        """

        meta = record.to_json()['meta']
        writer_id = meta['writer_id']
        user_id = meta['user_id']
        record_type = meta['type']
        ak = self.__get_access_key(writer_id, user_id, self.client_id, record_type)
        return self.__decrypt_record_with_key(record, ak)

    def __decrypt_record_with_key(self, record, ak):
        """
        Private method for decryption of record fields.

        Parameters
        ----------
        record : e3db.Record
            Encrypted record

        ak : str
            Access Key

        Returns
        -------
        e3db.Record
            Decrypted record
        """

        encrypted_record = record.to_json()

        for key, value in encrypted_record['data'].iteritems():
            fields = value.split(".")

            if len(fields) != 4:
                raise CryptoError("Invalid Encrypted record fields: {0}".format(value))

            edk = Crypto.base64decode(fields[0])
            edkN = Crypto.base64decode(fields[1])
            ef = Crypto.base64decode(fields[2])
            efN = Crypto.base64decode(fields[3])

            dk = Crypto.decrypt_secret(ak, edk, edkN)
            pv = Crypto.decrypt_secret(dk, ef, efN)

            encrypted_record['data'][key] = pv
        # return new Record object data with plaintext data
        return Record(Meta(encrypted_record['meta']), encrypted_record['data'])

    def __encrypt_record(self, plaintext_record):
        """
        Private method for encryption of record fields.

        Parameters
        ----------
        plaintext_record : e3db.Record
            Plaintext record

        Returns
        -------
        e3db.Record
            Encrypted record
        """

        record = plaintext_record.to_json()
        data = record['data']
        meta = record['meta']
        writer_id = meta['writer_id']
        user_id = meta['user_id']
        record_type = meta['type']

        # make copy of original record so we can modify it without altering
        # the original record
        new_meta = Meta(meta)
        record = Record(meta=new_meta, data=data).to_json()

        ak = self.__get_access_key(writer_id, user_id, self.client_id, record_type)

        # if the ak is missing, we need to create and push one to the server.
        if ak is None:
            ak = Crypto.random_key()
            self.__put_access_key(writer_id, user_id, self.client_id, record_type, ak)

        # Loop through the plaintext fields and encrypt them
        for key, value in record['data'].iteritems():
            dk = Crypto.random_key()
            efN = Crypto.random_nonce()
            ef = Crypto.encrypt_secret(dk, str(value), efN)
            # remove nonce from ciphertext
            ef = ef[len(efN):]
            edkN = Crypto.random_nonce()
            edk = Crypto.encrypt_secret(ak, dk, edkN)
            # remove nonce from ciphertext
            edk = edk[len(edkN):]

            record['data'][key] = ".".join([Crypto.base64encode(c) for c in [edk, edkN, ef, efN]])

        # return new Record object data with encrypted data
        return Record(Meta(meta), record['data'])

    def __decrypt_eak(self, eak_json):
        """
        Private method for decryption of an encrypted access key.

        Parameters
        ----------
        eak_json : dict
            json-style body returned from the API

        Returns
        -------
        str
            ak
        """

        k = eak_json['authorizer_public_key']['curve25519']
        authorizer_pubkey = Crypto.decode_public_key(k)
        fields = eak_json['eak'].split('.')
        if len(fields) != 2:
            raise CryptoError("Invalid access key format: {0}".format(eak_json['eak']))
        ciphertext = Crypto.base64decode(fields[0])
        nonce = Crypto.base64decode(fields[1])
        return Crypto.decrypt_eak(Crypto.decode_private_key(self.private_key), authorizer_pubkey, ciphertext, nonce)

    def __get_access_key(self, writer_id, user_id, reader_id, record_type):
        """
        Private method to obtain an access key.

        Parameters
        ----------
        writer_id : str
            uuid of the writer

        user_id : str
            uuid of the user

        reader_id : str
            uuid of the reader

        record_type: str
            type of the record to be stored

        Returns
        -------
        str
            ak
        """

        ak_cache_key = (writer_id, user_id, record_type)
        if ak_cache_key in self.ak_cache:
            return self.ak_cache[ak_cache_key]

        url = self.__get_url("v1", "storage", "access_keys", str(writer_id), str(user_id), str(reader_id), record_type)
        response = requests.get(url=url, auth=self.e3db_auth)
        # return None if eak not found, otherwise return eak
        if response.status_code == 404:
            return None
        else:
            self.__response_check(response)
            json = response.json()
            ak = self.__decrypt_eak(json)
            self.ak_cache[ak_cache_key] = ak
            return ak

    def __put_access_key(self, writer_id, user_id, reader_id, record_type, ak):
        """
        Private method to put an access key on the server.

        Parameters
        ----------
        writer_id : str
            uuid of the writer

        user_id : str
            uuid of the user

        reader_id : str
            uuid of the reader

        record_type: str
            type of the record to be stored

        ak: str
            access key

        Returns
        -------
        None
        """

        ak_cache_key = (writer_id, user_id, record_type)
        self.ak_cache[ak_cache_key] = ak

        reader_key = self.__client_key(reader_id)
        nonce = Crypto.random_nonce()
        eak = Crypto.encrypt_ak(Crypto.decode_private_key(self.private_key), reader_key, ak, nonce)
        # Need to strip the nonce off the front of the eak
        eak = eak[len(nonce):]
        encoded_eak = "{0}.{1}".format(Crypto.base64encode(eak), Crypto.base64encode(nonce))
        url = self.__get_url("v1", "storage", "access_keys", str(writer_id), str(user_id), str(reader_id), record_type)
        json = {
            'eak': encoded_eak
        }
        response = requests.put(url=url, json=json, auth=self.e3db_auth)
        self.__response_check(response)

    def __delete_access_key(self, writer_id, user_id, reader_id, record_type):
        """
        Private method to delete an access key on the server.

        Parameters
        ----------
        writer_id : str
            uuid of the writer

        user_id : str
            uuid of the user

        reader_id : str
            uuid of the reader

        record_type: str
            type of the record to be stored

        Returns
        -------
        None
        """

        url = self.__get_url("v1", "storage", "access_keys", str(writer_id), str(user_id), str(reader_id), record_type)
        requests.delete(url=url, auth=self.e3db_auth)

        ak_cache_key = (writer_id, user_id, record_type)
        del self.ak_cache[ak_cache_key]

    def __get_url(self, *args):
        """
        Private method to build an api url path.

        Parameters
        ----------
        *args : list
            list of url path strings

        Returns
        -------
        str
            Full api url with path
        """

        # list of paths that we make a nice url from
        return self.api_url + '/' + '/'.join(args)

    def __put_policy(self, user_id, writer_id, reader_id, record_type, policy):
        """
        Private method to delete an access key on the server.

        Parameters
        ----------
        user_id : str
            uuid of the user

        writer_id : str
            uuid of the writer

        reader_id : str
            uuid of the reader

        record_type: str
            type of the record to be stored

        policy: dict
            policy object to be stored

        Returns
        -------
        None
        """

        policy = dict(policy)
        url = self.__get_url("v1", "storage", "policy", str(user_id), str(writer_id), str(reader_id), record_type)

        response = requests.put(url=url, json=policy, auth=self.e3db_auth)
        self.__response_check(response)

    def outgoing_sharing(self):
        """
        Public Method to obtain outgoing sharing policies.

        This shows records, and clients that you have shared record types with.

        Parameters
        ----------
        None

        Returns
        -------
        list
            List of e3db.OutgoingSharingPolicy documents
        """

        url = self.__get_url("v1", "storage", "policy", "outgoing")
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        # create list of policy objects, and return them
        policies = []
        # check if there are no policies
        if response.json():
            for policy in response.json():
                policies.append(OutgoingSharingPolicy(policy))
        return policies

    def incoming_sharing(self):
        """
        Public Method to obtain incoming sharing policies.

        This shows records, and clients that have shared record types with you.

        Parameters
        ----------
        None

        Returns
        -------
        list
            List of e3db.IncomingSharingPolicy documents
        """

        url = self.__get_url("v1", "storage", "policy", "incoming")
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        # create list of policy objects, and return them
        policies = []
        # check if there are no policies
        if response.json():
            for policy in response.json():
                policies.append(IncomingSharingPolicy(policy))
        return policies

    @classmethod
    def register(self, registration_token, client_name, public_key, private_key=None, backup=False, api_url=DEFAULT_API_URL):
        """
        Public Method to register a client with the server.

        The server will return api key credentials, and a client id for the
        newly created client.

        Parameters
        ----------
        registration_token : str
            Token obtained from InnoVault console used for dynamic registration

        client_name : str
            Name of client to be registered with the InnoVault console

        public_key : str
            base64urlencoded public_key object obtained from
            e3db.Client.generate_keypair()

        private_key : str
            base64urlencoded public_key object obtained from
            e3db.Client.generate_keypair(). Optional. Included in client
            backup record for later key recovery in the InnoVault console,
            if desired.

        backup : bool
            Whether to backup client credentials to the InnoVault console.
            Optional.

        api_url : str
            API url useful for testing against different e3db instances.
            Optional.

        Returns
        -------
        e3db.ClientDetails
            Contains API credentials, a unique client_id generated by the
            server, client name, and client public key.
        """

        url = "{0}/{1}/{2}/{3}/{4}/{5}".format(api_url, 'v1', 'account', 'e3db', 'clients', 'register')
        payload = {
            'token': registration_token,
            'client': {
                'name': client_name,
                'public_key': {
                    'curve25519': public_key
                }
            }
        }
        response = requests.post(url=url, json=payload)
        self.__response_check(response)
        client_info = response.json()
        backup_client_id = response.headers['x-backup-client']

        if backup:
            if private_key is None:
                raise RuntimeError("Cannot back up client credentials without a private key!")

            config = Config(
                client_info['client_id'],
                client_info['api_key_id'],
                client_info['api_secret'],
                public_key,
                private_key,
                api_url=api_url
            )

            client = Client(config())
            client.backup(backup_client_id, registration_token)

        # make ClientDetails object
        return ClientDetails(client_info)

    @classmethod
    def generate_keypair(self):
        """
        Public Method to generate a public and private keypair.

        Used for dynamic registration where the SDK generates its own keys
        and gives the server the public key to generate a client.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            (public_key, private_key) tuple. Keys are Base64URLencoded strings
            of bytes.
        """

        public_key, private_key = Crypto.generate_keypair()
        return Crypto.encode_public_key(public_key), Crypto.encode_private_key(private_key)

    def client_info(self, client_id):
        """
        Public Method to retrieve client info from the server based on client id.

        Parameters
        ----------
        client_id : str
            UUID of the client to lookup info for

        Returns
        -------
        e3db.ClientInfo
            Contains client_id and client public key.
        """

        url = self.__get_url("v1", "storage", "clients", str(client_id))
        response = requests.get(url=url, auth=self.e3db_auth)
        if response.status_code == 404:
            raise LookupError('Client ID not found: {0}'.format(client_id))

        self.__response_check(response)
        json = response.json()

        client_id = json['client_id']
        public_key = json['public_key']
        validated = json['validated']
        return ClientInfo(client_id, public_key, validated)

    def __client_key(self, client_id):
        """
        Private method to retrieve decoded public key from the server based
        on client id.

        Parameters
        ----------
        client_id : str
            UUID of the client to lookup info for

        Returns
        -------
        nacl.public.PublicKey
            Public key from client_id specified
        """

        if client_id == self.client_id:
            return Crypto.decode_public_key(self.public_key)
        else:
            client_info = self.client_info(client_id).to_json()
            return Crypto.decode_public_key(client_info['public_key']['curve25519'])

    def __read_raw(self, record_id):
        """
        Private method to retrieve encrypted record from the server.

        Parameters
        ----------
        record_id : str
            UUID of the record to retrieve

        Returns
        -------
        e3db.Record
            Encrypted E3DB record
        """

        url = self.__get_url("v1", "storage", "records", str(record_id))
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        json = response.json()
        # craft meta object
        # craft record object
        meta_json = json['meta']
        data_json = json['data']
        meta = Meta(meta_json)
        record = Record(meta, data_json)
        return record

    def read(self, record_id):
        """
        Public Method to retrieve encrypted record from the server, and decrypt it
        locally.

        Parameters
        ----------
        record_id : str
            UUID of the record to retrieve

        Returns
        -------
        e3db.Record
            Decrypted E3DB record
        """

        return self.__decrypt_record(self.__read_raw(record_id))

    def write(self, record_type, data, plain=None):
        """
        Public Method to take a plaintext record, encrypt it locally, and send it
        to the server.

        Parameters
        ----------
        record_type: str
            type of the record to be stored

        data : dict
            JSON-style document containing data to encrypt

        plain : dict
            JSON-style document containing plaintext meta data.
            Optional.

        Returns
        -------
        e3db.Record
            Decrypted E3DB record
        """

        url = self.__get_url("v1", "storage", "records")
        meta_data = {
            'writer_id': str(self.client_id),
            'user_id': str(self.client_id),
            'type': record_type,
            'plain': plain
        }
        meta = Meta(meta_data)
        record = Record(meta, data)
        encrypted_record = self.__encrypt_record(record)
        response = requests.post(url=url, json=encrypted_record.to_json(), auth=self.e3db_auth)
        self.__response_check(response)
        response_json = response.json()
        response_meta = Meta(response_json['meta'])
        decrypted = self.__decrypt_record(Record(response_meta, response_json['data']))
        return decrypted

    def update(self, record):
        """
        Public Method to take an updated plaintext record, encrypt it locally, and
        send it to the server.

        Maintains the same record id, while the record version, and data
        changes.

        Parameters
        ----------
        record: e3db.Record
            plaintext record to encrypt and send updated version to server

        Returns
        -------
        e3db.Record
            Decrypted E3DB record, with updated record version
        """
        record_serialized = record.to_json()
        record_id = record_serialized['meta']['record_id']
        version = record_serialized['meta']['version']
        url = self.__get_url("v1", "storage", "records", "safe", str(record_id), version)
        encrypted_record = self.__encrypt_record(record)
        # We don't want to post datetime objects to the server, so we remove
        # them as they are unnecessary
        encrypted_record_json = encrypted_record.to_json()
        del encrypted_record_json['meta']['created']
        del encrypted_record_json['meta']['last_modified']
        response = requests.put(url=url, json=encrypted_record_json, auth=self.e3db_auth)
        self.__response_check(response)
        json = response.json()
        new_meta = Meta(json['meta'])
        new_data = json['data']
        new_record = Record(meta=new_meta, data=new_data)
        return self.__decrypt_record(new_record)

    def delete(self, record_id, version):
        """
        Public Method to delete a record.

        Requires both the record id, and current version to ensure a safe
        delete operation.

        Parameters
        ----------
        record_id: str
            UUID of the record

        version: str
            UUID version from the record

        Returns
        -------
        None
        """
        url = self.__get_url("v1", "storage", "records", "safe", str(record_id), version)
        response = requests.delete(url=url, auth=self.e3db_auth)
        self.__response_check(response)

    def backup(self, client_id, registration_token):
        """
        Public Method to write backup credentials to InnoVault console
        for recovery, if desired during registration.

        Parameters
        ----------
        client_id: str
            UUID of client

        registration_token: str
            Token obtained from InnoVault console used for dynamic registration

        Returns
        -------
        None
        """
        # credentials must be json encoded in order to decode
        # properly in the innovault console.
        credentials = {
            'version': '1',
            'client_id': "\"{0}\"".format(self.client_id),
            'api_key_id': "\"{0}\"".format(self.api_key_id),
            'api_secret': "\"{0}\"".format(self.api_secret),
            'client_email': "\"{0}\"".format(self.client_email),
            'public_key': "\"{0}\"".format(self.public_key),
            'private_key': "\"{0}\"".format(self.private_key),
            'api_url': "\"{0}\"".format(self.api_url)
        }

        self.write('tozny.key_backup', credentials, {'client': self.client_id})
        # share this record type with the backup client
        self.share('tozny.key_backup', client_id)

        url = self.__get_url('v1', 'account', 'backup', registration_token, str(self.client_id))
        response = requests.post(url=url, auth=self.e3db_auth)
        self.__response_check(response)

    def query(self, data=True, writer=[], record=[], record_type=[], plain=None, page_size=DEFAULT_QUERY_COUNT, last_index=0):
        """
        Public method to Query E3DB records according to selection criteria.


        The default behavior is to return all records written by the current
        authenticated client.

        Query results can be restricted based on types of records, record ids,
        writers, plaintext meta filters. Results can be 'paged' to limit large
        amounts of records being returned.

        Parameters
        ----------
        data: bool
            Whether to include the record's data when returned in the query.
            Optional.

        writer: list
            List of writer ids to filter on.
            Optional.

        record: list
            List of record ids to filter on.
            Optional.

        record_type: list
            List of record types to filter on.
            Optional.

        plain: dict
            JSON-style Plaintext meta data query object to use for matching
            against record plaintext meta data fields.
            Optional.

        page_size : int
            How many records to return per query. Can be used in conjunction
            with last_index to read records in 'batches'.

        last_index : int
            Retrieve records from this index onwards. Starts at 0 to return all.
            Useful for retrieving records in 'batches'. Exposed to user through
            the QueryResult.get_after_index() method.

        Returns
        -------
        e3db.QueryResult
            Iterable object that returns decrypted e3db.Record objects.
        """
        all_writers = False
        if writer == "all":
            all_writers = True
            writer = []

        # convert all possible UUID types back to strings
        writer = [str(i) for i in writer]
        record = [str(i) for i in record]

        q = Query(after_index=last_index, include_data=data, writer_ids=writer,
                record_ids=record, content_types=record_type, plain=plain,
                user_ids=[], count=page_size,
                include_all_writers=all_writers)

        response = self.__query(q)

        # take this apart
        last_index = response['last_index']
        results = response['results']
        records = []

        for result in results:
            result_meta = result['meta']
            meta = Meta(result_meta)
            result_data = result['record_data']
            record = Record(meta=meta, data=result_data)

            if data:
                # need to decrypt all the results before returning.
                access_key = result['access_key']
                if access_key:
                    ak = self.__decrypt_eak(access_key)
                    record = self.__decrypt_record_with_key(record, ak)
                else:
                    record = self.__decrypt_record(record)

            records.append(record)

        qr = QueryResult(q, records)
        qr.after_index = last_index
        return qr

    def __query(self, query):
        """
        Private Method to send query to server and return response.

        Parameters
        ----------
        query: e3db.Query
            Query to run against the server.

        Returns
        -------
        dict
            server response as dict (JSON)
        """
        url = self.__get_url('v1', 'storage', 'search')
        response = requests.post(url=url, json=query.to_json(), auth=self.e3db_auth)
        if 'error' in response.text:
            # we had an error, return this to user
            raise QueryError(response.json()['error'])
        self.__response_check(response)
        return response.json()

    def share(self, record_type, reader_id):
        """
        Public Method to share a record type with another client.

        Records are shared based on record type between clients. Once a record
        type is shared between clients, all future records of that type are
        automatically shared, and able to be read by both parties.

        Parameters
        ----------
        record_type: str
            type of the record to be stored

        reader_id : str
            The reader's client id (UUID) to share this record type with.

        Returns
        -------
        None
        """
        if reader_id == self.client_id:
            return

        ak = self.__get_access_key(self.client_id, self.client_id, self.client_id, record_type)
        if ak is None:
            ak = Crypto.random_key()
        self.__put_access_key(self.client_id, self.client_id, reader_id, record_type, ak)

        allow_read = {
            'allow': [
                {'read': {}}
            ]
        }

        self.__put_policy(str(self.client_id), str(self.client_id), str(reader_id), record_type, allow_read)

    def revoke(self, record_type, reader_id):
        """
        Public Method to revoke access to a record type that was previously
        shared with another client.

        Deletes the keys used by the other client to be able to decrypt the
        shared data.

        Parameters
        ----------
        record_type: str
            type of the record to be stored

        reader_id : str
            The reader's client id (UUID) to share this record type with.

        Returns
        -------
        None
        """
        if reader_id == self.client_id:
            return

        deny_read = {
            'deny': [
                {
                    'read': {}
                }
            ]
        }

        self.__put_policy(str(self.client_id), str(self.client_id), str(reader_id), record_type, deny_read)
        self.__delete_access_key(self.client_id, self.client_id, reader_id, record_type)

    def add_authorizer(self, record_type, authorizer_id):
        """
        Public Method to share a record type with an authorizer.

        Parameters
        ----------
        record_type: str
            type of the record to be stored

        authorizer_id : str
            The authorizer's client id (UUID) to share this record type with.

        Returns
        -------
        None
        """

        ak = self.__get_access_key(str(self.client_id), str(self.client_id), str(self.client_id), record_type)
        if ak is None:
            ak = Crypto.random_key()
        self.__put_access_key(str(self.client_id), str(self.client_id), str(authorizer_id), record_type, ak)

        allow_authorizer = {
            'allow': [
                {'authorizer': {}}
            ]
        }

        self.__put_policy(str(self.client_id), str(self.client_id), str(authorizer_id), record_type, allow_authorizer)

    def remove_authorizer(self, record_type, authorizer_id):
        """
        Public Method to revoke access of a record type shared with an authorizer.

        Parameters
        ----------
        record_type: str
            type of the record to be stored

        authorizer_id : str
            The authorizer's client id (UUID) to share this record type with.

        Returns
        -------
        None
        """

        deny_authorizer = {
            'deny': [
                {'authorizer': {}}
            ]
        }

        self.__put_policy(str(self.client_id), str(self.client_id), str(authorizer_id), record_type, deny_authorizer)
        self.__delete_access_key(str(self.client_id), str(self.client_id), str(authorizer_id), record_type)

    def share_on_behalf_of(self, writer_id, reader_id, record_type):
        """
        Public Method for an authorizer to share data it has been authorized to share
        with another client

        Parameters
        ----------
        writer_id: str
            type of the record to be stored

        reader_id : str
            The reader's client id (UUID) to share this record type with.

        Returns
        -------
        None
        """

        ak = self.__get_access_key(str(writer_id), str(writer_id), str(self.client_id), record_type)
        # This should only happen if the authorizer tries to share on behalf of, and has had
        # their authorizer rights revoked, the eak will be missing from the E3DB system at that point
        if ak is None:
            raise APIError('Requested item not found: HTTP 404')
        self.__put_access_key(str(writer_id), str(writer_id), str(reader_id), record_type, ak)

        allow_read = {
            'allow': [
                {'read': {}}
            ]
        }

        self.__put_policy(str(writer_id), str(writer_id), str(reader_id), record_type, allow_read)

    def get_authorized_by(self):
        """
        Public Method to get a list of all clients (and associated record types) that
        this client may act as an authorizer

        Parameters
        ----------
        None

        Returns
        -------
        list
            List of e3db.GrantedAuthorizerPolicy documents
        """

        url = self.__get_url("v1", "storage", "policy", "granted")
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        # create list of policy objects, and return them
        policies = []
        # check if there are no policies
        if response.json():
            for policy in response.json():
                policies.append(GrantedAuthorizerPolicy(policy))
        return policies

    def get_authorizers(self):
        """
        Public Method to get a list of all clients (and associated record types) that
        this client has authorized to share on its behalf.

        Parameters
        ----------
        None

        Returns
        -------
        list
            List of e3db.ProxyAuthorizerPolicy documents
        """

        url = self.__get_url("v1", "storage", "policy", "proxies")
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        # create list of policy objects, and return them
        policies = []
        # check if there are no policies
        if response.json():
            for policy in response.json():
                policies.append(ProxyAuthorizerPolicy(policy))
        return policies
