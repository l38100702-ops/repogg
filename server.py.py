import socket
import threading

HOST = '0.0.0.0'
PORT = 8080

clients = []
# Блокування для безпечного доступу до списку клієнтів з різних потоків
clients_lock = threading.Lock()


def broadcast(data, exclude_socket=None):
    with clients_lock:
        # Створюємо список для видалення тих, хто відключився
        to_remove = []
        for client in clients:
            if client != exclude_socket:
                try:
                    client.sendall(data)
                except:
                    to_remove.append(client)

        # Видаляємо неактивні сокети
        for client in to_remove:
            if client in clients:
                clients.remove(client)


def handle_client(client_socket, addr):
    print(f"[НОВЕ ПІДКЛЮЧЕННЯ] {addr}")
    while True:
        try:
            # Отримуємо дані
            data = client_socket.recv(1024 * 1024)  # Збільшений буфер для фото
            if not data:
                break

            # Пересилаємо всім іншим
            broadcast(data, exclude_socket=client_socket)
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"[ПОМИЛКА] {addr}: {e}")
            break

    print(f"[ВІДКЛЮЧЕННЯ] {addr}")
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
    client_socket.close()


def main():
    # Виправлено звернення до socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
    except Exception as e:
        print(f"[ПОМИЛКА ЗАПУСКУ] Не вдалося прив'язати порт {PORT}: {e}")
        return

    server_socket.listen(10)
    print(f"[ЗАПУСК] Сервер слухає на {HOST}:{PORT}")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            with clients_lock:
                clients.append(client_socket)

            # Передаємо addr у потік для логів
            t = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            t.start()
        except KeyboardInterrupt:
            print("\n[ЗУПИНКА] Сервер вимикається...")
            break

    server_socket.close()


if __name__ == "__main__":
    main()