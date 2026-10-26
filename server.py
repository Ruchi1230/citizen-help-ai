
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Citizen Help AI",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True
)

SCHEMES = [
    {
        "name": "National Scholarship Portal",
        "purpose": "Find scholarship opportunities",
        "website": "https://scholarships.gov.in"
    },
    {
        "name": "UMANG",
        "purpose": "Access government services",
        "website": "https://web.umang.gov.in"
    }
]

@mcp.tool()
def search_citizen_services(keyword: str) -> list[dict]:
    """Search example citizen services by name or purpose."""
    keyword = keyword.lower().strip()
    return [
        scheme for scheme in SCHEMES
        if keyword in scheme["name"].lower()
        or keyword in scheme["purpose"].lower()
    ]

@mcp.tool()
def get_application_guidance(service_name: str) -> dict:
    """Get basic information about a citizen service."""
    for scheme in SCHEMES:
        if service_name.lower() in scheme["name"].lower():
            return scheme
    return {"message": "Service not found. Please check the name."}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
