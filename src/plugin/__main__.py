from mcp.server.fastmcp import FastMCP

from plugin.deduplicate_contacts import deduplicate_contacts

mcp = FastMCP("contact-deduplicator")

IMPLEMENTATIONS = {
    "deduplicate_contacts": deduplicate_contacts,
}

for implementation in IMPLEMENTATIONS.values():
    mcp.tool()(implementation)

if __name__ == "__main__":
    mcp.run(transport="stdio")