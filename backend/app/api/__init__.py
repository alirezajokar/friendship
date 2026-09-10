from fastapi import FastAPI

from app.api import auth, friends, health, invites, notifications, users, wishlists


def register_routes(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(friends.router)
    app.include_router(invites.router)
    app.include_router(wishlists.router)
    app.include_router(notifications.router)
