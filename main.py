from models.model_factory import ModelFactory, ModelFamily

if __name__ == "__main__":
  
  agent = ModelFactory.createModel(ModelFamily.GEMINI, "gemini-3.8-flash")
  
  response = agent.query("Hello, please introduce yourself")
  print(response["text"])
  print(f"Tokens used: {response.total_token_count}")