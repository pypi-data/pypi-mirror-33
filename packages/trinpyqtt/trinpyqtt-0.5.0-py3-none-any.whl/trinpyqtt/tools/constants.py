# RESULT CODES
# Above 0 = Partial Success (Does not raise exception)
# Below 0 = Outright failure (Raises Exception)
# Between -200 and +200 is reserved, and user codes should be assigned
# outside this range.
P_SOME_EVENTS_BROKEN = 2    # Partial, Bad timestamp.
P_BAD_TS = 1                # Partial, Bad timestamp.
SUCCESS = 0                 # Success, None
F_PL_EMPTY = -1             # Payload empty.
F_PL_NOT_LIST = -2          # Payload is not an array.
F_PL_TOO_SHORT = -3         # Payload does not contain at least 2 elements.
F_PL_TOO_LONG = -4          # Payload longer than 3 or 4(for x types) elements.
F_MSG_TYPE = -5             # The message is not of the type c, d, e, x or i.
F_CT_NOT_LIST = -6          # The command type not an array.
F_CTL_EMPTY = -7            # Command array is empty.
F_C_NOT_STRING = -8         # First element of command array is not a string.
F_ET_NOT_LIST = -9          # The event type not an array.
F_ET_EMPTY = -10            # Event array is empty.
F_E_NOT_LIST = -11          # The event not an array.
F_E_EMPTY = -12             # Event array is empty.
F_EC_NOT_INT = -13          # Event code is not a number.
F_PL_NOT_JSON = -14         # Master payload is not parseable as a JSON object.
F_TCT_NOT_STRING = -15      # TCT is not a string
F_RC_NOT_INT = -16          # Reply code on an reply message is not an number
F_ALL_EVENTS_BROKEN = -17   # Raised when no events could successfully be parsed
F_ERROR = -18               # General Error
F_UNKNOWN_PID = -19         # Failed: Unknown PID
F_BROKEN_TOPIC = -20        # Failed: Malformed topic structure
F_VAR_NOT_EXP = -21         # Failed: Variable not exposed
F_EXCEPTION = -22           # Failed: Caught exception
F_DW_NOT_EXPOSED = -23      # Failed: Attempted data-write to unexposed variable
F_NOT_A_BOOLEAN = -24       # Failed: Parameter not a boolean
F_NO_RPC = -100             # RPC command not implemented.

# EVENT CODES
EC_LWT = 101                # Last Will And testament released
EC_CONNECT_SUCCESS = 102    # Last Will And testament released

