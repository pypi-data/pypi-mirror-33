import re

class ArgvParser:
    """
    This module allows to format an argument vector
    Its structure is easier to read and use for command line applications
    """

    @classmethod
    def parse(cls, argv):
        """
        Formate arguments vector to a dictionnary

        :param argv: The arguments vector
        :type argv: list

        :return: The formated arguments
        :rtype: dict

        :raise Exception: Argument assigned to any option

        :Example:

        >>> cls.parse(['app.py', 'ls', '-lar', '42', '--float', '3.14'])
        {
            'app': 'app', 
            'command': 'ls', 
            'options': {
                '-l': None, 
                '-a': None, 
                '-r': 42, 
                '--float': 3.14
            }
        }

        >>> cls.parse(['app.py', '--print', 'My message I want to print', '-i'])
        {
            'app': 'app', 
            'command': None, 
            'options': {
                '--print': 'My message I want to print', 
                '-i': None
            }
        }

        >>> cls.parse(['app.py', '-v', '/var/www', '-i', '-v', '/var/bin/bash'])
        {
            'app': 'app', 
            'command': None, 
            'options': {
                '-v': [
                    '/var/www',
                    '/var/bin/bash'
                ],
                '-i': None
            }
        }
        """

        args = {'app': None, 'command': None, 'options': {}}

        if re.search(r'\.(\w)+', argv[0], re.IGNORECASE):
            args['app'] = re.sub(r'\.(\w)+', '', argv.pop(0), re.IGNORECASE)

        if not cls.is_option(argv[0]):
            args['command'] = argv[0]

        argv = cls.parse_multi_options(argv)

        for i, arg in enumerate(argv):
            j = (i + 1) if (i + 1) < len(argv) else i

            if cls.is_option(arg) and not cls.is_option(argv[j]):
                if arg in args['options']:
                    if isinstance(args['options'][arg], list):
                        args['options'][arg].append(cls.parse_type(argv[j]))
                    else:
                        tmp = args['options'][arg]
                        args['options'][arg] = list((cls.parse_type(argv[j]), tmp))
                else:
                    args['options'][arg] = cls.parse_type(argv[j])
            elif cls.is_option(arg):
                args['options'][arg] = None

            if i < (len(argv) - 1) and not cls.is_option(arg) and not cls.is_option(argv[j]):
                raise Exception('Argument \'%s\' is assigned to any option.' % argv[j])  

        return args

    @classmethod
    def parse_multi_options(cls, argv):
        """
        Retrieves multiple argument (like -li) and reconstruct it to a correct format

        :param argv: The arguments vector
        :type argv: list

        :return: Correctly formated arguments vector
        :rtype: list

        :Example:

        >>> cls.parse_multi_options(['app.py', '-liar', '--test'])
        ['app.py', '-l', '-i', '-a', '-r', '--test']
        """

        new_argv = []

        for arg in argv:
            if re.search(r'^(-)(\w){2,}', arg, re.IGNORECASE):
                for letter in list(arg)[1:]:
                    new_argv.append(arg[0] + letter)
            else:
                new_argv.append(arg)
        
        return new_argv

    @classmethod
    def is_option(cls, arg):
        """
        Check if the argument in parameter is an option or not

        :param arg: The argument to control
        :type arg: str

        :return: True if arg is an option, else false
        :rtype: bool

        :Example:

        >>> cls.is_option('-t')
        True

        >>> cls.is_option('--test')
        True

        >>> cls.is_option('test')
        False
        """

        if re.search(r'^(-){1,2}', arg, re.IGNORECASE):
            return True

        return False

    @classmethod
    def parse_type(cls, arg):
        """
        Convert the passed argument into the appropriate type

        :param arg: The argument to convert
        :type arg: str, None

        :return: The converted argument
        :rtype: int, float, str, None

        :note: The default type returned is a str

        :Example:

        >>> cls.parse_type('test')
        'test'

        >>> cls.parse_type('42')
        42

        >>> cls.parse_type('3.14')
        3.14
        """

        if re.search(r'^(\d)+$', arg, re.IGNORECASE):
            return int(arg)

        if re.search(r'^(\d)+(\.){1}(\d)$', arg, re.IGNORECASE):
            return float(arg)

        return arg