import os
import hmac
import hashlib
import time
from urllib.parse import parse_qs

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
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

ADMIN_COOKIE = "sevasetu_admin_session"
SESSION_DURATION = 3600


def create_session_signature(timestamp: str) -> str:
    secret = os.environ.get("SECRET_KEY", "")
    username = os.environ.get("ADMIN_USERNAME", "")
    message = f"{username}:{timestamp}".encode()
    return hmac.new(
        secret.encode(), message, hashlib.sha256
    ).hexdigest()


def is_admin_logged_in(request: Request) -> bool:
    username = os.environ.get("ADMIN_USERNAME", "")
    secret = os.environ.get("SECRET_KEY", "")
    cookie = request.cookies.get(ADMIN_COOKIE, "")

    if not username or len(secret) < 32 or "." not in cookie:
        return False

    timestamp, signature = cookie.split(".", 1)

    if not timestamp.isdigit():
        return False

    if time.time() - int(timestamp) > SESSION_DURATION:
        return False

    expected = create_session_signature(timestamp)
    return hmac.compare_digest(signature, expected)


@mcp.custom_route("/admin/login", methods=["GET", "POST"])
async def admin_login(request: Request):
    username = os.environ.get("ADMIN_USERNAME", "")
    password = os.environ.get("ADMIN_PASSWORD", "")
    secret = os.environ.get("SECRET_KEY", "")

    if not username or not password or len(secret) < 32:
        return HTMLResponse(
            "Admin login is not configured. Check Render environment variables.",
            status_code=503
        )

    error = ""

    if request.method == "POST":
        body = (await request.body()).decode("utf-8", errors="replace")
        form = parse_qs(body)
        entered_username = form.get("username", [""])[0]
        entered_password = form.get("password", [""])[0]

        valid_username = hmac.compare_digest(
            entered_username, username
        )
        valid_password = hmac.compare_digest(
            entered_password, password
        )

        if valid_username and valid_password:
            timestamp = str(int(time.time()))
            signature = create_session_signature(timestamp)

            response = RedirectResponse("/admin", status_code=303)
            response.set_cookie(
                ADMIN_COOKIE,
                f"{timestamp}.{signature}",
                max_age=SESSION_DURATION,
                httponly=True,
                secure=True,
                samesite="lax",
                path="/admin"
            )
            return response

        error = "Invalid username or password."

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Administrator Login | Seva Setu</title>
      <style>
        body { font-family: Arial; background: #f3f6fb; padding: 40px 16px; }
        main { max-width: 380px; margin: 50px auto; background: white;
               padding: 28px; border-radius: 12px; }
        input, button { box-sizing: border-box; width: 100%; padding: 12px;
                        margin: 9px 0; }
        button { background: #124b8c; color: white; border: 0;
                 border-radius: 6px; cursor: pointer; }
        .error { color: #b42318; }
      </style>
    </head>
    <body>
      <main>
        <h2>Administrator Login</h2>
        <p>Sign in to the Seva Setu prototype.</p>
        <p class="error">ERROR_MESSAGE</p>
        <form method="post" action="/admin/login">
          <label for="username">Username</label>
          <input id="username" name="username" required autocomplete="username">
          <label for="password">Password</label>
          <input id="password" name="password" type="password"
                 required autocomplete="current-password">
          <button type="submit">Log in</button>
        </form>
      </main>
    </body>
    </html>
    """
    html = html.replace("ERROR_MESSAGE", error)
    return HTMLResponse(html)


@mcp.custom_route("/admin", methods=["GET"])
async def admin_dashboard(request: Request):
    if not is_admin_logged_in(request):
        return RedirectResponse("/admin/login", status_code=303)

    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>Seva Setu Admin</title></head>
    <body style="font-family:Arial;margin:40px">
      <h1>Seva Setu Admin Dashboard</h1>
      <p>You are logged in successfully.</p>
      <p>This is a prototype dashboard. Service-management features
         have not been implemented yet.</p>
      <form method="post" action="/admin/logout">
        <button type="submit">Log out</button>
      </form>
    </body>
    </html>
    """)


@mcp.custom_route("/admin/logout", methods=["POST"])
async def admin_logout(request: Request):
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie(ADMIN_COOKIE, path="/admin")
    return response

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
