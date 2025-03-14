# Creaverse

Creaverse is an exclusive, invite-only creator guild designed to foster collaboration, innovation, and engagement among digital creators. This platform enables users to share posts, interact with a curated community, and access AI-powered content recommendations.

## Features
- **Invite-Only Access**: Users can only join via an invitation link.
- **User Authentication**: Secure login and registration system.
- **Dashboard**: Personalized homepage with updates and insights.
- **Post Feed**: Share content, engage with other creators, and explore trending posts.
- **Private Messaging**: One-on-one communication between members.
- **AI-Powered Recommendations**: Intelligent content suggestions based on user engagement.

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (Bootstrap for UI styling)
- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Authentication**: Django's built-in authentication system
- **Hosting & Deployment**: Heroku

## Installation & Setup
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/your-username/creaverse.git
   cd creaverse
   ```
2. **Create a Virtual Environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply Migrations**:
   ```sh
   python manage.py migrate
   ```
5. **Run the Development Server**:
   ```sh
   python manage.py runserver
   ```

## Deployment to Heroku
1. **Install Heroku CLI** (if not already installed):
   ```sh
   curl https://cli-assets.heroku.com/install.sh | sh
   ```
2. **Login to Heroku**:
   ```sh
   heroku login
   ```
3. **Create a Heroku App**:
   ```sh
   heroku create creaverse
   ```
4. **Add Heroku Postgres** (Database):
   ```sh
   heroku addons:create heroku-postgresql:hobby-dev
   ```
5. **Set Up Environment Variables**:
   ```sh
   heroku config:set DJANGO_SECRET_KEY='your-secret-key'
   heroku config:set DEBUG=False
   ```
6. **Deploy the App**:
   ```sh
   git push heroku main
   heroku run python manage.py migrate
   heroku open
   ```

## Contribution Guidelines
1. Fork the repository
2. Create a new feature branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push to the branch (`git push origin feature-branch`)
5. Submit a pull request

## License
