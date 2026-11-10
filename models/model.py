
import contextlib
import inspect
import io
import traceback
import types
from abc import ABC, abstractmethod
from typing import (
    Any, Callable, Dict, Literal, Optional, Union, get_args, get_origin, get_type_hints,
)


class Model(ABC):
    """Abstract base class for model implementations.
    
    Allows users to implement any model (LLM, classifier, etc.) by inheriting
    from this class and implementing the required methods.
    """
    
    def __init__(self, model_id: str, **kwargs):
        """Initialize the model.
        
        Args:
            model_id: The actual model being used (e.g., "gemini-pro", "gpt-4", "llama-2")
            **kwargs: Additional model-specific configuration parameters
        """
        self.model_id = model_id
        self.config = kwargs
        self.skills = {}
    
    @abstractmethod
    def query(self, input_text: str, **kwargs) -> str:
        """Query the model with input text.
        
        Args:
            input_text: The input prompt or query
            **kwargs: Model-specific query parameters (temperature, max_tokens, etc.)
        
        Returns:
            Model output as a string along with token usage
        
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and ready to use.
        
        Returns:
            True if model is ready, False otherwise
        
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_token_usage(reponse: any):
        """Extracts the token usage of a response

        Args:
            reponse (any): The response returned by the model
        
        Returns:
            The total number of tokens consumed to generate the response
        
        Raises:
            NontImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError
    
    def define_skill(
        self,
        skill_name: str,
        skill_callback: Callable[..., Any],
        skill_args: Dict[str, Any],
        skill_desc: str,
    ) -> None:
        """Register a skill the model has access to.
        
        Args:
            skill_name: The name of the skill
            skill_callback: Function used to execute the skill
            skill_args: Maps each argument name to its expected type, in the
                order the arguments must be provided (e.g. {"a": int, "b": str})
            skill_desc: A short summary of what the skill does
        
        Raises:
            ValueError: If the callback is not callable, a declared type is not
                supported, the declared arguments do not fit the callback's
                signature, or a declared type contradicts the callback's own
                type annotation
        """
        
        # validate that it is actually a function
        if not callable(skill_callback):
            raise ValueError(f"Callback for skill '{skill_name}' is not callable")
        
        # validates that each skill_args is a dict and that all the keys (arg_names) are strings
        if not isinstance(skill_args, dict) or not all(isinstance(name, str) for name in skill_args):
            raise ValueError(
                f"skill_args for skill '{skill_name}' must be a dict mapping "
                f"argument names (str) to types"
            )
        
        # validates that each skill_arg's type is a supported type
        # A supported type is a type that can be checked
        # This includes plain classes like int, plus Any, None, Optional,
        # Union, Literal and generics like list[int]
        for name, expected in skill_args.items():
            if not self._is_supported_type(expected):
                raise ValueError(
                    f"Argument '{name}' of skill '{skill_name}' has unsupported "
                    f"type {expected!r}; use a class, Any, None, Optional, Union, "
                    f"Literal, or a generic such as list[int]"
                )
        
        # validates that the function can be called with the number of arguments provided
        signature = inspect.signature(skill_callback)
        try:
            signature.bind(*skill_args)
        except TypeError as e:
            raise ValueError(
                f"Arguments {list(skill_args)} do not match the signature of "
                f"skill '{skill_name}': {e}"
            ) from e
        
        # Get the type hints for the callback if there are any
        try:
            hints = get_type_hints(skill_callback)
        except Exception:
            # there is an argument whose type cannot be resolved to a type
            hints = {}
            
        # gather the args that can be passed by position (the place in order of the arguments)
        positional = [
            p for p in signature.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL)
        ]
        for i, (name, declared) in enumerate(skill_args.items()):
            # for the ith arg, pick the ith parm
            # min(...) handles *args
            # The last parameter absorbs every extra declared arg
            param = positional[min(i, len(positional) - 1)]
            
            # check that the names of the arguements match
            if param.kind is not param.VAR_POSITIONAL and name != param.name:
                raise ValueError(
                    f"Argument #{i + 1} of skill '{skill_name}' is named '{name}' "
                    f"but the callback's parameter at that position is "
                    f"'{param.name}'; declare arguments in the callback's order"
                )
            annotation = hints.get(param.name, param.annotation)
            # if the arg didn't have a type annotation
            if annotation is param.empty:
                continue
            # if the arg's annotation states that it is NoneType
            if annotation is None:
                annotation = type(None)
            # if the arg's declared type (from the user) is NoneType
            if declared is None:
                declared = type(None)
            # NoneType deserves its own case because None == type(None) evals to false
            if annotation != declared:
                raise ValueError(
                    f"Argument '{name}' of skill '{skill_name}' is declared as "
                    f"{declared!r} but the callback annotates parameter "
                    f"'{param.name}' as {annotation!r}"
                )
        
        # save the skill
        self.skills[skill_name] = {
            "callback": skill_callback,
            "args": skill_args,
            "desc": skill_desc,
        }
    
    @staticmethod
    def _is_supported_type(expected: Any) -> bool:
        """Check that a declared type can be validated by _matches_type."""
        if expected is Any or expected is None:
            return True
        origin = get_origin(expected)
        if origin is Union or origin is types.UnionType:
            return all(Model._is_supported_type(t) for t in get_args(expected))
        if origin is Literal:
            return True
        if origin is not None:
            return isinstance(origin, type)
        return isinstance(expected, type)
    
    @staticmethod
    def _matches_type(value: Any, expected: Any) -> bool:
        """Check a value against a type; generics are checked by container type only."""
        if expected is Any:
            return True
        if expected is None:
            return value is None
        origin = get_origin(expected)
        if origin is Union or origin is types.UnionType:
            return any(Model._matches_type(value, t) for t in get_args(expected))
        if origin is Literal:
            return value in get_args(expected)
        if origin is not None:
            expected = origin
        if isinstance(expected, type):
            return isinstance(value, expected)
        return True
    
    def execute_skill(self, skill_name: str, skill_args: list[Any]) -> Dict[str, Any]:
        """Execute a registered skill by calling its callback.
        
        Args:
            skill_name: The name of a skill registered with define_skill
            skill_args: Arguments for the callback, in the order they were defined.
                They are passed as-is and must already have the declared types.
        
        Returns:
            A dictionary with:
                success: False if the callback raised an exception
                result: The callback's return value (None if it raised)
                output: Everything the callback wrote to stdout
                error: Everything the callback wrote to stderr, followed by the
                    traceback if it raised
        
        Raises:
            ValueError: If the skill does not exist, or the arguments do not match
                the skill's declared argument count or types
        """
        if skill_name not in self.skills:
            raise ValueError(
                f"Unknown skill '{skill_name}'. Available skills: {list(self.skills)}"
            )
        skill = self.skills[skill_name]
        callback = skill["callback"]
        arg_types = skill["args"]
        
        if len(skill_args) != len(arg_types):
            raise ValueError(
                f"Skill '{skill_name}' expects {len(arg_types)} argument(s) "
                f"{list(arg_types)} but got {len(skill_args)}"
            )
        for (name, expected), value in zip(arg_types.items(), skill_args):
            if not self._matches_type(value, expected):
                raise ValueError(
                    f"Argument '{name}' of skill '{skill_name}' expected "
                    f"{expected.__name__ if isinstance(expected, type) else expected}, got "
                    f"{type(value).__name__}"
                )
        
        stdout, stderr = io.StringIO(), io.StringIO()
        success, result = True, None
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                result = callback(*skill_args)
            except Exception:
                success = False
                traceback.print_exc()
        return {
            "success": success,
            "result": result,
            "output": stdout.getvalue(),
            "error": stderr.getvalue(),
        }
    
    def batch_query(self, inputs: list[str], **kwargs) -> list[str]:
        """Query the model with multiple inputs.
        
        Args:
            inputs: List of input prompts
            **kwargs: Model-specific query parameters
        
        Returns:
            List of model outputs
        """
        return [self.query(inp, **kwargs) for inp in inputs]
    
    def get_config(self) -> Dict[str, Any]:
        """Get the model configuration.
        
        Returns:
            Dictionary of model configuration parameters
        """
        return {"model_id": self.model_id, **self.config}
