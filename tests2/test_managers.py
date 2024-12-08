import pytest
from typing import Dict, Any
from flextag.core.managers.registry import RegistryManager
from flextag.core.managers.parser import ParserManager
from flextag.core.managers.search import SearchManager
from flextag.core.managers.transport import TransportManager
from flextag.core.parsers.content import JSONParser, YAMLParser, TextParser
from flextag.core.search.algorithms import ExactMatchAlgorithm, WildcardMatchAlgorithm
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.core.types.metadata import Metadata
from flextag.exceptions import FlexTagError

# Add more test cases?
# Add integration tests between managers?
# Add performance benchmarks?


class TestRegistryManager:
    """Test registry manager functionality"""

    @pytest.fixture
    def registry_manager(self):
        return RegistryManager()

    def test_registry_creation(self, registry_manager):
        """Test creating new registries"""
        registry_manager.create_registry("test")
        assert "test" in registry_manager.list_registries()

        # Test duplicate creation
        with pytest.raises(FlexTagError):
            registry_manager.create_registry("test")

    def test_registration(self, registry_manager):
        """Test registering implementations"""
        class TestImpl:
            pass

        registry_manager.register("test_registry", "test_impl", TestImpl)

        # Verify registration
        impl = registry_manager.get("test_registry", "test_impl")
        assert impl == TestImpl

        # Test getting nonexistent implementation
        with pytest.raises(FlexTagError):
            registry_manager.get("test_registry", "nonexistent")

    def test_unregistration(self, registry_manager):
        """Test unregistering implementations"""
        registry_manager.register("test_registry", "test_impl", object)
        registry_manager.unregister("test_registry", "test_impl")

        # Verify removal
        with pytest.raises(FlexTagError):
            registry_manager.get("test_registry", "test_impl")

    def test_list_implementations(self, registry_manager):
        """Test listing registered implementations"""
        registry_manager.register("test_registry", "impl1", object)
        registry_manager.register("test_registry", "impl2", object)

        impls = registry_manager.list_registered("test_registry")
        assert "impl1" in impls
        assert "impl2" in impls


class TestParserManager:
    """Test parser manager functionality"""

    @pytest.fixture
    def parser_manager(self):
        return ParserManager()

    @pytest.fixture
    def sample_content(self):
        return """[[PARAMS fmt="json"]]
[[META:config #system]]
[[SEC:data fmt="json"]]
{"key": "value"}
[[/SEC]]"""

    def test_content_parser_registration(self, parser_manager):
        """Test registering content parsers"""
        parser_manager.register_content_parser("json", JSONParser())
        parser_manager.register_content_parser("yaml", YAMLParser())

        # Test getting registered parser
        json_parser = parser_manager.get_content_parser("json")
        assert isinstance(json_parser, JSONParser)

        # Test getting nonexistent parser
        with pytest.raises(FlexTagError):
            parser_manager.get_content_parser("nonexistent")

    def test_container_parsing(self, parser_manager, sample_content):
        """Test parsing complete container"""
        parser_manager.register_container_parser(ContainerParser())
        parser_manager.register_content_parser("json", JSONParser())

        container = parser_manager.parse_container(sample_content)
        assert container.metadata.id == "config"
        assert "system" in container.metadata.tags
        assert len(container.sections) == 1
        assert container.sections[0].metadata.id == "data"

    def test_section_parsing(self, parser_manager):
        """Test parsing individual section"""
        parser_manager.register_section_parser(SectionParser())
        parser_manager.register_content_parser("json", JSONParser())

        content = '''[[SEC:test fmt="json"]]
{"key": "value"}
'''
        section = parser_manager.parse_section(content, "json")
        assert section.metadata.id == "test"
        assert section.content["key"] == "value"


class TestSearchManager:
    """Test search manager functionality"""

    @pytest.fixture
    def search_manager(self):
        manager = SearchManager()
        manager.register_algorithm("exact", ExactMatchAlgorithm)
        manager.register_algorithm("wildcard", WildcardMatchAlgorithm)
        return manager

    @pytest.fixture
    def test_container(self):
        """Create test container with sections"""
        container = Container.create()

        # Add sections
        section1 = Section.create()
        section1.metadata = Metadata(
            id="config",
            tags=["system", "database"],
            paths=["sys.config"]
        )

        section2 = Section.create()
        section2.metadata = Metadata(
            id="api",
            tags=["service", "web"],
            paths=["sys.api"]
        )

        container.add_section(section1)
        container.add_section(section2)
        return container

    def test_algorithm_registration(self, search_manager):
        """Test registering search algorithms"""
        # Test setting active algorithm
        search_manager.set_active_algorithm("exact")

        # Test invalid algorithm
        with pytest.raises(SearchError):
            search_manager.set_active_algorithm("nonexistent")

    def test_auto_algorithm_selection(self, search_manager):
        """Test automatic algorithm selection"""
        # Simple query should use exact match
        search_manager.auto_select_algorithm("#system")
        assert isinstance(search_manager._active_algorithm, ExactMatchAlgorithm)

        # Wildcard query should use wildcard match
        search_manager.auto_select_algorithm("#sys*")
        assert isinstance(search_manager._active_algorithm, WildcardMatchAlgorithm)

    def test_find_operations(self, search_manager, test_container):
        """Test find operations"""
        # Test find_first
        section = search_manager.find_first(test_container, "#system")
        assert section.metadata.id == "config"

        # Test find all
        sections = search_manager.find(test_container, "#service")
        assert len(sections) == 1
        assert sections[0].metadata.id == "api"

    def test_container_filtering(self, search_manager, test_container):
        """Test container filtering"""
        containers = [test_container]

        # Filter by metadata
        test_container.metadata.tags.append("prod")
        filtered = search_manager.filter(containers, "#prod")
        assert len(filtered) == 1

        # Filter with no matches
        filtered = search_manager.filter(containers, "#staging")
        assert len(filtered) == 0


class TestTransportManager:
    """Test transport manager functionality"""

    @pytest.fixture
    def transport_manager(self):
        return TransportManager()

    @pytest.fixture
    def test_container(self):
        """Create test container"""
        container = Container.create()
        container.metadata = Metadata(id="test", tags=["prod"])
        return container

    def test_encoding_configuration(self, transport_manager):
        """Test encoding configuration"""
        # Test setting valid encoding
        transport_manager.set_default_encoding("base64")

        # Test invalid encoding
        with pytest.raises(TransportError):
            transport_manager.set_default_encoding("invalid")

    def test_compression_configuration(self, transport_manager):
        """Test compression configuration"""
        # Register compressor
        transport_manager.register_compressor("gzip", GzipCompressor)

        # Test setting valid compression
        transport_manager.set_default_compression("gzip")

        # Test invalid compression
        with pytest.raises(TransportError):
            transport_manager.set_default_compression("invalid")

    def test_transport_operations(self, transport_manager, test_container):
        """Test transport operations"""
        # Register required components
        transport_manager.register_transport_container(TransportContainer)
        transport_manager.register_compressor("gzip", GzipCompressor)
        transport_manager.set_default_encoding("base64")

        # Test transport conversion
        transport_data = transport_manager.to_transport(test_container)
        assert isinstance(transport_data, str)
        assert transport_data.startswith("FLEXTAG__META_")

        # Test transport parsing
        restored = transport_manager.from_transport(transport_data)
        assert restored.metadata.id == test_container.metadata.id
        assert restored.metadata.tags == test_container.metadata.tags


@pytest.mark.parametrize("manager_cls,expected_features", [
    (RegistryManager, ["create_registry", "register", "unregister", "get"]),
    (ParserManager, ["parse_container", "parse_section", "register_content_parser"]),
    (SearchManager, ["find", "find_first", "filter", "register_algorithm"]),
    (TransportManager, ["to_transport", "from_transport", "register_compressor"])
])
def test_manager_interfaces(manager_cls, expected_features):
    """Test manager interfaces implement required features"""
    manager = manager_cls()
    for feature in expected_features:
        assert hasattr(manager, feature)


def test_manager_isolation():
    """Test managers maintain proper isolation"""
    registry = RegistryManager()
    parser = ParserManager()
    search = SearchManager()
    transport = TransportManager()

    # Each manager should maintain its own state
    registry.create_registry("test")
    assert "test" not in parser.__dict__
    assert "test" not in search.__dict__
    assert "test" not in transport.__dict__
