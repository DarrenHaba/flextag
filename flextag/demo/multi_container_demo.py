import flextag


def demo_multi_container():
    """Multi-container filtering and search demo"""
    # Create sample containers
    container1 = """[[PARAMS fmt="text"]]
[[META title="Production Config" version="1.0" #production .config]]

[[SEC:db #database .sys.db fmt="json"]]
{
    "host": "prod-db",
    "port": 5432
}
[[/SEC]]"""

    container2 = """[[PARAMS fmt="text"]]
[[META title="Development Config" version="1.0" #development .config]]

[[SEC:db #database .sys.db fmt="json"]]
{
    "host": "dev-db",
    "port": 5432
}
[[/SEC]]"""

    try:
        print("=== Multi-Container Demo ===")

        # Parse containers
        containers = [flextag.parse(container1), flextag.parse(container2)]

        # Create container manager
        manager = flextag.ContainerManager(containers)
        print(f"\nLoaded {len(containers)} containers")

        # Filter by metadata
        prod_containers = manager.filter("#production")
        print(f"\nFound {len(prod_containers.containers)} production containers")

        # Search across filtered containers
        db_sections = prod_containers.search("#database")
        print(f"\nFound {len(db_sections)} database sections in production")

        for section in db_sections:
            print(f"\nDatabase section:")
            print(f"  ID: {section.id}")
            print(f"  Content: {section.content}")

        # Chain operations
        dev_db = manager.filter("#development").search(".sys.db")
        print(f"\nFound {len(dev_db)} development database sections")

    except Exception as e:
        print(f"Error in demo: {str(e)}")


if __name__ == "__main__":
    print("Running FlexTag Demo\n")
    print("\n" + "=" * 50 + "\n")
    demo_multi_container()
