from models.gemini import Gemini
from enum import Enum


class InvalidModelFamilyError(Exception):
  """Raised when an unsupported model family is requested."""
  def __init__(self, model_family):
    self.model_family = model_family
    message = f"Invalid model family: {model_family}. Supported families: {', '.join([f.name for f in ModelFamily])}"
    super().__init__(message)


# Enums for model Family
class ModelFamily(Enum):
  GEMINI = 1


class ModelFactory:
  
  def createModel(model_family: ModelFamily, model_id: str, **kwargs: any):
    match model_family:
      case ModelFamily.GEMINI:
        return Gemini(model_id, **kwargs)
      case _:
        raise InvalidModelFamilyError(model_family)
