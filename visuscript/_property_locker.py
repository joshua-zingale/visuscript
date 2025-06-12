from typing import Iterable
class LockedPropertyError(ValueError):
    def __init__(self, obj: object, property: str):
        message = f"'{property}' on object of type {type(obj).__name__} is already locked."
        super().__init__(message)

class PropertyLocker:
    def __init__(self, locks: dict[object, Iterable[str]] | None = None):
        self._map: dict[object, set[str]] = dict()
        if not locks is None:
            for obj, properties in locks.items():
                self._map[obj] = set(properties)


    def add(self, obj: object, property: str, ignore_conflicts = False):
        """Raises LockedPropertyError if the property is already locked by this PropertyLocker."""
        if not ignore_conflicts and self.locks(obj, property):
            raise LockedPropertyError(obj, property)        
        self._map[obj] = self._map.get(obj, set()).union(set([property]))

    def update(self, other: "PropertyLocker", ignore_conflicts = False):
        """Merges this PropertyLocker with another in place. Raises LockedPropertyError if the two PropertyLockers lock one or more of the same properties on the same object."""
        for obj in other._map:
            for property in other._map[obj]:
                self.add(obj, property, ignore_conflicts=ignore_conflicts)

    def locks(self, obj: object, property: str) -> bool:
        """Returns whether this :class:`PropertyLocker` locks the specified property.

        :param obj: The object for which the property's lock is checked.
        :type obj: object
        :param property: The property for which the lock is checked, defaults to checking if any of the properties is locked
        :type property: str, optional
        :return: True if this :class:`PropertyLocker` locks the specified property; else False
        :rtype: bool
        """
        lock_set = self._map.get(obj, set())        
        return property in lock_set
