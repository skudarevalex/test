from database.database import init_db


def main():
    init_db()
    print("База данных успешно инициализирована.")

if __name__ == "__main__":
    main()