class FilterBuilder:
    not_clauses = ("neq", "nin", "missing")

    def handler(self, constraint, *args):
        fn_name = "_{0}_".format(constraint)
        fn = getattr(self, fn_name)
        return fn(*args)

    @staticmethod
    def is_nested_bool(field: str):
        if field.startswith("nested_bool"):
            return True
        else:
            return False

    @staticmethod
    def _eq_(*args):
        return {
            "term": {args[0]: args[1]}
        }

    def _neq_(self, *args):
        return self._eq_(*args)

    @staticmethod
    def _base_range_(condition, *args):
        return {
            "range": {
                args[0]: {condition: args[1]}
            }
        }

    def _gt_(self, *args):
        return self._base_range_("gt", *args)

    def _gte_(self, *args):
        return self._base_range_("gte", *args)

    def _lt_(self, *args):
        return self._base_range_("lt", *args)

    def _lte_(self, *args):
        return self._base_range_("lte", *args)

    @staticmethod
    def _between_(*args):
        values = args[1]
        assert isinstance(values, list) and len(values) == 2, \
            "Invalid between condition provided for {}".format(args[0])
        return {
            "range": {
                args[0]: {"gte": values[0], "lte": values[1]}
            }
        }

    @staticmethod
    def _inq_(*args):
        return {
            "terms": {args[0]: args[1]}
        }

    def _nin_(self, *args):
        return self._inq_(*args)

    @staticmethod
    def _exists_(*args):
        return {
            "exists": {"field": args[0]}
        }

    def _missing_(self, *args):
        return self._exists_(*args)

    @staticmethod
    def is_exists_clause(key, value):
        if key not in ("exists", "missing"):
            return False
        value = str(value).lower()
        if value not in ("true", "false"):
            raise SyntaxError("Invalid value provided in clause {}".format(key))
        if key == "exists" and str(value).lower() == "true":
            return True
        elif key == "missing" and str(value).lower() == "false":
            return True
        else:
            return False

    @staticmethod
    def is_missing_clause(key, value):
        if key not in ("exists", "missing"):
            return False
        value = str(value).lower()
        if value not in ("true", "false"):
            raise SyntaxError("Invalid value provided in clause {}".format(key))
        if key == "exists" and str(value).lower() == "false":
            return True
        elif key == "missing" and str(value).lower() == "true":
            return True
        else:
            return False

    def handle_nested_bool(self, clauses: dict):
        assert len(clauses) == 1, "nested_bool condition only supports a single boolean operation (or/and)."
        if clauses.get("and"):
            return {
                "bool": self._and_(clauses["and"])
            }
        elif clauses.get("or"):
            return {
                "bool": self._or_(clauses["or"])
            }
        else:
            raise SyntaxError("No boolean operator provided inside nested_bool.")

    def _bool_(self, clauses: dict):
        positives, negatives = list(), list()

        for field, constraints in clauses.items():
            assert isinstance(constraints, dict), "Invalid clause structure provided for inside {}".format(field)
            if self.is_nested_bool(field):
                positives.append(self.handle_nested_bool(constraints))
                continue
            for key, value in constraints.items():
                # Special handling for exists/missing clauses
                if self.is_exists_clause(key, value):
                    positives.append(self._exists_(field))
                elif self.is_missing_clause(key, value):
                    negatives.append(self._missing_(field))
                elif key in self.not_clauses:
                    negatives.append(self.handler(key, field, value))
                else:
                    positives.append(self.handler(key, field, value))
        return positives, negatives

    def _and_(self, clauses: dict):
        if not clauses:
            return {}
        must, must_not = self._bool_(clauses)
        return {
            "must": must,
            "must_not": must_not
        }

    def _or_(self, clauses: dict):
        if not clauses:
            return {}
        should, should_not = self._bool_(clauses)
        query = {
            "should": should,
            "minimum_should_match": 1
        }
        if len(should_not):
            query["should"].append({
                "bool": {
                    "must_not": should_not
                }
            })
        return query

    def __call__(self, data):
        return {
            "bool": {
                **self._and_(data.get("and")),
                **self._or_(data.get("or"))
            }
        }


build_filters = FilterBuilder()
