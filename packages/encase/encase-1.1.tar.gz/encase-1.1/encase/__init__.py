class Encase(dict):
    """This Class is used to create dictionary style objects that
    can have key data accessed by dot (.) notation, for example,
    ::

        data = Encase()
        data.key = "Sample data"
        print(data.key)

    ...would print "Sample Data". Instances of this class can be
    nested. Existing dictionaries, including nested dictionaries,
    can be converted into Encase instances by passing the parent
    dict in as a single parameter. The __init__ function will
    recursively convert any child dictionaries into a Encase
    instances. This also includes any sub-dicts contained within
    a list.
    """

    def __init__(self, existing_object=None):
        """Recursively convert an existing dictionary, if given.

        :param dict existing_object:
            Optional dictionary object to convert
        """
        if isinstance(existing_object, dict):
            for key, value in existing_object.items():
                if isinstance(value, dict):
                    self.set(key, Encase(value))
                elif isinstance(value, list):
                    self.set(key, self._convert_list(value))
                else:
                    self.set(key, value)

    def __getattr__(self, key):
        """Get value of attribute at 'key'. Do not call directly.
        Use, ``data.key``, instead (data is instance of this class).
        """
        if key in self:
            return self[key]
        else:
            raise AttributeError("No value set for: " + key)

    def __setattr__(self, key, value):
        """Set value of attribute at 'key'. Do not call directly.
        Use, ``data.key = value``, instead (data is instance of
        this class).
        """
        if key not in dir(dict):
            self[key] = value
        else:
            raise AttributeError("Cannot overwrite the '%s' dict method" % key)

    def get(self, key):
        """Return value of attribute at 'key'. This is the method
        form of using, ``encase.child``. This can be used when you
        won't know a key name prior and need to use a variable for
        'key'.

        :param str key:
            Name of attribute whose value will be returned
        """
        return self.__getattr__(key)

    def set(self, key, value):
        """Set value of attribute at 'key'. This is the method
        form of using, ``encase.child = 'Value'``. This can be used
        when you won't know key name prior and need to use a
        variable for 'key'.

        :param str key:
            Name of attribute to set
        :param str value:
            Value to set for attribute
        """
        self.__setattr__(key, value)

    def _convert_list(self, existing_list):
        """Helper function for __init__. Loop through all items in
        a list recursively and convert any dictionaries into Encase
        objects.

        :param list existing_list:
            List of objects to potentially convert
        """
        L = []
        for item in existing_list:
            if isinstance(item, dict):
                L.append(Encase(item))
            elif isinstance(item, list):
                L.append(self._convert_list(item))
            else:
                L.append(item)
        return L
