import os
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse

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


@mcp.custom_route("/", methods=["GET"])
async def homepage(request: Request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Seva Setu Portal</title>
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f3f6fb;
                color: #243247;
            }
            header {
                background: #124b8c;
                color: white;
                padding: 24px 8%;
            }
            header h1 { margin: 0 0 8px; }
            header p { margin: 0; }
            main {
                max-width: 1000px;
                margin: 35px auto;
                padding: 0 20px;
            }
            .welcome {
                background: white;
                padding: 28px;
                border-radius: 12px;
                box-shadow: 0 3px 14px #0000000d;
            }
            input {
                width: 100%;
                padding: 13px;
                margin-top: 15px;
                border: 1px solid #ccd5e0;
                border-radius: 7px;
                font-size: 16px;
            }
            .services {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 18px;
                margin-top: 24px;
            }
            .card {
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 3px 14px #0000000d;
            }
            .card a {
                display: inline-block;
                margin-top: 12px;
                background: #124b8c;
                color: white;
                padding: 10px 14px;
                text-decoration: none;
                border-radius: 6px;
            }
            .card a:hover { background: #0b3566; }
            footer {
                text-align: center;
                padding: 25px;
                color: #586579;
                font-size: 14px;
            }
            .notice {
                font-size: 13px;
                color: #586579;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Seva Setu Portal</h1>
            <p>Your starting point for citizen services</p>
        </header>

        <main>
            <section class="welcome">
                <h2>Welcome to Seva Setu</h2>
                <p>Explore government service resources and find useful links
                   in one place.</p>
                <label for="search">Search for a service</label>
                <input id="search" type="search"
                    placeholder="Try scholarship or government services..."
                    oninput="filterServices()">
            </section>

            <section class="services" id="services">
                <article class="card">
                    <h3>National Scholarship Portal</h3>
                    <p>Find information about scholarship opportunities.</p>
                    <a href="https://scholarships.gov.in"
                       target="_blank" rel="noopener noreferrer">
                       Visit official website
                    </a>
                </article>

                <article class="card">
                    <h3>UMANG</h3>
                    <p>Explore access to a range of government services.</p>
                    <a href="https://web.umang.gov.in"
                       target="_blank" rel="noopener noreferrer">
                       Visit official website
                    </a>
                </article>
            </section>

            <p class="notice">
                This is a demonstration project, not an official government
                website. Please verify eligibility and application details
                on the relevant official websites.
            </p>
        </main>

        <footer>Seva Setu Portal | Citizen Help AI Prototype</footer>

        <script>
            function filterServices() {
                const query = document.getElementById("search")
                    .value.toLowerCase().trim();

                document.querySelectorAll(".card").forEach(card => {
                    card.style.display =
                        card.innerText.toLowerCase().includes(query)
                        ? "" : "none";
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
