import os
import json
import psycopg2

DB_CONFIG = {
    'dbname': "todo_db",
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

JSON_PATH = "mainDataBase.json"

def get_conn():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

def create_default_data():
    return {
        "login": "login",
        "name": "name",
        "city": "city",
        "question": "question",
        "priority": "nothing",
        "done": False
    }

def insert_task(task):
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (login, name, city, question, priority, done)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (task["login"], task["name"], task["city"], task["question"], task["priority"], task["done"]))
    conn.commit()
    cur.close()
    conn.close()
    print("Задача добавлена в БД.")

def delete_task(task_id):
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    print("Задача удалена из БД.")

def update_task(task_id, update_fields):
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    set_clause = ", ".join([f"{key} = %s" for key in update_fields.keys()])
    values = list(update_fields.values())
    values.append(task_id)
    query = f"UPDATE tasks SET {set_clause} WHERE id = %s"
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()
    print("Задача обновлена.")

def list_all_tasks():
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT id, login, name, city, question, priority, done FROM tasks ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        status = "✔" if row[6] else "✖"
        print(f"{row[0]} {status} {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")

def list_hot_tasks():
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT id, login, name, city, question FROM tasks WHERE priority = 'high'")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for i, row in enumerate(rows, 1):
        print(f"{i}. {row}")

def export_tasks_to_json():
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT login, name, city, question, priority, done FROM tasks")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tasks = [dict(zip(["login", "name", "city", "question", "priority", "done"], row)) for row in rows]
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)
    print("Резервная копия сохранена в JSON.")

def cli_menu():
    while True:
        print("\nЧто вы хотите сделать?\n")
        print("1. Создать дефолтную задачу")
        print("2. Добавить новую задачу")
        print("3. Удалить задачу")
        print("4. Показать задачи с высоким приоритетом")
        print("5. Показать все задачи")
        print("6. Редактировать задачу")
        print("7. Сделать резервную копию в JSON")
        print("8. Выйти")

        try:
            choice = int(input("Введите номер действия: "))
            if choice == 8:
                print("Выход")
                break
            logic_menu(choice)
        except ValueError:
            print("Ошибка: введите число от 1 до 8.")

def logic_menu(choice):
    if choice == 1:
        task = create_default_data()
        insert_task(task)

    elif choice == 2:
        task = {
            "login": input("Логин: "),
            "name": input("Имя: "),
            "city": input("Город: "),
            "question": input("Вопрос: "),
            "priority": input("Приоритет (low/medium/high): "),
            "done": False
        }
        insert_task(task)

    elif choice == 3:
        try:
            task_id = int(input("Введите ID задачи для удаления: "))
            delete_task(task_id)
        except ValueError:
            print("Ошибка: введите корректный ID.")

    elif choice == 4:
        list_hot_tasks()

    elif choice == 5:
        list_all_tasks()

    elif choice == 6:
        try:
            task_id = int(input("Введите ID задачи для редактирования: "))
            print("Оставьте поле пустым, если не хотите его менять.")
            updated_fields = {}
            login = input("Новый логин: ")
            if login: updated_fields["login"] = login
            name = input("Новое имя: ")
            if name: updated_fields["name"] = name
            city = input("Новый город: ")
            if city: updated_fields["city"] = city
            question = input("Новый вопрос: ")
            if question: updated_fields["question"] = question
            priority = input("Новый приоритет (low/medium/high): ")
            if priority: updated_fields["priority"] = priority
            done = input("Статус выполнения (true/false): ").lower()
            if done in ["true", "false"]:
                updated_fields["done"] = done == "true"

            if updated_fields:
                update_task(task_id, updated_fields)
            else:
                print("Ничего не изменено.")
        except ValueError:
            print("Ошибка: введите корректный ID.")

    elif choice == 7:
        export_tasks_to_json()

    else:
        print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    print("******** Добро пожаловать ********")
    cli_menu()