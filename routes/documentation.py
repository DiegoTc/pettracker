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
            ul { list-style-type: square; }
            a { color: #0d6efd; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .card { background-color: #212529; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
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
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)