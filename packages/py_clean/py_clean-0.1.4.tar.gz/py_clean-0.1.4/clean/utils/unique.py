import uuid
import shortuuid


class UniqueGenerator:

    @staticmethod
    def generate() -> str:
        raise NotImplementedError


class UUIDGenerator(UniqueGenerator):

    @staticmethod
    def generate():
        return str(uuid.uuid4())


class ShortUUIDGenerator(UniqueGenerator):

    @staticmethod
    def generate() -> str:
        return shortuuid.uuid()
