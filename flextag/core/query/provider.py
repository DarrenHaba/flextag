from ...core.query.query import QueryParser


class QueryProvider:
    """Provider class for registering with manager"""

    def __init__(self):
        self._parser = QueryParser()

    def to_sql(self, query: str) -> str:
        """Convert FlexTag query to SQL"""
        return self._parser.parse_query(query)
