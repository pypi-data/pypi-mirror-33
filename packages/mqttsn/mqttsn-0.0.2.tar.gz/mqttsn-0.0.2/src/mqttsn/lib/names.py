# Message types
ADVERTISE, SEARCHGW, GWINFO, _reserved, \
    CONNECT, CONNACK, \
    WILLTOPICREQ, WILLTOPIC, WILLMSGREQ, WILLMSG, \
    REGISTER, REGACK, \
    PUBLISH, PUBACK, PUBCOMP, PUBREC, PUBREL, _reserved_, \
    SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK, \
    PINGREQ, PINGRESP, DISCONNECT, _reserved__, \
    WILLTOPICUPD, WILLTOPICRESP, WILLMSGUPD, WILLMSGRESP = range(30)

packet_names = [
    "ADVERTISE", "SEARCHGW", "GWINFO", "reserved",
    "CONNECT", "CONNACK",
    "WILLTOPICREQ", "WILLTOPIC", "WILLMSGREQ", "WILLMSG",
    "REGISTER", "REGACK",
    "PUBLISH", "PUBACK", "PUBCOMP", "PUBREC", "PUBREL", "reserved",
    "SUBSCRIBE", "SUBACK", "UNSUBSCRIBE", "UNSUBACK",
    "PINGREQ", "PINGRESP", "DISCONNECT", "reserved",
    "WILLTOPICUPD", "WILLTOPICRESP", "WILLMSGUPD", "WILLMSGRESP"
]

topic_id_type_names = ["NORMAL", "PREDEFINED", "SHORT_NAME"]
TOPIC_NORMAL, TOPIC_PREDEFINED, TOPIC_SHORTNAME = range(3)
