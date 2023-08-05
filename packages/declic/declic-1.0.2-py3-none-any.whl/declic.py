import argparse
import inspect

__all__ = ['command', 'group', 'argument', 'Group', 'Command']


# patch add_parser to allow use of pre-existing parser
def custom_add_parser(self, name, **kwargs):
    # set prog from the existing prefix
    if kwargs.get('prog') is None:
        kwargs['prog'] = '%s %s' % (self._prog_prefix, name)

    aliases = kwargs.pop('aliases', ())

    # create a pseudo-action to hold the choice help
    if 'help' in kwargs:
        help = kwargs.pop('help')
        choice_action = self._ChoicesPseudoAction(name, aliases, help)
        self._choices_actions.append(choice_action)

    parser = kwargs.pop('parser', None)
    # allow use of pre-existing parser
    # could check that it is valid, e.g. isinstance(parse, ArgumentParser)
    if parser is None:
        # create the parser and add it to the map
        parser = self._parser_class(**kwargs)
    self._name_parser_map[name] = parser

    # make parser available under aliases also
    for alias in aliases:
        self._name_parser_map[alias] = parser

    return parser


argparse._SubParsersAction.add_parser = custom_add_parser


class CachedProperty(object):
    """
    A descriptor to cache the execution of a property, and sending the computed
    value again and again.
    """

    def __init__(self, method):
        """
        Store the wrapped method, and its name.
        """
        self.name = method.__name__
        self.func = method

    def __get__(self, instance, owner):
        """
        When getting the attribute the first time, the descriptor is called and
        then compute the method (no arguments) as usual. Then the method in
        the instance is replaced by an attribute containing the cached value.
        """
        # compute the method as usual
        result = self.func(instance)

        # replace the method by the attribute, avoiding to call the descriptor
        # again !
        setattr(instance, self.name, result)

        # return the result
        return result


class Command(object):
    def __init__(self, name, description=None, callback=None, parent=None, chain=False):
        self.name = name
        # set the parser
        self.parser = argparse.ArgumentParser(prog=name, description=description)

        # set the callback command
        self._callback = callback

        # enable/disable chain mode
        self.chain = chain

        # the the parent command/group if any
        self.parent = parent

        # get command parameters
        try:
            params = callback.__cli_params__
            del callback.__cli_params__
        except AttributeError:
            params = []

        # add parameters to the parser
        for param_args, param_kwargs in params:
            self.add_argument(*param_args, **param_kwargs)

        # check if the reserved argument '__declic_invoke_function__' is used
        if '__declic_invoke_function__' in [action.dest for action in self.parser._actions]:
            raise Exception('"__declic_invoke_function__" is a reserved argument')

        # specify which function to call depending on args parsing
        self.parser.set_defaults(__declic_invoke_function__=self.invoke)

    @CachedProperty
    def parents(self):
        if self.parent is None:
            # parents list is empty
            return []
        else:
            # get the parent list
            return self.parent.parents + [self.parent]

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    @staticmethod
    def get_func_keywords(func):
        callback_argspec = inspect.getfullargspec(func)
        # if **kwargs in the callback signature, there is no specific keywords
        if callback_argspec.varkw is not None:
            return None
        else:
            # else, only args/kwargs present in the callback signature are returned
            keywords = callback_argspec.args + callback_argspec.kwonlyargs
            return keywords

    def generic_callback(self, args_dict, callback_function):
        """
        Invoke a callback function with a filtered list of arguments to undefined argument issues

        :param args_dict: unfiltered arguments
        :param callback_function: Callback function
        :return:
        """

        callback_keywords = self.get_func_keywords(callback_function)

        # if there are specific keywords for the callback function
        if callback_keywords is not None:
            # remove unwanted keys
            try:
                filtered_args_dict = {key: args_dict[key] for key in callback_keywords}
            except KeyError as err:
                raise KeyError(f'No argument "{err.args[0]}" found in the definition of the command "{self.name}"')

        else:
            filtered_args_dict = args_dict
        callback_function(**filtered_args_dict)

    def callback(self, args_dict):
        self.generic_callback(args_dict, self._callback)

    def on_before(self, args_dict):
        self.generic_callback(args_dict, self._on_before)

    def invoke_parents(self, args_dict):
        # if chain mode is activated, call parents callbacks before command callback itself
        for parent in self.parents:
            # for each parent, call the on_before function if any
            if parent._on_before is not None:
                parent.on_before(args_dict)
            # then call the callback function if chain mode is activated and if the parent is invokable
            if parent._callback is not None:
                if self.chain and parent.invokable:
                    parent.callback(args_dict)

    def invoke(self, args):
        args_dict = vars(args)

        self.invoke_parents(args_dict)

        if self._callback is None:
            raise NotImplementedError(f'No callback function set for the command "{self.name}"')
        else:
            self.callback(args_dict)

    def main(self, argv=None):
        args = self.parser.parse_args(argv)
        args.__declic_invoke_function__(args)

    def print_help(self):
        self.parser.print_help()

    def __call__(self, argv=None):
        return self.main(argv)


class Group(Command):
    def __init__(self, *args, invokable=False, on_before=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.subparsers = self.parser.add_subparsers()
        self.commands = {}
        # this controls if the group command itself can be invoked
        self.invokable = invokable

        # this function will be called before each invoke of the group
        # even if the group is not invokable
        self._on_before = on_before

    def invoke_group(self, args_dict):

        if self._callback is None:
            raise NotImplementedError(f'No callback function set for the command "{self.name}"')
        else:
            self.callback(args_dict)

    def invoke(self, args):
        args_dict = vars(args)

        # check chain attribute and invoke parents if any
        self.invoke_parents(args_dict)

        # call on_before function
        if self._on_before is not None:
            self.on_before(args_dict)

        if self.invokable:
            self.invoke_group(args_dict)
        else:
            self.print_help()

    def add_command(self, cmd, name=None):
        name = name or cmd.name
        if name is None:
            raise TypeError('Command has no name.')
        self.commands[name] = cmd
        self.subparsers.add_parser(name, parser=cmd.parser)

    def command(self, *args, **kwargs):
        """A shortcut decorator for declaring and attaching a command to
        the group.  This takes the same arguments as :func:`command` but
        immediately registers the created command with this instance by
        calling into :meth:`add_command`.
        """

        def decorator(callback):
            cmd = command(*args, parent=self, **kwargs)(callback)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        """A shortcut decorator for declaring and attaching a group to
        the group.  This takes the same arguments as :func:`group` but
        immediately registers the created command with this instance by
        calling into :meth:`add_command`.
        """

        def decorator(callback):
            cmd = group(*args, parent=self, **kwargs)(callback)
            self.add_command(cmd)
            return cmd

        return decorator


def command(name=None, *args, **kwargs):
    def decorator(callback):
        command_name = name or callback.__name__.lower()
        return Command(command_name, callback=callback, *args, **kwargs)

    return decorator


def group(name=None, *args, **kwargs):
    def decorator(callback):
        group_name = name or callback.__name__.lower()
        return Group(group_name, callback=callback, *args, **kwargs)

    return decorator


def argument(*args, **kwargs):
    def decorator(func):
        if not hasattr(func, '__cli_params__'):
            func.__cli_params__ = []
        func.__cli_params__.append((args, kwargs))
        return func

    return decorator
