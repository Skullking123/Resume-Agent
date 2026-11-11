from constants.ModelFamily import ModelFamilyEnum

class InvalidModelFamilyError(Exception):
  """Raised when an unsupported model family is requested."""
  def __init__(self, model_family):
    self.model_family = model_family
    message = f"Invalid model family: {model_family}. Supported families: {', '.join([f.name for f in ModelFamily])}"
    super().__init__(message)


class ModelFactory:
  
  def createModel(model_family: ModelFamilyEnum, model_id: str, **kwargs: any):
    match model_family:
      case ModelFamilyEnum.GEMINI:
        from models.gemini import Gemini
        return Gemini(model_id, **kwargs)
      case _:
        raise InvalidModelFamilyError(model_family)
