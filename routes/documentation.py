from flask import Blueprint, send_from_directory, render_template_string

doc_bp = Blueprint('documentation', __name__)

@doc_bp.route('/architecture')
def architecture():
    """Serve the system architecture diagram"""
    return send_from_directory('static', 'architecture.html')

@doc_bp.route('/architecture/ascii')
def architecture_ascii():
    """Serve an ASCII representation of the system architecture"""
    ascii_diagram = """
================================= PET TRACKER SYSTEM ARCHITECTURE =================================
------------------- Dual Protocol Support with Frontend and Backend Integration -------------------


     +------------------------------+               +-------------------------------------+
     |        Vue.js Frontend       |               |      Flask Backend Application     |
     +------------------------------+               +-------------------------------------+
     |                              |               |                                     |
     |  - Auth Components           |               |  - Auth Routes        - Models     |
     |  - Pet Management            |               |  - Pet Routes         - Services   |
     |  - Device Management         |               |  - Device Routes                   |
     |  - Location Tracking         |               |  - Location Routes                 |
     |                              |               |                                     |
     +------------------------------+               +-------------------------------------+
                                            ^               |
                    <---------HTTP/REST API------->               |
                                            |               |
                                                                        <---------+  +---------------------------+
                                                                                  |  |    Protocol Server (TCP)  |
                                                                                  |  +---------------------------+
                                                                                  |  |                           |
                                                                            Data  |  |  - Protocol 808 Parser    |
                                                                          Updates |  |  - JT808 Parser           |
                                                                                  |  |  - Socket Server          |
                                                                                  |  |                           |
                                                                                  |  +---------------------------+
                                                                                  |             ^
                                                                                  v             |
                              +---------------------------+
                              |   PostgreSQL Database    |
                              +---------------------------+
                              |                          |
                              |  - Users    - Locations  |
                              |  - Pets     - Devices    |
                              |                          |
                              +---------------------------+
                                                                        +---------------------------+
                                                                        |     Tracking Devices      |
                                                                        +---------------------------+
                                                                        |                           |
                                                                        |  - 808 Protocol Devices   |
                                                                        |  - JT808 Protocol Devices |
                                                                        |  - Device Simulator       |
                                                                        |                           |
                                                                        +---------------------------+
     +------------------------------+
     |        Google OAuth          |
     +------------------------------+
     |     User Authentication      |
     +------------------------------+
                    |
                    v
             Authentication Flow


---------------------------------------------- LEGEND ----------------------------------------------
 - Frontend: Vue.js application for user interface
 - Backend: Flask application with REST API endpoints
 - Database: PostgreSQL for data persistence
 - Protocol Server: TCP server handling both 808 and JT808 protocols
 - Devices: Physical or virtual GPS tracking devices
 - Google OAuth: External authentication service

---------------------------------------------- DATA FLOW ----------------------------------------------
 1. Users authenticate via Google OAuth
 2. Frontend communicates with Backend via REST API
 3. Backend stores/retrieves data from PostgreSQL
 4. GPS devices connect to Protocol Server via TCP
 5. Protocol Server parses messages and updates location data
 6. Protocol Server forwards data to Backend
 7. Frontend displays location updates to users
"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pet Tracker Architecture (ASCII)</title>
        <style>
            body {{ font-family: monospace; background-color: #121212; color: #f8f9fa; padding: 20px; }}
            pre {{ white-space: pre-wrap; }}
            h1 {{ color: #0d6efd; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Pet Tracker System Architecture (ASCII)</h1>
        <pre>{ascii_diagram}</pre>
        <p><a href="/architecture" style="color: #0d6efd;">View interactive HTML diagram</a></p>
    </body>
    </html>
    """
    
    return render_template_string(html)

@doc_bp.route('/documentation')
def documentation_home():
    """Documentation home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pet Tracker Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #f8f9fa; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            h1, h2 { color: #0d6efd; }
            h3 { color: #20c997; margin-top: 15px; }
            ul { list-style-type: square; }
            a { color: #0d6efd; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .card { background-color: #212529; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
            code { background-color: #0d1117; padding: 2px 5px; border-radius: 3px; color: #e83e8c; }
            table { width: 100%; border-collapse: collapse; margin: 15px 0; }
            th { text-align: left; padding: 8px; border-bottom: 1px solid #495057; color: #adb5bd; }
            td { padding: 8px; border-bottom: 1px solid #343a40; }
            tr:last-child td { border-bottom: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Pet Tracker System Documentation</h1>
            
            <div class="card">
                <h2>System Architecture</h2>
                <ul>
                    <li><a href="/architecture">Interactive Architecture Diagram</a></li>
                    <li><a href="/architecture/ascii">ASCII Architecture Diagram</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h2>API Endpoints</h2>
                <ul>
                    <li>Authentication: <code>/api/auth/*</code></li>
                    <li>Pets: <code>/api/pets/*</code></li>
                    <li>Devices: <code>/api/devices/*</code></li>
                    <li>Locations: <code>/api/locations/*</code></li>
                </ul>
            </div>
            
            <div class="card">
                <h2>Environment Configuration</h2>
                
                <h3>Backend Environment Variables</h3>
                <table>
                    <tr>
                        <th>Variable</th>
                        <th>Description</th>
                        <th>Default Value</th>
                    </tr>
                    <tr>
                        <td><code>DATABASE_URL</code></td>
                        <td>PostgreSQL database connection string</td>
                        <td>Provided by Replit</td>
                    </tr>
                    <tr>
                        <td><code>SESSION_SECRET</code></td>
                        <td>Secret key for session encryption</td>
                        <td>Generated or provided</td>
                    </tr>
                    <tr>
                        <td><code>GOOGLE_OAUTH_CLIENT_ID</code></td>
                        <td>Google OAuth client ID</td>
                        <td>Must be provided</td>
                    </tr>
                    <tr>
                        <td><code>GOOGLE_OAUTH_CLIENT_SECRET</code></td>
                        <td>Google OAuth client secret</td>
                        <td>Must be provided</td>
                    </tr>
                    <tr>
                        <td><code>PROTOCOL_808_PORT</code></td>
                        <td>TCP port for the protocol server</td>
                        <td>8080</td>
                    </tr>
                </table>
                
                <h3>Frontend Environment Variables</h3>
                <table>
                    <tr>
                        <th>Variable</th>
                        <th>Description</th>
                        <th>Default Value</th>
                    </tr>
                    <tr>
                        <td><code>VITE_API_BASE_URL</code></td>
                        <td>Base URL for API requests from the frontend</td>
                        <td>http://localhost:5000</td>
                    </tr>
                </table>
                
                <p>The <code>VITE_API_BASE_URL</code> is especially important as it defines where the frontend will send all API requests. In development, it points to localhost, but in production, it should point to your actual API domain.</p>
            </div>
            
            <div class="card">
                <h2>Protocols</h2>
                <ul>
                    <li>808 Protocol (Text-based)</li>
                    <li>JT808 Protocol (Binary)</li>
                    <li>Pet-specific extensions for both protocols</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>Development Tools</h2>
                <ul>
                    <li>Device Simulator: <code>python tools/device_simulator.py</code></li>
                    <li>API Test Suite: <code>python tools/test_api.py</code></li>
                </ul>
                
                <h3>Frontend-Backend Communication</h3>
                <p>The frontend communicates with the backend through REST API calls using the Axios library. The base URL for these calls is configured through the <code>VITE_API_BASE_URL</code> environment variable in the <code>frontend/.env</code> file.</p>
                
                <p>When deploying to production, you should update this variable to point to your production API endpoint. For example:</p>
                <code>VITE_API_BASE_URL=https://api.pettracker.yourdomain.com</code>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)