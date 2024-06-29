# Azure-Flask-Web-App

Repository: Online Survey App
Description

This repository contains the source code for an online survey application built using Python Flask. The app allows users to create, distribute, and analyze surveys easily. It is designed to be scalable and user-friendly, offering a seamless experience for survey creators and respondents alike.
Features

  * User Authentication: Secure user registration and login system.
  * Survey Creation: Intuitive interface for creating and customizing surveys with various question types.
  * Response Collection: Collect responses in real-time and ensure data integrity.
  * Data Analysis: Tools for visualizing survey results and exporting data.
  * Responsive Design: Mobile-friendly design to ensure accessibility across devices.
  * Email Notifications: Automated notifications for survey responses and important updates.

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
