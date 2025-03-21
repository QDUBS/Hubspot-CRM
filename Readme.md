# HubSpot CRM Integration

## Project Overview

This project provides an API for managing contacts, deals, and support tickets in HubSpot. It allows users to:

- Create and update contacts.
- Create, update, and link deals with contacts.
- Create and link support tickets to contacts and deals.
- Retrieve recent CRM objects like contacts, deals, and tickets.

This project leverages Flask for the backend and integrates with HubSpot's CRM system to automate and streamline the management of contacts, deals, and tickets.

## Installation and setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/qdubs/hubspot-crm-integration.git
   cd hubspot-crm-integration
   ```

2. **Set up virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate  # For Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables in a `.env` file**:

   ```env
   FLASK_ENV=
   FLASK_APP=
   FLASK_RUN_HOST=

   SECRET_KEY=
   JWT_SECRET_KEY=

   DATABASE_URL=

   HUBSPOT_CLIENT_ID=<client_id>
   HUBSPOT_CLIENT_SECRET=<client_secret>
   HUBSPOT_REFRESH_TOKEN=<refresh_token>
   ```

5. **Set up database and make migrations**:
   - Firstly, ensure that you have a PostgreSQL server running on your local machine
   - Configure your database credentials in the `.env` file:

     ```
     DATABASE_URL=postgresql://username:password@host:port/dbname
     ```
   
   - Run alembic to make migrations to the database

   ```
   alembic revision --autogenerate -m "Description of changes"
   alembic upgrade head
   alembic current # Optional
   alembic downgrade <revision_id> # To revert to a previous migration
   ```

6. **Access the App**:
   - API available at http://localhost:5000
   - Swagger Documentation available at http://localhost:5000/docs
   - Health check at http://localhost:5000/health


## Dockerisation and Deployment

1. **Build the Docker image**
   To dockerize the application, we need to build a Docker image. The project comes with a Dockerfile that sets up the environment and installs the necessary dependencies.

   - First, make sure Docker is installed on your machine. If it's not installed, follow the instructions on the Docker website to install Docker.

   - Next, in the root directory of the project, build the Docker image:

   ```
   docker build -t hubspot-crm-api .
   ```

2. **Run the Docker container**
   Once the Docker image is built, you can run the application in a container using the following command:

   ```
   docker run -d -p 5000:5000 --env-file .env crm-api
   ```

   This will run the Flask app inside a Docker container and map it to port 5000 on your local machine.

3. **Verify the app is running**
   Verify that the application is running on http://localhost:5000.
   

## Endpoints

- **Create or update a contact**:
  **Endpoint**: `/api/create_contact`
  **Method**: POST
  **Description**: Create a new contact or update an existing contact.
  **Request Body**:

  ```
  {
      "properties": {
         "email": "superjones@gmail.com",
         "firstname": "Jones",
         "lastname": "Moore",
         "phone": "+1234567890"
      }
   }
  ```

  **Request Body**: Returns the created or updated contact object.

- **Create or update a deal**:
  **Endpoint**: `/api/create_deal`
  **Method**: POST
  **Description**: Create or update a deal and link it to a contact.
  **Request Body**:

  ```
  {
      "properties": {
         "dealname": "Acme Corporation - Subscription Renewal",
         "amount": 1500,
         "pipeline": "default",
         "dealstage": "appointmentscheduled",
         "description": "Annual subscription renewal for Acme Corporation.",
         "contact_id": "12345"
      }
   }
  ```

  **Request Body**: Returns the created or updated deal object.

- **Create a new support ticket**:
  **Endpoint**: `/api/create_ticket`
  **Method**: POST
  **Description**: Create a new support ticket and link it to the appropriate contact and deal.
  **Request Body**:

  ```
  {
      "properties": {
         "subject": "Support Ticket Subject",
         "description": "Ticket Description",
         "category": "Category",
         "pipeline": "0",  // assuming pipelineId=0 is correct for your use case
         "hs_ticket_priority": "HIGH",
         "hs_pipeline_stage": "1",  // Valid stage ID (1, 2, 3, or 4)
         "hs_pipeline": "0",
         "contact_id": "107739060800"
      },
      "associations": [
         {
            "to": {
            "id": "107739060800"
            },
            "types": [
            {
               "associationCategory": "HUBSPOT_DEFINED",
               "associationTypeId": 16
            }
            ]
         }
      ]
   }
  ```

  **Request Body**: Returns the created support ticket object.

- **Retrieve New CRM Objects**:
  **Endpoint**: `/api/new_crm_objects`
  **Method**: GET
  **Description**: Get a list of recent CRM objects (contacts, deals, tickets).
  **Query Parameters**:
  - `page`: The page number (default: 1)
  - `page_size`: The number of items per page (default: 10)
    **Response**: Returns a JSON object containing the recent contacts, deals, and tickets.

## Running Tests

1. **Set Up Test Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest pytest-cov
   ```

2. **Run All Tests**:

   ```bash
   python -m pytest
   ```

3. **Run Specific Test Categories**:
   ```bash
   python -m pytest tests/unit/       # Unit tests only
   python -m pytest tests/integrations/ # Integration tests only
   python -m pytest -v                 # Verbose output
   python -m pytest --cov=app          # With coverage
   ```

## Troubleshooting and Logs

1. **Error 401 - Unauthorized**:

   - Check if your `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET`, and `HUBSPOT_REFRESH_TOKEN` are correct.
   - The access token may have expired. The app automatically handles token refresh, but check the logs for any issues.

2. **Error 400 - Bad Request**:

   - Ensure the request body contains all the required fields. Refer to the API documentation for the expected fields.

3. **API Rate Limiting**:

   - HubSpot imposes rate limits on their API. If you exceed the limits, you may receive a 429 Too Many Requests error. Check the HubSpot API documentation for the rate limits.

4. **Database Connection**: Verify port 5432 is available for container communication

5. **Test Database Issues**: Delete test.db and restart tests if database errors occur

6. **View Logs**: Logs are available in the `/logs` folder


## Swagger Documentation

The API is documented using Swagger UI. Once you run the app, you can access the interactive Swagger UI at:

```
http://localhost:5000/docs
```
