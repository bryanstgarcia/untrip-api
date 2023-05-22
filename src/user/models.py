from models_config import db, DataError, ServerError
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash
import datetime, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=True)
    hash_password = db.Column(db.String(256), unique=False, nullable=False)
    salt = db.Column(db.String(256), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.datetime.now)
    project = db.relationship("Project", back_populates="user")


    @classmethod
    def create(cls, **kwargs):
        try:
            email_valid = cls.email_is_valid(kwargs["email"])

            if not email_valid:
                raise DataError({
                    "error": "Wrong email"
                })

            if type(email_valid) == dict:
                raise ServerError({
                    "error": "Server error"
                })
            salt = cls.generate_salt()
            salted_password = salt + kwargs["password"]
            hashed_password = generate_password_hash(salted_password)
            new_user = cls(
                email=kwargs["email"],
                name=kwargs["name"],
                hash_password= hashed_password,
                salt = salt
            )
            if not isinstance(new_user, cls):
                raise ServerError({
                    "error", "An error occurred creating the user"
                })
            return new_user
        except DataError as error:
            print("Ingresando a un DataError: ", error)
            return {
                "error" : error.args[0]["error"],
                "status": 400
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
    def email_is_valid(cls, email):
        """Checks if user exist in DB by email. If not, return True"""
        try:
            user_exist = cls.query.filter_by(email=email).one_or_none()
            if user_exist:
                return False
            return True 
        except ServerError as error:
            print(error)
            return {
                "error": "Server error"
            }
        except Exception as error:
            print(error)
            return error.args

    @classmethod
    def deactive_user(cls, userId):
        pass

    @staticmethod
    def generate_salt():
        """ Generates salt, turn to string an return it"""
        salt = bcrypt.gensalt()
        print(type(salt))
        return salt.decode()

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
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "time_created": self.time_created,
            "time_upated": self.time_updated
        }