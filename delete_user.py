import os
import sys

# Add Admin_api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Admin_api"))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.auth import User

def delete_user_by_email(email: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email '{email}' not found.")
            return
        
        db.delete(user)
        db.commit()
        print(f"User '{email}' deleted successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

def delete_user_by_id(user_id: int):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User with ID '{user_id}' not found.")
            return
        
        db.delete(user)
        db.commit()
        print(f"User ID '{user_id}' deleted successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

def delete_all_users():
    db: Session = SessionLocal()
    try:
        count = db.query(User).count()
        db.query(User).delete()
        db.commit()
        print(f"All {count} users deleted successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

def list_users():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found.")
            return
        print("\nUsers in database:")
        print("-" * 50)
        for u in users:
            print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Role: {u.role}")
        print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Delete users from database")
    parser.add_argument("--email", help="Delete user by email")
    parser.add_argument("--id", type=int, help="Delete user by ID")
    parser.add_argument("--all", action="store_true", help="Delete ALL users")
    parser.add_argument("--list", action="store_true", help="List all users")
    
    args = parser.parse_args()
    
    if args.list:
        list_users()
    elif args.email:
        delete_user_by_email(args.email)
    elif args.id:
        delete_user_by_id(args.id)
    elif args.all:
        confirm = input("Are you sure you want to delete ALL users? (yes/no): ")
        if confirm.lower() == "yes":
            delete_all_users()
        else:
            print("Cancelled.")
    else:
        list_users()
