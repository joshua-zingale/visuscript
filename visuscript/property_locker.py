class LockedPropertyError(ValueError):
    def __init__(self, obj: object, property: str):
        message = f"'{property}' on object of type {type(obj)} is already locked."
        super().__init__(message)

class PropertyLocker:
    ALL_PROPERTIES = "*"
    """Signifies that all properties are locked for this object."""

    def __init__(self):
        self._map: dict[object, set[str]] = dict()

    def add(self, obj: object, property: str = ALL_PROPERTIES, ignore_conflicts = False):
        """Raises LockedPropertyError if the property is already locked by this PropertyLocker."""

        self._map[obj] = self._map.get(obj, set())

        if not ignore_conflicts:
            if PropertyLocker.ALL_PROPERTIES in self._map[obj]:
                raise LockedPropertyError(obj, property)
            if property == PropertyLocker.ALL_PROPERTIES and len(self._map[obj]) > 0:
                raise LockedPropertyError(obj, property)
            if property in self._map[obj]:
                raise LockedPropertyError(obj, property)
    
        self._map[obj] = self._map[obj].union(set([property]))

    def update(self, other: "PropertyLocker", ignore_conflicts = False):
        """Merges this PropertyLocker with another in place. Raises LockedPropertyError if the two PropertyLockers lock one or more of the same properties on the same object."""

        for obj in other._map:
            for property in other._map[obj]:
                self.add(obj, property, ignore_conflicts=ignore_conflicts)