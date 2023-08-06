#
# Jinja2-Redis
#
# Copyright (C) 2018 Boris Raicheff
# All rights reserved
#


from jinja2 import BytecodeCache


class RedisBytecodeCache(BytecodeCache):
    """
    http://jinja.pocoo.org/docs/api/#bytecode-cache
    """

    def __init__(self, client, prefix='jinja2:'):
        self.client = client
        self.prefix = prefix

    def load_bytecode(self, bucket):
        code = self.client.get(self.prefix + bucket.key)
        if code is not None:
            bucket.bytecode_from_string(code)

    def dump_bytecode(self, bucket):
        args = (self.prefix + bucket.key, bucket.bytecode_to_string())
        self.client.set(*args)


# EOF
