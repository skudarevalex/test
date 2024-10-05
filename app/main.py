from database.database import init_db
from services.crud.mlservice import MLService
from models.mlmodelmanager import MLModelManager
from services.crud.userservice import UserService


# Инициализация базы данных
init_db()

if __name__ == "__main__":
    model_manager = MLModelManager()
    model_manager.load_models()
    
    user_service = UserService()
    ml_service = MLService(model_manager)
    
    # Регистрация пользователя
    user_service.register("example_user", "password123")
    
    # Вход в систему
    login_result = user_service.login("example_user", "password123")
    if login_result["status"] == "success":
        user_id = login_result["user_id"]
        
        # Добавление баланса
        user_service.add_balance(user_id, 100)
        
        # Обработка задачи ML с валидными и невалидными данными
        user = user_service.get_user_by_credentials("example_user", "password123")
        if user:
            task_result = ml_service.process_task(user, 1, "1,2,3,invalid,4.5,abc,5")
            print("Task result:", task_result)
        
        # Получение баланса пользователя
        user_balance = user_service.get_user_balance(user_id)
        print(user_balance)
