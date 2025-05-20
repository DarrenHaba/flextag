from flextag.flextag import Section


class TestSection:

    def test_content_parsing(self):
        """Test content parsing based on type"""
        # Create minimal section for text type
        text_section = Section(
            section_id="text_sec",
            tags=[],
            paths=[],
            parameters={},
            type_name="raw",
            open_line=0,
            close_line=2,
            is_self_closing=False,
            all_lines=["[[text_sec]]", "plain text", "[[/text_sec]]"],
        )
        assert text_section.content == "plain text"

        # Create minimal section for yaml type
        yaml_section = Section(
            section_id="yaml_sec",
            tags=[],
            paths=[],
            parameters={},
            type_name="yaml",
            open_line=0,
            close_line=3,
            is_self_closing=False,
            all_lines=[
                "[[yaml_sec]]: yaml\n",
                "key: value\n",
                "items: [1,2,3]\n",
                "[[/yaml_sec]]\n",
            ],
        )
        assert yaml_section.content == {"key": "value", "items": [1, 2, 3]}

    def test_metadata_inheritance(self):
        """Test metadata inheritance from defaults"""
        section = Section(
            section_id="",
            tags=["#local"],
            paths=[".local"],
            parameters={"local": "value"},
            type_name="text",
            open_line=0,
            close_line=1,
            is_self_closing=False,
            all_lines=["[[]]", "[[/]]"],
        )

        # Set inherited values
        section.inherited_id = "default_id"
        section.inherited_tags = ["#default"]
        section.inherited_paths = [".default"]
        section.inherited_params = {"default": "value"}

        # Check combined results
        assert section.id == "default_id"  # Uses inherited when raw is empty
        assert sorted(section.tags) == sorted(["#default", "#local"])
        assert sorted(section.paths) == sorted([".default", ".local"])
        assert section.parameters == {"default": "value", "local": "value"}

    def test_type_inheritance(self):
        """Test type name inheritance behavior"""
        section = Section(
            section_id="sec",
            tags=[],
            paths=[],
            parameters={},
            type_name="raw",  # Default
            open_line=0,
            close_line=1,
            is_self_closing=False,
            all_lines=["[[sec]]", "[[/sec]]"],
        )

        # Should use raw type if specified
        assert section.type_name == "raw"

        # Should use inherited type only if raw type is empty/text
        section.inherited_type = "yaml"
        assert section.type_name == "yaml"
