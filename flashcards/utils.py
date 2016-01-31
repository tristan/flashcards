import tornado.escape

def force_unicode(value):
    if not isinstance(value, (str, bytes)):
        return str(value)
    return tornado.escape.to_unicode(value)
