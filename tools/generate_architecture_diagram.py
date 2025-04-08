#!/usr/bin/env python3
"""
Pet Tracker Architecture Diagram Generator

This script generates a text-based representation of the Pet Tracker system architecture.
"""

def print_centered(text, width=80, char='-'):
    """Print text centered with characters on both sides"""
    text = f" {text} "
    padding = char * ((width - len(text)) // 2)
    print(f"{padding}{text}{padding}")

def print_box(title, content=None, width=40, height=5):
    """Print a box with title and optional content"""
    print("+" + "-" * (width - 2) + "+")
    print(f"|{title.center(width - 2)}|")
    
    if content:
        print("|" + " " * (width - 2) + "|")
        for line in content:
            if line:
                print(f"|{line.center(width - 2)}|")
            else:
                print("|" + " " * (width - 2) + "|")
    
    # Fill remaining lines
    remaining = height - (3 if not content else 2 + len(content))
    for _ in range(remaining):
        print("|" + " " * (width - 2) + "|")
    
    print("+" + "-" * (width - 2) + "+")

def print_component(name, width=20):
    """Print a small component box"""
    print("/" + "-" * (width - 2) + "\\")
    print(f"|{name.center(width - 2)}|")
    print("\\" + "-" * (width - 2) + "/")

def print_arrow(direction="down", length=3, label=None):
    """Print an arrow with optional label"""
    if direction == "down":
        for _ in range(length - 1):
            print("|".center(20))
        print("V".center(20))
    elif direction == "right":
        arrow = "--" * length + ">"
        if label:
            print(f"{arrow.center(20)}")
            print(f"{label.center(20)}")
        else:
            print(f"{arrow.center(20)}")
    elif direction == "left":
        arrow = "<" + "--" * length
        if label:
            print(f"{arrow.center(20)}")
            print(f"{label.center(20)}")
        else:
            print(f"{arrow.center(20)}")

def main():
    """Generate and print the architecture diagram"""
    print("\n")
    print_centered("PET TRACKER SYSTEM ARCHITECTURE", 100, "=")
    print_centered("Dual Protocol Support with Frontend and Backend Integration", 100, "-")
    print("\n")
    
    # Frontend and Backend side-by-side
    print(" " * 5 + "+------------------------------+" + " " * 15 + "+-------------------------------------+")
    print(" " * 5 + "|        Vue.js Frontend       |" + " " * 15 + "|      Flask Backend Application     |")
    print(" " * 5 + "+------------------------------+" + " " * 15 + "+-------------------------------------+")
    
    # Components in each
    print(" " * 5 + "|                              |" + " " * 15 + "|                                     |")
    print(" " * 5 + "|  - Auth Components           |" + " " * 15 + "|  - Auth Routes        - Models     |")
    print(" " * 5 + "|  - Pet Management            |" + " " * 15 + "|  - Pet Routes         - Services   |")
    print(" " * 5 + "|  - Device Management         |" + " " * 15 + "|  - Device Routes                   |")
    print(" " * 5 + "|  - Location Tracking         |" + " " * 15 + "|  - Location Routes                 |")
    print(" " * 5 + "|                              |" + " " * 15 + "|                                     |")
    print(" " * 5 + "+------------------------------+" + " " * 15 + "+-------------------------------------+")
    
    # Connection between Frontend and Backend
    print(" " * 44 + "^" + " " * 15 + "|")
    print(" " * 20 + "<---------HTTP/REST API------->" + " " * 15 + "|")
    print(" " * 44 + "|" + " " * 15 + "|")
    
    # Protocol Server on the right
    print(" " * 72 + "<---------+  +---------------------------+")
    print(" " * 72 + "          |  |    Protocol Server (TCP)  |")
    print(" " * 72 + "          |  +---------------------------+")
    print(" " * 72 + "          |  |                           |")
    print(" " * 72 + "    Data  |  |  - Protocol 808 Parser    |")
    print(" " * 72 + "  Updates |  |  - JT808 Parser           |")
    print(" " * 72 + "          |  |  - Socket Server          |")
    print(" " * 72 + "          |  |                           |")
    print(" " * 72 + "          |  +---------------------------+")
    print(" " * 72 + "          |             ^")
    print(" " * 72 + "          v             |")
    
    # Database in the middle
    print(" " * 30 + "+---------------------------+")
    print(" " * 30 + "|   PostgreSQL Database    |")
    print(" " * 30 + "+---------------------------+")
    print(" " * 30 + "|                          |")
    print(" " * 30 + "|  - Users    - Locations  |")
    print(" " * 30 + "|  - Pets     - Devices    |")
    print(" " * 30 + "|                          |")
    print(" " * 30 + "+---------------------------+")
    
    # Devices at the bottom right
    print(" " * 72 + "+---------------------------+")
    print(" " * 72 + "|     Tracking Devices      |")
    print(" " * 72 + "+---------------------------+")
    print(" " * 72 + "|                           |")
    print(" " * 72 + "|  - 808 Protocol Devices   |")
    print(" " * 72 + "|  - JT808 Protocol Devices |")
    print(" " * 72 + "|  - Device Simulator       |")
    print(" " * 72 + "|                           |")
    print(" " * 72 + "+---------------------------+")
    
    # Authentication service on the left
    print(" " * 5 + "+------------------------------+")
    print(" " * 5 + "|        Google OAuth          |")
    print(" " * 5 + "+------------------------------+")
    print(" " * 5 + "|     User Authentication      |")
    print(" " * 5 + "+------------------------------+")
    print(" " * 20 + "          |")
    print(" " * 20 + "          v")
    print(" " * 20 + "   Authentication Flow")
    
    # Legend
    print("\n")
    print_centered("LEGEND", 50, "-")
    print(" - Frontend: Vue.js application for user interface")
    print(" - Backend: Flask application with REST API endpoints")
    print(" - Database: PostgreSQL for data persistence")
    print(" - Protocol Server: TCP server handling both 808 and JT808 protocols")
    print(" - Devices: Physical or virtual GPS tracking devices")
    print(" - Google OAuth: External authentication service")
    print("\n")
    print_centered("DATA FLOW", 50, "-")
    print(" 1. Users authenticate via Google OAuth")
    print(" 2. Frontend communicates with Backend via REST API")
    print(" 3. Backend stores/retrieves data from PostgreSQL")
    print(" 4. GPS devices connect to Protocol Server via TCP")
    print(" 5. Protocol Server parses messages and updates location data")
    print(" 6. Protocol Server forwards data to Backend")
    print(" 7. Frontend displays location updates to users")
    print("\n")

if __name__ == "__main__":
    main()