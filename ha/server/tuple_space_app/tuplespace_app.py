import json


class TupleSpaceApp:

    def __init__(self, tuple_space_file):
        self.tuple_space_file = tuple_space_file
        self.tuple_space = {}
        pass

    def init(self):
        self.load_tuple_space()

    def get(self, data):
        print(data)

        try:
            tp = eval(data)
        except:
            return self.error_msg('invlaid')

        return self.ok_msg('this is ur result')

    def post(self, data):
        return "do post"

    def put(self, data):
        # self.tuple_space.update()
        try:
            tp = eval(data)
            if not isinstance(tp, list):
                raise ValueError("not list")
        except:
            return self.error_msg('invlaid')

        for t in tp:
            self.tuple_space[t[0]] = t[1]

        return self.ok_msg(f'{len(tp)} tuples saved')

    def delete(self, data):

        return "do delete"

    def ok_msg(self, msg):
        return 'ok:'+msg

    def error_msg(self, msg):
        return 'error:'+msg

    def load_tuple_space(self) -> None:
        """ Load tuple space from tuple space file"""
        try:
            if self.tuple_space_file is not None:
                with open(self.tuple_space_file, "r") as file:
                    file_content = file.read().strip()
                    try:
                        self.tuple_space = json.loads(file_content)
                    except ValueError as err:
                        raise

        except Exception as err:
            raise

    def shutdown(self):
        if self.tuple_space:
            with open(self.tuple_space_file, 'w') as fp:
                json.dump(self.tuple_space, fp)
