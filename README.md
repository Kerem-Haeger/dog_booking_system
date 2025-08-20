
# Dog Booking System

**Live Version:** [Dog Booking System](https://your-deployment-url.com)  
**Repository:** [GitHub Repo](https://github.com/Kerem-Haeger/dog_booking_system)  
**Author:** [Kerem Haeger](https://github.com/Kerem-Haeger)

![Dog Booking System](documentation/features/dashboard/dashboard.png)

---

## About

The **Dog Booking System** is a full-featured pet grooming and service management platform tailored for grooming businesses. It simplifies the management of clients, pets, appointments, and staff through role-based access control. The primary goal is to streamline daily operations, reduce scheduling conflicts, and enhance the client experience.

---

## User Experience Design

### Strategy

The system was designed with simplicity and clarity in mind. By focusing on the specific needs of grooming businesses, it offers intuitive dashboards, smart scheduling, and seamless client interaction. Role-based interfaces ensure that each user type—manager, employee, or client—has access only to relevant tools and views.

### Target Audience

- **Managers**: Oversee operations, manage users and services, approve appointments and pet profiles.
- **Employees**: View and manage their appointment schedules, update statuses, and access client/pet info.
- **Clients**: Register pets, request services, track appointments, and manage profiles.

### User Stories

User stories are linked to the issue tracker in the repository and are grouped by user type. They reflect real-world goals and expected behaviors.

#### First-Time Visitors

| ID | Story |
|----|-------|
| [#1](https://github.com/Kerem-Haeger/dog_booking_system/issues/1) | Understand the purpose of the application. |
| [#2](https://github.com/Kerem-Haeger/dog_booking_system/issues/2) | Navigate the interface with ease. |
| [#3](https://github.com/Kerem-Haeger/dog_booking_system/issues/3) | Register an account. |
| [#4](https://github.com/Kerem-Haeger/dog_booking_system/issues/4) | Recognize the value of the service. |

#### Frequent Users

| ID | Story |
|----|-------|
| [#5](https://github.com/Kerem-Haeger/dog_booking_system/issues/5) | Log in to a personalized dashboard. |
| [#6](https://github.com/Kerem-Haeger/dog_booking_system/issues/6) | Log in/out securely. |
| [#7](https://github.com/Kerem-Haeger/dog_booking_system/issues/7) | Recover forgotten passwords. |
| [#8](https://github.com/Kerem-Haeger/dog_booking_system/issues/8) | Change password to maintain security. |

#### Clients

| ID | Story |
|----|-------|
| [#9](https://github.com/Kerem-Haeger/dog_booking_system/issues/9) | Manage pet profiles. |
| [#10](https://github.com/Kerem-Haeger/dog_booking_system/issues/10) | Book appointments. |
| [#11](https://github.com/Kerem-Haeger/dog_booking_system/issues/11) | View appointment history. |
| [#12](https://github.com/Kerem-Haeger/dog_booking_system/issues/12) | Modify or cancel bookings. |
| [#13](https://github.com/Kerem-Haeger/dog_booking_system/issues/13) | View services and pricing. |

#### Managers

| ID | Story |
|----|-------|
| [#14](https://github.com/Kerem-Haeger/dog_booking_system/issues/14) | Approve new users. |
| [#15](https://github.com/Kerem-Haeger/dog_booking_system/issues/15) | Approve/reject pet profiles. |
| [#16](https://github.com/Kerem-Haeger/dog_booking_system/issues/16) | Manage all appointments. |
| [#17](https://github.com/Kerem-Haeger/dog_booking_system/issues/17) | Edit service offerings. |
| [#18](https://github.com/Kerem-Haeger/dog_booking_system/issues/18) | Monitor calendar overview. |
| [#19](https://github.com/Kerem-Haeger/dog_booking_system/issues/19) | Control user roles and permissions. |

#### Employees

| ID | Story |
|----|-------|
| [#20](https://github.com/Kerem-Haeger/dog_booking_system/issues/20) | View assigned appointments. |
| [#21](https://github.com/Kerem-Haeger/dog_booking_system/issues/21) | Update appointment statuses. |
| [#22](https://github.com/Kerem-Haeger/dog_booking_system/issues/22) | Access pet information. |
| [#23](https://github.com/Kerem-Haeger/dog_booking_system/issues/23) | View client contact details. |

---

## Technologies Used

### Languages

- Python 3.12
- JavaScript
- HTML5
- CSS3

### Frameworks and Libraries

- Django 4.2 (backend framework)
- jQuery (DOM manipulation and AJAX)
- FullCalendar 6.1 (calendar views)
- AJAX (real-time UI updates)

### Databases

- SQLite (development)
- PostgreSQL (production, hosted via Neon)

### Developer Tools

- Git & GitHub
- Gunicorn (production server)
- Psycopg2 (PostgreSQL adapter)
- Pip3 (Python dependency manager)
- VSCode (IDE)
- Chrome DevTools (browser debugging)
- Validators: W3C, JSHint, PEP8
- Font Awesome (icons)

---

## Project Structure

See file tree and notes in the section above.

---

## Features

See [FEATURES.md](FEATURES.md) for a comprehensive breakdown of implemented and planned features.

---

## Design

The application adheres to modern UI/UX design principles with an emphasis on:

- Simplicity and clarity
- Accessibility and responsiveness
- Role-specific user flows

### Visual Design

- **Color Palette**: Blues and grays to promote professionalism and calm
- **Typography**: System font stack for speed and consistency
- **Buttons**: Semantic coloring for UX clarity
- **Imagery**: Minimal, icon-driven design via Font Awesome

### Wireframes

- [Desktop](documentation/wireframes/desktop_wireframes.pdf)  
- [Tablet](documentation/wireframes/tablet_wireframes.pdf)  
- [Mobile](documentation/wireframes/mobile_wireframes.pdf)

---

## Information Architecture

### Database Design

- Development: SQLite  
- Production: PostgreSQL on Neon

### Data Models

See the detailed model definitions and ER diagrams in this README above.

---

## Testing

See [TESTING.md](TESTING.md) for a full overview of manual and automated tests, including:

- Model tests
- Form and view tests
- End-to-end use case testing

---

## Deployment

- Hosted on: **[Deployment Platform Name]**  
- Database: **Neon** PostgreSQL (production)  
- Live URL: [Dog Booking System](https://your-deployment-url.com)

Full instructions: see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Future Improvements

The current version of the Dog Booking System serves as a robust foundation, but several planned enhancements could significantly improve functionality, usability, and business value:

- **Grooming Logs for Staff**: Implement a private logging system where employees and managers can leave internal comments or notes after each grooming session. These logs would be accessible only to staff and linked to pet profiles for future reference.
- **Image Uploads**: Allow users to upload profile pictures for pets and include image attachments in staff logs (e.g., for before/after grooming shots or special instructions).
- **Email Notifications**: Integrate automated email functionality for booking confirmations, appointment reminders, cancellations, and other system alerts.
- **Expanded Employee Dashboard**: Enable employees to:
  - Request time off (with approval workflows)
  - View their full grooming schedule
  - Access pet profiles for upcoming appointments
- **Voucher System**: Introduce a system for special offers (e.g., birthday vouchers) with optional discount codes that can be tracked and managed by managers.

These features are intentionally modular and designed for future scalability.

---

## Learning Outcomes

This project was part of my Diploma in Full Stack Software Development and has helped me solidify a wide range of development and project management skills.

### Key Takeaways

- **Full-Stack Application Development**: I successfully built a scalable web application using Django, PostgreSQL, JavaScript, and AJAX, with a strong emphasis on user roles and database relationships.
- **Modular and Role-Based Design**: I learned to structure logic and views in a maintainable way by separating functionality across user types (client, employee, manager).
- **Frontend/Backend Integration**: I gained practical experience in integrating real-time frontend functionality with backend validation and security using AJAX and Django forms.
- **Deployment**: I learned how to prepare, deploy, and maintain a Django project in a cloud-hosted environment.
- **Security and Access Control**: Implementing custom role-based permissions, input validation, and restricted views helped me understand key principles of secure development.

### Agile Reflections

Although I implemented an issue tracker to follow Agile principles, I acknowledge that my issue logs are out of sync with my current development progress. This has helped me realize the importance of consistent documentation and progress tracking. I now have a better understanding of Agile workflows and plan to apply this more rigorously in future projects.

---

## Credits

- **Django** for the framework powering the backend  
- **Bootstrap**, **jQuery**, and **Font Awesome** for frontend functionality  
- **Neon** for cloud-based PostgreSQL  
- **GitHub** for version control and collaboration tools

---

## Acknowledgments

- Code Institute and mentor support  
- My partner Saskia, whose business this idea is based on
- Django and open-source communities for their documentation and libraries

---







## About

[Dog Booking System](https://your-deployment-url.com) is a comprehensive pet grooming and services management application. The main goal of this app is to help pet service businesses manage clients, pets, appointments, services, and staff efficiently. Moreover, the app is aimed at streamlining the booking process and improving customer service quality.

## User Experience Design

### Strategy

Developed for pet service businesses, the app is designed to be user-friendly and intuitive. The main goal of the app is to help businesses manage their pet clients, appointments, services, and staff members effectively. This has been achieved through a clean and straightforward interface with role-based access control. As a final goal, the app is aimed at increasing operational efficiency and customer satisfaction.

### Target Audience

The app was developed for all stakeholders in pet service businesses:
* Managers: to oversee business operations, manage staff, approve new users and pets, monitor appointments, and control service offerings
* Employees: to manage their assigned appointments, view client and pet information, and update appointment statuses
* Clients: to book services for their pets, manage pet profiles, view appointment history, and track upcoming appointments

### User Stories

#### **First Time Visitor Goals**

| Issue ID    | User Story |
|-------------|-------------|
| [#1](https://github.com/Kerem-Haeger/dog_booking_system/issues/1) | As a First Time Visitor, I want to be able to easily understand the main purpose of the app, so that I can learn more about the pet services offered. |
| [#2](https://github.com/Kerem-Haeger/dog_booking_system/issues/2) | As a First Time Visitor, I want to be able to easily navigate through the app, so that I can find relevant information. |
| [#3](https://github.com/Kerem-Haeger/dog_booking_system/issues/3) | As a First Time Visitor, I want to be able to register my account, so that I can access the booking system. |
| [#4](https://github.com/Kerem-Haeger/dog_booking_system/issues/4) | As a First Time Visitor, I want to be able to find the app useful, so that I can book services for my pet. |

#### **Frequent User Goals**

| Issue ID    | User Story |
|-------------|-------------|
| [#5](https://github.com/Kerem-Haeger/dog_booking_system/issues/5) | As a Frequent User, I want to be able to log in to my account, so that I can access my personal dashboard. |
| [#6](https://github.com/Kerem-Haeger/dog_booking_system/issues/6) | As a Frequent User, I want to be able to easily log in and log out, so that I can securely access my account information. |
| [#7](https://github.com/Kerem-Haeger/dog_booking_system/issues/7) | As a Frequent User, I want to be able to easily recover my password in case I forget it, so that I can regain access to my account. |
| [#8](https://github.com/Kerem-Haeger/dog_booking_system/issues/8) | As a Frequent User, I want to be able to change my password, so that I can ensure account security. |

#### **Client Goals**

| Issue ID    | User Story |
|-------------|-------------|
| [#9](https://github.com/Kerem-Haeger/dog_booking_system/issues/9) | As a Client, I want to be able to add and manage my pet profiles, so that I can book appropriate services. |
| [#10](https://github.com/Kerem-Haeger/dog_booking_system/issues/10) | As a Client, I want to be able to book appointments for my pets, so that I can schedule grooming services. |
| [#11](https://github.com/Kerem-Haeger/dog_booking_system/issues/11) | As a Client, I want to be able to view my appointment history, so that I can track my pet's service records. |
| [#12](https://github.com/Kerem-Haeger/dog_booking_system/issues/12) | As a Client, I want to be able to cancel or edit appointments, so that I can manage my schedule. |
| [#13](https://github.com/Kerem-Haeger/dog_booking_system/issues/13) | As a Client, I want to be able to view available services and pricing, so that I can make informed decisions. |

#### **Manager Goals**

| Issue ID    | User Story |
|-------------|-------------|
| [#14](https://github.com/Kerem-Haeger/dog_booking_system/issues/14) | As a Manager, I want to be able to approve new user registrations, so that I can control access to the system. |
| [#15](https://github.com/Kerem-Haeger/dog_booking_system/issues/15) | As a Manager, I want to be able to approve new pet registrations, so that I can verify pet information. |
| [#16](https://github.com/Kerem-Haeger/dog_booking_system/issues/16) | As a Manager, I want to be able to manage all appointments, so that I can oversee business operations. |
| [#17](https://github.com/Kerem-Haeger/dog_booking_system/issues/17) | As a Manager, I want to be able to manage services and pricing, so that I can control business offerings. |
| [#18](https://github.com/Kerem-Haeger/dog_booking_system/issues/18) | As a Manager, I want to be able to view calendar overview, so that I can monitor daily operations. |
| [#19](https://github.com/Kerem-Haeger/dog_booking_system/issues/19) | As a Manager, I want to be able to manage user roles and permissions, so that I can control system access. |

#### **Employee Goals**

| Issue ID    | User Story |
|-------------|-------------|
| [#20](https://github.com/Kerem-Haeger/dog_booking_system/issues/20) | As an Employee, I want to be able to view my assigned appointments, so that I can prepare for my workday. |
| [#21](https://github.com/Kerem-Haeger/dog_booking_system/issues/21) | As an Employee, I want to be able to update appointment statuses, so that I can track service completion. |
| [#22](https://github.com/Kerem-Haeger/dog_booking_system/issues/22) | As an Employee, I want to be able to view pet information, so that I can provide appropriate care. |
| [#23](https://github.com/Kerem-Haeger/dog_booking_system/issues/23) | As an Employee, I want to be able to view client contact information, so that I can communicate when necessary. |

---

## Technologies used

- ### Languages:
    
    + [Python 3.12](https://www.python.org/downloads/release/python-3120/): the primary language used to develop the server-side of the website.
    + [JavaScript](https://www.javascript.com/): the primary language used to develop interactive components of the website.
    + [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML): the markup language used to create the website.
    + [CSS](https://developer.mozilla.org/en-US/docs/Web/css): the styling language used to style the website.

- ### Frameworks and libraries:

    + [Django 4.2](https://www.djangoproject.com/): python framework used to create all the logic.
    + [jQuery](https://jquery.com/): was used to control click events and sending AJAX requests.
    + [FullCalendar 6.1](https://fullcalendar.io/): JavaScript calendar library used for appointment scheduling and calendar views.
    + [AJAX](https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX): used for asynchronous data exchange, particularly for appointment management and real-time updates.

- ### Databases:

    + [SQLite](https://www.sqlite.org/): was used as a development database.
    + [PostgreSQL](https://www.postgresql.org/): the database used to store all the data via Neon cloud service (provided by Code Institute).

- ### Other tools:

    + [Git](https://git-scm.com/): the version control system used to manage the code.
    + [Pip3](https://pypi.org/project/pip/): the package manager used to install the dependencies.
    + [Gunicorn](https://gunicorn.org/): the webserver used to run the website.
    + [Psycopg2](https://www.psycopg.org/docs/): the database adapter used to connect to PostgreSQL.
    + [Neon](https://neon.tech/): the cloud database service used to host PostgreSQL (provided by Code Institute).
    + [GitHub](https://github.com/): used to host the website's source code.
    + [VSCode](https://code.visualstudio.com/): the IDE used to develop the website.
    + [Chrome DevTools](https://developer.chrome.com/docs/devtools/open/): was used to debug the website.
    + [Font Awesome](https://fontawesome.com/): was used to create the icons used in the website.
    + [W3C Validator](https://validator.w3.org/): was used to validate HTML5 code for the website.
    + [W3C CSS validator](https://jigsaw.w3.org/css-validator/): was used to validate CSS code for the website.
    + [JSHint](https://jshint.com/): was used to validate JS code for the website.
    + [PEP8](https://pep8.org/): was used to validate Python code for the website.

---

## Project Structure

```
dog_booking_system/
├── booking_system/                 # Main Django project directory
│   ├── __init__.py
│   ├── asgi.py                    # ASGI configuration
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Main URL configuration
│   ├── wsgi.py                    # WSGI configuration
│   └── templates/
│       └── registration/          # Authentication templates
│           ├── login.html
│           └── register.html
│
├── core/                          # Main application directory
│   ├── __init__.py
│   ├── admin.py                   # Django admin configuration
│   ├── apps.py                    # App configuration
│   ├── context_processors.py     # Custom context processors
│   ├── forms.py                   # Django forms
│   ├── models.py                  # Database models
│   ├── urls.py                    # App URL patterns
│   ├── utils.py                   # Utility functions
│   ├── views.py                   # Legacy views (kept for compatibility)
│   │
│   ├── views/                     # Organized view modules
│   │   ├── __init__.py
│   │   ├── api_views.py          # AJAX and API endpoints
│   │   ├── auth_views.py         # Authentication views
│   │   ├── client_views.py       # Client-specific views
│   │   ├── employee_views.py     # Employee-specific views
│   │   ├── manager_views.py      # Manager-specific views
│   │   └── roles.py              # Role-based mixins and utilities
│   │
│   ├── migrations/               # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── ...
│   │
│   ├── static/core/              # Static files
│   │   ├── css/
│   │   │   ├── base.css          # Base styling
│   │   │   ├── dashboard.css     # Dashboard styling
│   │   │   ├── forms.css         # Form styling
│   │   │   ├── user-management.css
│   │   │   ├── pet_management.css
│   │   │   └── ...
│   │   └── js/                   # JavaScript files
│   │
│   ├── templates/core/           # Application templates
│   │   ├── base.html            # Base template
│   │   ├── dashboard/           # Dashboard templates
│   │   ├── appointments/        # Appointment templates
│   │   ├── pets/               # Pet management templates
│   │   ├── users/              # User management templates
│   │   └── ...
│   │
│   └── templatetags/            # Custom template tags
│       ├── __init__.py
│       └── form_tags.py
│
├── staticfiles/                  # Collected static files (production)
├── templates/                    # Global templates
│   ├── 400.html                 # Error pages
│   ├── 403.html
│   ├── 404.html
│   └── 500.html
│
├── .venv/                       # Virtual environment
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── env.py                       # Environment variables
├── Procfile                     # Deployment configuration
├── db.sqlite3                   # Local development database
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

### Key Files and Directories:

- **booking_system/**: Contains the main Django project configuration
- **core/**: The primary application handling all business logic
- **core/views/**: Organized view modules separated by user roles and functionality
- **core/models.py**: Database models for User, Pet, Appointment, and Service management
- **core/static/**: CSS and JavaScript files for frontend functionality
- **core/templates/**: HTML templates organized by feature
- **env.py**: Environment variables including database configuration
- **requirements.txt**: All Python package dependencies

---

## FEATURES

Please refer to the [FEATURES.md](FEATURES.md) file for all features-related documentation.

---

## Design

The design of the application follows modern web design principles with a focus on usability and accessibility.
The central theme of the application is professional service delivery with intuitive navigation. A clean, minimalistic approach was used to create a functional interface without overwhelming users. As this application serves multiple user types with different needs, careful attention was paid to information hierarchy and user flow.

### Color Scheme

The color scheme of the application is based on professional and calming colors:

![Color Scheme](documentation/design/color_palette.png)

The design uses a sophisticated blue and gray palette that conveys trust and professionalism. The navigation uses dark gray (#343a40) with light text for clear contrast. The main content area features a clean white background with subtle gray borders and blue accent colors (#007bff) for interactive elements.

Button colors follow a semantic approach:
- Primary actions: Blue (#007bff)
- Success actions: Green (#28a745)
- Warning actions: Orange (#ffc107)
- Danger actions: Red (#dc3545)
- Secondary actions: Gray (#6c757d)

### Typography

The main font used in the application is the system font stack including -apple-system, BlinkMacSystemFont, 'Segoe UI', and Roboto. This choice ensures optimal readability across different operating systems while maintaining consistent performance.

Font weights are used strategically:
- Bold (700): For headings and important labels
- Normal (400): For body text and general content
- Light weights are avoided to maintain readability

### Imagery

- Icons are primarily sourced from [Font Awesome](https://fontawesome.com/) to maintain consistency
- Pet and service-related imagery placeholders are included for future customization
- The application focuses on functional design with minimal decorative elements

### Wireframes

- [Desktop Wireframes](documentation/wireframes/desktop_wireframes.pdf)
- [Tablet Wireframes](documentation/wireframes/tablet_wireframes.pdf)
- [Mobile Wireframes](documentation/wireframes/mobile_wireframes.pdf)

---

## Information Architecture

### Database

* During development, the database uses SQLite for local testing.
* The production database uses PostgreSQL hosted on Neon cloud service.

### Entity-Relationship Diagram

* The ERD was created using database design tools.

- [Database Schema](documentation/diagrams/database_schema.pdf)

### Data Modeling

1. **User (Django's built-in User model)**

Extended through UserProfile for additional functionality.

| Name          | Database Key  | Field Type    | Validation |
| ------------- | ------------- | ------------- | ---------- |
| Username      | username      | CharField     | max_length=150, unique=True |
| Email         | email         | EmailField    | max_length=254, optional |
| First Name    | first_name    | CharField     | max_length=150 |
| Last Name     | last_name     | CharField     | max_length=150 |
| Password      | password      | CharField     | Django's built-in validation |

2. **UserProfile**

Extends the User model with role-based functionality.

| Name          | Database Key  | Field Type    | Validation |
| ------------- | ------------- | ------------- | ---------- |
| User          | user          | OneToOneField | User, on_delete=models.CASCADE |
| Role          | role          | CharField     | max_length=20, choices=ROLE_CHOICES |

```Python
ROLE_CHOICES = [
    ('pending', 'Pending Approval'),
    ('client', 'Client'),
    ('employee', 'Employee'),
    ('manager', 'Manager'),
]
```

3. **PetProfile**

Stores information about pets registered in the system.

| Name          | Database Key  | Field Type    | Validation |
| ------------- | ------------- | ------------- | ---------- |
| User          | user          | ForeignKey    | User, on_delete=models.CASCADE |
| Name          | name          | CharField     | max_length=100 |
| Breed         | breed         | CharField     | max_length=100 |
| Size          | size          | CharField     | max_length=20, choices=SIZE_CHOICES |
| Age           | age           | PositiveIntegerField |  |
| Special Notes | special_notes | TextField     | blank=True |
| Status        | status        | CharField     | max_length=20, choices=STATUS_CHOICES |

```Python
SIZE_CHOICES = [
    ('small', 'Small (0-25 lbs)'),
    ('medium', 'Medium (26-60 lbs)'),
    ('large', 'Large (61-100 lbs)'),
    ('extra_large', 'Extra Large (100+ lbs)'),
]

STATUS_CHOICES = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]
```

4. **Service**

Defines available services and pricing.

| Name          | Database Key  | Field Type    | Validation |
| ------------- | ------------- | ------------- | ---------- |
| Name          | name          | CharField     | max_length=100 |
| Description   | description   | TextField     |  |
| Duration      | duration_minutes | PositiveIntegerField |  |
| Is Active     | is_active     | BooleanField  | default=True |
| Slot Interval | slot_interval | PositiveIntegerField | default=30 |

5. **ServicePrice**

Handles pricing based on pet size and service type.

| Name          | Database Key  | Field Type    | Validation |
| ------------- | ------------- | ------------- | ---------- |
| Service       | service       | ForeignKey    | Service, on_delete=models.CASCADE |
| Size          | size          | CharField     | max_length=20, choices=SIZE_CHOICES |
| Price         | price         | DecimalField  | max_digits=10, decimal_places=2 |

6. **Appointment**

Manages booking appointments for pet services.

| Name          | Database Key  | Field Type    | Validation |
| ------------- | ------------- | ------------- | ---------- |
| User          | user          | ForeignKey    | User, on_delete=models.CASCADE |
| Pet           | pet           | ForeignKey    | PetProfile, on_delete=models.CASCADE |
| Service       | service       | ForeignKey    | Service, on_delete=models.CASCADE |
| Date          | date          | DateField     |  |
| Time          | time          | TimeField     |  |
| Status        | status        | CharField     | max_length=20, choices=STATUS_CHOICES |
| Final Price   | final_price   | DecimalField  | max_digits=10, decimal_places=2 |
| Special Requests | special_requests | TextField | blank=True |
| Edit Count    | edit_count    | PositiveIntegerField | default=0 |

```Python
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('rejected', 'Rejected'),
]
```

---

## Testing

Please refer to the [TESTING.md](TESTING.md) file for all test-related documentation.

---

## Deployment

- The app will be deployed to [Your Deployment Platform].
- The database is hosted on [Neon](https://neon.tech/).

- The app can be reached by the [link](https://your-deployment-url.com).

Please refer to the [DEPLOYMENT.md](DEPLOYMENT.md) file for all deployment-related documentation.

---

## Credits

- [GitHub](https://github.com/) for hosting the project repository.
- [Django](https://www.djangoproject.com/) for the comprehensive web framework.
- [Neon](https://neon.tech/) for the cloud PostgreSQL database hosting.
- [Font Awesome](https://fontawesome.com/) for the comprehensive icon library.
- [Bootstrap](https://getbootstrap.com/) for responsive design components.
- [jQuery](https://jquery.com/) for enhanced JavaScript functionality.
- [PostgreSQL](https://www.postgresql.org/) for the robust database system.

---

## Acknowledgments

- The development team for creating a comprehensive pet service management solution.
- Pet service industry professionals who provided insights into business requirements.
- The Django community for excellent documentation and support resources.
