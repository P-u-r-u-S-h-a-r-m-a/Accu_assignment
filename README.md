**Prerequisites**
1. Python
2. Docker
3. Docker Compose

# Accu Assignment Project Setup

Follow these steps to run the Django project using Docker:

## 1. Clone the Repository
```bash
git clone https://github.com/P-u-r-u-S-h-a-r-m-a/Accu_assignment.git

2. Navigate to the Project Directory

cd Accu_assignment

3. Build the Docker Containers

docker-compose build

4. Start the Containers

docker-compose up

Alternatively, you can also run the project by cloning the repository, creating a virtual environment, and installing all dependencies.

Please before using any api 
1.Before making POST requests (e.g., login, sending a friend request), retrieve a CSRF token by sending a GET request to /csrf_cookie/.
2.Please include the CSRF token in the X-CSRFToken
  header for all subsequent POST requests.

for Postman collection open SocialMedia.postman_collection via postman
