# -*- coding: utf-8 -*-
'''
This module contains classes for game objects that are relevant for both client and server:
*GameState*, *GameStateUpdate* and *ClientActivity*.
Client as well as server are supposed to define subclasses of classes in this module,
that extend those types with data and functionality that is client-/server-specific.

Also, this module defines the network protocol which *Connection*s and *Server*s use
to communicate. It contains the *UDPPackage* class, which represents a unit of information
that client and server can exchange with each other, as well as classes that make up parts
of a package.
'''

import sys
import random
import umsgpack

# Unique 4-byte token to mark the end of the header of a UDPPackage
_HEADER_END_TOKEN = bytes.fromhex('b5968459')
# Unique 4-byte token to mark
TO_DELETE = bytes.fromhex('d281e5ba')

class TypeClass:
    '''
    Mixin that allows to add class variables to a class during runtime.
    It is used to make enum classes like AktivityType or PackageType extensible.
    '''
    @classmethod
    def add_type(cls, name: str):
        '''
        Add a new named type to this enum-like class.
        '''
        setattr(cls, name, len(cls.__dict__) + 1)

class Sendable:
    '''
    Mixin for classes that are supposed to be sendable as part of a server request or response.
    Sendables can only have basic Python types as attributes and their constructor needs
    to be callable without passing any arguments.
    '''

    def to_bytes(self):
        '''
        Packs and return a small a binary representation of self.

        '''
        return umsgpack.packb(self.__dict__)

    @classmethod
    def from_bytes(cls, bytepack: bytes):
        '''
        Returns a copy of the object that was packed into byte format.
        '''
        try:
            received_sendable = cls()
            received_sendable.__dict__ = umsgpack.unpackb(bytepack)
            return received_sendable
        except (umsgpack.InsufficientDataException, KeyError):
            raise TypeError('Bytes could no be parsed into ' + cls.__name__ + '.')

class GameStatus(TypeClass):
    '''
    Enum class with the values:
    - *Paused*
    - *Active*
    '''
    Paused = 1
    Active = 2

class ActivityType(TypeClass):
    '''
    Enum class with the values:
    - *PauseGame*
    - *ResumeGame*

    Can and is supposed to be extended using *TypeClass*'s *add_type* method.
    '''

    PauseGame = 1
    ResumeGame = 2
    JoinServer = 3
    LeaveServer = 4

class PackageType(TypeClass):
    '''
    Enum class with the following values:
    - *GetGameStateRequest*: As client request the full shared game state from the server.
        body = None
    - *GetGameStateUpdateRequest*: As client request all polled game state updates.
        body = *GameStateUpdate* (purely for time-ordering)
    - *PostClientActivityRequest*: As client post client-side activity to the *GameService*.
        body = *ClientActivity*
    - *ServerResponse*: As server respond to a client request.
        body = request-dependent
    - *ServerError*: As server report an error to the client.
        body = *ErrorMessage*
    '''

    GetGameStateRequest = 1
    GetGameStateUpdateRequest = 2
    PostClientActivityRequest = 3
    ServerResponse = 4
    ServerError = 5

class ErrorType(TypeClass):
    '''
    Enum class with the following values:
    - *RequestTimeout*: Server _response took to long.
    - *UnpackError*: Request or _response bytepack corrupted.
    - *RequestInvalid*: Server could not handle the request.

    To be used as part of an *ErrorMessage* object in a *ServerError* package.
    '''

    RequestTimeout = 1
    UnpackError = 2
    RequestInvalid = 3
    OutOfSync = 4

class ErrorMessage(Sendable):
    '''
    The sendable type *ErrorMessage* is used for the body of *UDPPackage*s with
    *package_type* *PackageType.ServerError* in their *header*.
    '''
    def __init__(self, error_type=ErrorType.RequestInvalid, message=''):
        self.error_type = error_type
        self.message = message

class UDPPackageHeader(Sendable):
    def __init__(self, package_type=PackageType.ServerResponse, body_type='NoneType'):
        self.package_type = package_type
        self.body_type = body_type

    '''
    Override 'object' members
    '''
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.package_type == other.package_type and self.body_type == other.body_type
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

class UDPPackage:
    '''
    Contains *header* and *body* as attributes. The header contains information about the the
    package type and body. The body is some object of a core class like *ErrorMessage*,
    *GameState*, *GameStateUpdate* or *ClientActivity*.
    '''
    def __init__(self, package_type: PackageType, body: Sendable = None):
        self.header = UDPPackageHeader(package_type, body.__class__.__name__)
        self.body = body

    def to_datagram(self):
        '''
        Returns a bytepacked datagram representing the UDPPackage.
        '''
        self.header.body_type = self.body.__class__.__name__
        datagram = bytearray(self.header.to_bytes())
        datagram.extend(_HEADER_END_TOKEN)
        if self.body != None:
            datagram.extend(self.body.to_bytes())
        return bytes(datagram)

    @staticmethod
    def from_datagram(datagram: bytes):
        '''
        Unpacks the given bytepacked datagram and returns it's content as a *UDPPackage*
        object.
        '''
        datagram = datagram.split(_HEADER_END_TOKEN)
        header = UDPPackageHeader.from_bytes(datagram[0])
        if header.body_type != 'NoneType':
            body = getattr(sys.modules[__name__], header.body_type).from_bytes(datagram[1])
        else:
            body = None
        return UDPPackage(header.package_type, body)

    def is_response(self):
        '''
        Returns *True* if the package is of package type *ServerResponse*.
        '''
        return self.header.package_type == PackageType.ServerResponse

    def is_error(self):
        '''
        Returns *True* if the package is of package type *ServerError*.
        '''
        return self.header.package_type == PackageType.ServerError

    def is_update_request(self):
        '''
        Returns *True* if the package is of package type *GetGameStateUpdateRequest*.
        '''
        return self.header.package_type == PackageType.GetGameStateUpdateRequest

    def is_state_request(self):
        '''
        Returns *True* if the package is of package type *GetGameStateRequest*.
        '''
        return self.header.package_type == PackageType.GetGameStateRequest

    def is_post_activity_request(self):
        '''
        Returns *True* if the package is of package type *PostClientActivityRequest*.
        '''
        return self.header.package_type == PackageType.PostClientActivityRequest

    '''
    Override object members
    '''
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.header == other.header and self.body == other.body
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

class GameState(Sendable):
    '''
    Contains game state information that is required to be known both by the server and the client.
    Since it is a *Sendable*, it can only contain basic python types as attributes.

    *time_order* should be in alignment with the servers current update counter.
    '''

    def __init__(self, time_order=0, game_status=GameStatus.Paused):
        self.game_status = game_status
        self.time_order = time_order
        self.players = {}

        ### ONLY FOR TESTING PURPOSES
        self.test_pos = 0

    def is_paused(self):
        '''
        Returns *True* if game status is *Paused*.
        '''
        return self.game_status == GameStatus.Paused

    def iter(self, dict_attr: str):
        '''
        Returns a representation of the *GameState* attribute *dict_attr* that is safe to
        iterate through, while the GameState is concurrently updated. Returns keys and
        values in a tuple.

        Example: Iterate through players with `for player_id, player in game_state.iter('players')`.
        '''
        return getattr(self, dict_attr).copy().items()

    '''
    Overrides of 'object' member functions
    '''
    # Check time ordering
    def __lt__(self, other):
        return self.time_order < other.time_order

    def __gt__(self, other):
        return self.time_order > other.time_order

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.game_status == other.game_status
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

class GameStateUpdate(Sendable):
    '''
    Represents a set of changes to carry out on a *GameState*.
    The server keep a *time_order* counter and labels all updates in ascending order.

    Keywords are *GameState* atttribute names. If you want to remove some key from the
    game state (*GameState* attributes themselves can also be deleted, which removes them from
    the object altogether), just assign *TO_DELETE* to it in the update.

    Use the *+* operator to add *GameStateUpdate*s together or to add them to a
    *GameState* (returning the updated update/state).

    Adding up available updates will always result in an equally or more current but
    also heavier update (meaning it will contain more data).
    '''

    def __init__(self, time_order=0, **kwargs):
        self.__dict__ = kwargs
        self.time_order = time_order

    # Adding to another update should return an updated update
    def __add__(self, other):
        if other > self:
            _recursive_update(self.__dict__, other.__dict__)
            return self
        else:
            _recursive_update(other.__dict__, self.__dict__)
            return other

    # Adding to a GameState should update and return the state
    def __radd__(self, other):
        if type(other) is int:
            # This is so that sum() works on lists of updates, because
            # sum will always begin by adding the first element of the
            # list to 0.
            return self
        if self > other:
            _recursive_update(other.__dict__, self.__dict__, delete=True)
        return other

    # Check time ordering
    def __lt__(self, other):
        return self.time_order < other.time_order

    def __gt__(self, other):
        return self.time_order > other.time_order

class ClientActivity(Sendable):
    '''
    An update the client sends to the server about client-side processes like player movement and
    collisions. The server will validate *ClientActivity* samples and respond with an *OutOfSync*
    error, if they contradict the server-side game state.

    *activity_data* is a *dict* object, that contains all necessary information to process the
    activity server-side (a player's *id*, *position* and *velocity* for example).
    '''
    def __init__(self, activity_type=ActivityType.PauseGame, activity_data={}):
        self.activity_type = activity_type
        self.activity_data = activity_data

def join_server_activity(player_name: str):
    '''
    Returns a *ClientActivity* that joins a player with name *player_name* to the game.

    The field *join_id* in the *activity_data* attribute of the activity can be used
    to uniquely identify the joined player in the shared game state. This means player
    names need not be unique.
    '''
    # 4-byte random id for unique identification of players
    join_id = bytes.fromhex(''.join(random.choices('0123456789abcdef', k=8)))
    return ClientActivity(
        activity_type=ActivityType.JoinServer,
        activity_data={
            'name': player_name,
            'join_id': join_id
        }
    )

def leave_server_activity(player_id):
    '''
    Returns a *ClientActivity* that removes the player with the ID *player_id* from the game.
    '''
    return ClientActivity(
        activity_type=ActivityType.LeaveServer,
        activity_data={'player_id': player_id}
    )

def timeout_error(message=''):
    '''
    Returns a *UDPPackage* with package type *ServerError*,
    error type *RequestTimeout* and *message* as error message.
    '''
    return UDPPackage(
        package_type=PackageType.ServerError,
        body=ErrorMessage(
            error_type=ErrorType.RequestTimeout,
            message=message
        )
    )

def unpack_error(message=''):
    '''
    Returns a *UDPPackage* with package type *ServerError*,
    error type *UnpackError* and *message* as error message.
    '''
    return UDPPackage(
        package_type=PackageType.ServerError,
        body=ErrorMessage(
            error_type=ErrorType.UnpackError,
            message=message
        )
    )

def request_invalid_error(message=''):
    '''
    Returns a *UDPPackage* with package type *ServerError*,
    error type *RequestInvalid* and *message* as error message.
    '''
    return UDPPackage(
        package_type=PackageType.ServerError,
        body=ErrorMessage(
            error_type=ErrorType.RequestInvalid,
            message=message
        )
    )

def out_of_sync_error(message=''):
    '''
    Returns a *UDPPackage* with package type *ServerError*,
    error type *OutOfSync* and *message* as error message.
    '''
    return UDPPackage(
        package_type=PackageType.ServerError,
        body=ErrorMessage(
            error_type=ErrorType.OutOfSync,
            message=message
        )
    )

def game_state_request():
    '''
    Returns a *UDPPackage* with package type *GetGameStateRequest*.
    '''
    return UDPPackage(
        package_type=PackageType.GetGameStateRequest
    )

def game_state_update_request(time_order: int):
    '''
    Returns a *UDPPackage* with package type *GetGameStateUpdateRequest*.
    Enter the *time_order* attribute of the client's last known *GameState*.
    '''
    return UDPPackage(
        package_type=PackageType.GetGameStateUpdateRequest,
        body=GameStateUpdate(
            time_order=time_order
        )
    )

def post_activity_request(client_activity: ClientActivity):
    '''
    Returns a *UDPPackage* with package type *PostClientActivityRequest* with
    the given *ClientActivity* object as it's body.
    '''
    return UDPPackage(
        package_type=PackageType.PostClientActivityRequest,
        body=client_activity
    )

def response(body: Sendable):
    '''
    Returns a *UDPPackage* with package type *ServerResponse*.
    '''
    return UDPPackage(
        package_type=PackageType.ServerResponse,
        body=body
    )

def toggle_pause_activity(shared_game_state: GameState):
    '''
    Returns a *ClientActivity* that either pauses or resumes the server's game loop, depending
    on the *game_status* of the given *GameState*.
    '''
    if shared_game_state.is_paused():
        activity_type = ActivityType.ResumeGame
    else:
        activity_type = ActivityType.PauseGame
    return ClientActivity(
        activity_type=activity_type,
        activity_data={}
    )

# This is for GameStateUpdate objects, which should update nested
# dicts recursively so that no state data is unexpectedly deleted.
# Also, this functions manages deletion of state objects.
def _recursive_update(d: dict, u: dict, delete=False):
    for k, v in u.items():
        if v == TO_DELETE and delete and k in d.keys():
            del d[k]
        elif isinstance(v, dict) and k in d.keys() and isinstance(d[k], dict):
            _recursive_update(d[k], v, delete=delete)
        else:
            d[k] = v
