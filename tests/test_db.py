from api.db.database import init_db
from api.v1.models.user import User
from datetime import datetime
import sys

def test_create_user():
    try:
        # Initialize database connection
        init_db()

        # Create a test user
        test_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            avatar_url="https://example.com/avatar.jpg",
            is_active=True,
            is_verified=True
        )
        
        # Save the user to database
        test_user.save()
        
        print(f"Successfully created user with id: {test_user.id}")
        
        # Verify we can retrieve the user
        retrieved_user = User.objects(email="test@example.com").first()
        print(f"Retrieved user: {retrieved_user.first_name} {retrieved_user.last_name}")
        
        # Clean up - delete the test user
        test_user.delete()
        print("Test user deleted successfully")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_create_user()