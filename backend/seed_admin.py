import argparse
import asyncio
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import AsyncSessionLocal, init_db
from models import User
from auth import hash_password

async def seed_admin(username, email, password):
    await init_db()
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("Error: Invalid email format.")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where((User.username == username) | (User.email == email)))
        existing_user = result.scalars().first()
        
        if existing_user:
            print("Error: User with this username or email already exists.")
            return

        hashed_pw = hash_password(password)
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_pw,
            role="admin"
        )
        session.add(admin_user)
        await session.commit()
        print(f"Success: Admin user '{username}' created.")

def main():
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument("--username", required=True, help="Username for the admin")
    parser.add_argument("--email", required=True, help="Email for the admin")
    parser.add_argument("--password", required=True, help="Password for the admin")
    args = parser.parse_args()

    asyncio.run(seed_admin(args.username, args.email, args.password))

if __name__ == "__main__":
    main()
