# ObejctId Field for pydantic models
from typing import Annotated
from pydantic import BeforeValidator
from bson import ObjectId
 
# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)] 