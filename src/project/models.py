from models_config import db, DataError, ServerError, AuthorizationError
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash
import datetime, bcrypt

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(280), unique=False, nullable=True)
    image_url = db.Column(db.String(580), unique=False, nullable=True)
    is_favorite = db.Column(db.Boolean(), unique=False, nullable=False, default=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="project")

    @classmethod
    def create(cls, **kwargs):
        try:
            if not kwargs.get("user_id"):
                raise AuthorizationError({
                    "error": "Action not allowed"
                })

            new_project = cls(
                title=kwargs["title"],
                user_id=kwargs["user_id"],
                image_url=kwargs.get("image_url")
            )
            if not isinstance(new_project, cls):
                raise ServerError({
                    "error", "An error occurred creating the project, contact "
                })
            return new_project
        except DataError as error:
            print("Ingresando a un DataError: ", error)
            return {
                "error" : error.args[0]["error"],
                "status": 400
            }
        except AuthorizationError as error:
            print("Ingresando a un AuthorizationError: ", error)
            return {
                "error" : error.args[0]["error"],
                "status": 403
            }
        except ServerError as error:
            return {
                "error" : error.args[0]["error"],
                "status": 500
            }
        except Exception as error:
            print(error)
            return error.args[0]

    @classmethod
    def deactive_project(cls):
        pass

    def save_and_commit(self):
        """ Adds user to session and commit """
        try:
            db.session.add(self)
            db.session.commit()
            return {
                "success": True,
                "message": "User saved"
            }
        except ServerError as error:
            print(error)
            return {
                "success": False,
                "message": "An error occurs saving the user into de session"
            }
        except Exception as error:
            print(error)
            return {
                "success": False,
                "message": "An extrangge error occurs, sorry"
            }
    
    def __repr__(self):
        return f'<Project {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "is_favorite": self.is_favorite,
            "is_active": self.is_active,
            "user_id": self.user_id,
            "time_created": self.time_created,
            "time_upated": self.time_updated
        }