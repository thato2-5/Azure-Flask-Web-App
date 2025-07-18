# Azure-Flask-Web-App

Repository: FHS Visitor Management Dashboard
Description

This repository contains the source code for the FHS visitor management dashboard built using Python Flask. 
# Functionality:

   The /api/visitors/export endpoint generates a CSV file with all visitor data

   It respects the same filters as the other endpoints

   The browser will automatically download the file when the endpoint is called

# Filtering Capabilities:

   Date range filtering (start and end dates)

   Purpose filtering

   Signed-in-only filtering

   All filters are applied consistently across all endpoints

# Dashboard Controls:

   Date pickers for selecting date ranges

   Dropdown with all available purposes

   Apply Filters button to refresh data

   Export Data button to download CSV

# Backend Changes:

   All endpoints now support filtering

   New endpoint to get unique purposes for the filter dropdown

# Entity Diagram(Database Schema)
``` mermaid
erDiagram
    VISITORS {
        int id PK
        varchar(100) name
        varchar(100) company
        varchar(20) phone
        varchar(100) email
        varchar(255) purpose
        datetime time_in
        datetime time_out
        varchar(100) vehicleRegistrationNumber
        text signature
        tinyint is_synced
    }
```

# System Flowchart
``` mermaid
flowchart TD
    A[Visitor Arrives] --> B[Check-In Process]
    B --> C{Input Details}
    C -->|Form| D[Save to Database]
    D --> E[Display Confirmation]
    A --> F[Visitor Departs]
    F --> G[Check-Out Process]
    G --> H{Update Record}
    H --> I[Set Time Out]
    I --> J[Generate Report]
```

# API Sequence Diagram
``` mermaid
sequenceDiagram
    participant Frontend
    participant Backend
    participant Database
    
    Frontend->>Backend: POST /api/visitors (Check-In)
    Backend->>Database: INSERT visitor
    Database-->>Backend: Success
    Backend-->>Frontend: 201 Created
    
    Frontend->>Backend: GET /api/visitors (List)
    Backend->>Database: SELECT * FROM visitors
    Database-->>Backend: Data
    Backend-->>Frontend: 200 OK
    
    Frontend->>Backend: PUT /api/visitors/:id (Check-Out)
    Backend->>Database: UPDATE time_out
    Database-->>Backend: Success
    Backend-->>Frontend: 200 OK
```

# Class Diagram
``` mermaid
classDiagram
    class Visitor {
        +id: int
        +name: str
        +company: str
        +phone: str
        +email: str
        +purpose: str
        +time_in: datetime
        +time_out: datetime
        +vehicleRegistrationNumber: str
        +signature: str
        +is_synced: bool
        +to_dict(): dict
    }


    class VisitorManagementApp {
        -db: SQLAlchemy
        +create_visitor()
        +get_visitors()
        +sign_out_visitor()
        +generate_report()
    }
    
    VisitorManagementApp --> Visitor: Manages
```

Getting Started
Prerequisites

  * Python 3.x
  * Git

Installation

  Clone the repository:

    git clone https://github.com/thato2-5/Azure-Flask-Web-App.git
    cd Azure-Flask-Web-App

Create and activate a virtual environment:

    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install dependencies:

    pip install -r requirements.txt

Set up the database:

    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade

Run the application locally:

    flask run

Deployment
Deploy to Azure App Service

  Login to Azure:

    az login

Create a resource group:

    az group create --name myResourceGroup --location eastus

Create an App Service plan:

    az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku FREE

Create a web app:

    az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myUniqueSurveyAppName --runtime "PYTHON|3.8"

Deploy the application:

    az webapp up --name myUniqueSurveyAppName --resource-group myResourceGroup

Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.
License

This project is licensed under the MIT License.
Acknowledgments

    Flask Documentation: https://flask.palletsprojects.com/
    Azure Documentation: https://docs.microsoft.com/en-us/azure/
    Bootstrap: https://getbootstrap.com/
