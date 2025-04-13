from typing import Any, Dict, Optional, Union


class ResponseHandler:
    
    @staticmethod
    def success(data: Any = [], message: str = "Operação concluída com sucesso") -> Dict[str, Any]:
        return {
            "success": True,
            "data": data,
            "message": message
        }
    
    @staticmethod
    def error(message: str = "Ocorreu um erro durante a operação", data: Any = [], error_code: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        response = {
            "success": False,
            "data": data,
            "message": message
        }
        
        if error_code is not None:
            response["error_code"] = error_code
            
        return response
