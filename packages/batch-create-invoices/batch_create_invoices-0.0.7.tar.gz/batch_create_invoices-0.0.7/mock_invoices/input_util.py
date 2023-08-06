import re
from getpass import getpass
from typing import Pattern, List


class IndexNotExistError(Exception):
    pass


class EmptyInputError(Exception):
    pass


class InputOption:
    def __init__(self, label: str, value):
        self.label: str = label
        self.value = value


def input_with_validate(prompt: str, reg: str = '.+', err_msg: str = 'Input invalid, please re-input!',
                        default_val: str = '', is_password: bool = False) -> str:
    pattern: Pattern
    if reg:
        pattern = re.compile(reg)

    while True:
        use_default: bool = False
        input_str: str = ''
        if is_password:
            print('{:s}: '.format(prompt))
            input_str = getpass()
        else:
            input_str = input('{:s}: '.format(prompt))
        input_str = input_str.strip()

        if len(input_str) == 0 and default_val != '':
            use_default = True
            input_str = default_val

        if pattern and not pattern.match(input_str):
            print(err_msg)
        else:
            if use_default:
                print('Use default value: {:s}'.format(default_val))
            break
    return input_str


def input_with_options(prompt: str, options: List[InputOption]):
    print('{:s} '.format(prompt))

    for idx, opt in enumerate(options):
        print('{:d}. {:s}'.format(idx, opt.label))

    while True:
        input_str = input()
        input_str = input_str.strip()
        selected_index: int

        try:
            if len(input_str) == 0:
                raise EmptyInputError('Please choose an option!')
            selected_index = int(input_str)

            if selected_index >= len(options) or selected_index < 0:
                raise IndexNotExistError('Index of input {:d} not exist!'.format(selected_index))
        except EmptyInputError as err:
            print(err)
            continue
        except ValueError as err:
            print(err)
            continue
        except IndexNotExistError as err:
            print(err)
            continue
        break

    opt: InputOption = options[selected_index]
    return opt.value
