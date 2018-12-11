import json
import re
from ha.commons.utils import validate_reg_ex


class TupleSpaceApp:

    def __init__(self, tuple_space_file):
        self.tuple_space_file = tuple_space_file
        self.tuple_space = {}
        pass

    def init(self):
        self.load_tuple_space()

    def get(self, data):
        """
            Find matching (key,val) pairs in tuple space
        :param data:(keyExp,valExp)
        :return: list of matching key,val pairs. Empty list, if regex is invalid
        """

        try:
            key_expr, val_expr = eval(data)
            response = self.search_tuple(key_expr, val_expr)
        except:
            return self.error_msg('invlaid')

        return self.ok_msg(str(response))

    def search_tuple(self, key_expr, val_expr):
        validate_reg_ex(key_expr)
        validate_reg_ex(val_expr)
        response = [(k, v) for k, v in self.tuple_space.items()
                    if re.match(key_expr, k) and re.match(val_expr, v)]
        return response

    def put(self, data):
        """
            adds tuples to the tuple space,
        :param data: list of tuples
        :return: List containing (key, value) pairs that could not be added to the tuple space
        """
        print(self.tuple_space)

        not_added = []
        try:
            tuples_list = eval(data)
            if not isinstance(tuples_list, list):
                raise ValueError("not a list: put accepts only a valid list")
        except ValueError as err:
            return self.error_msg(err)
        except:
            return self.error_msg('invlaid command')

        for tp in tuples_list:

            # check if key,val is well formed and key is not yet in tuple space
            if isinstance(tp, tuple) and tp[0] not in self.tuple_space:
                self.tuple_space.update({tp[0]: tp[1]})
            else:
                not_added.append(tp)
        print(self.tuple_space)


        return self.ok_msg(f'{not_added} not added to the tuple space')

    def post(self, data):
        """
            update the tuple space (key,val) pairs using matching keys,
        :param data: list of tuples
        :return: List of (key, value) pairs not used to update the tuple space
        """

        not_used = []
        try:
            tuples_list = eval(data)
        except:
            return self.error_msg("Invalid")

        if not isinstance(tuples_list, list):
            return self.error_msg("not a list")
        for tp in tuples_list:

            # check if key,val is well formed and key is in tuple space
            if isinstance(tp, tuple) and tp[0] in self.tuple_space:
                # update value associated with key
                self.tuple_space.update({tp[0]: tp[1]})
            else:
                not_used.append(tp)

        return self.ok_msg(f'{not_used} not used to update the tuple space')

    def delete(self, data):
        """
        Delete matching (key,val) pairs in tuple space
        :param data:
        :return: list of matching (key,val) pairs that were deleted. Empty list, if regex is invalid
        """
        deleted_items = []
        try:
            key_expr, val_expr = eval(data)
            validate_reg_ex(key_expr)
            validate_reg_ex(val_expr)
        except re.error:
            return self.ok_msg([])
        except:
            return self.error_msg('invlaid')

        for k in [k for k, v in self.tuple_space.items() if re.match(key_expr, k) and re.match(val_expr, v)]:
            deleted_items.append((k, self.tuple_space[k]))
            del self.tuple_space[k]

        return self.ok_msg(f'{deleted_items} deleted from the tuple space')

    def ok_msg(self, msg):
        return 'ok:' + msg

    def error_msg(self, msg):
        return 'error:' + msg

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
        try:
            if self.tuple_space:
                with open(self.tuple_space_file, 'w') as fp:
                    json.dump(self.tuple_space, fp)
        except :
            raise

