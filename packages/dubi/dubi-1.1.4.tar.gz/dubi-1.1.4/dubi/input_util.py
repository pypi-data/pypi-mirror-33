from version_util import is_python_2


def get_input(hint, refresh=None):
    inputs = compatible_input(':')
    if inputs[0] == 'q' and len(inputs) == 1:
        print('quit')
        exit()
    elif inputs[0] == 'h' and len(inputs) == 1:
        print(hint)
        print('h: helper\nr: refresh\nq: exit')
        return get_input(hint, refresh)
    elif inputs[0] == 'r' and len(inputs) == 1:
        if refresh is not None:
            refresh()
        return get_input(hint, refresh)
    else:
        return inputs.split(' ')


def compatible_input(hint):
    if is_python_2():
        return raw_input(hint)
    else:
        return input(hint)
