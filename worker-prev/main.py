import pika, sys, os, json
import logging
import threading
import functools
import pika.channel

import importlib

import redis

from common.redis_publisher import update_status

VIDEO_FORMATS_DIR = 'video_formats'

AVAILABLE_FORMATS = {}

def load_available_formats():
    # Сканируем директорию с форматами
    for format_name in os.listdir(VIDEO_FORMATS_DIR):
        format_path = os.path.join(VIDEO_FORMATS_DIR, format_name)
        if os.path.isdir(format_path):
            manifest_path = os.path.join(format_path, 'manifest.json')
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                except Exception as e:
                    continue

                entrypoint = "generate.create_video"

                # Формируем полный путь для импорта: VideoFormats.<format_name>.<module_part>
                import_path = f"{VIDEO_FORMATS_DIR}.{format_name}.generate"

                try:
                    print(import_path)
                    module = importlib.import_module(
                        import_path,
                        package = os.getcwd()
                    )
                    generate_video_func = getattr(module, "create_video")
                    AVAILABLE_FORMATS[format_name] = {
                        "function": generate_video_func,
                        "requires": manifest.get('requires', [])
                    }
                    print(f"Загружен формат '{format_name}' с entrypoint '{import_path}.create_video'.")
                except Exception as e:
                    print(f"Ошибка при импорте формата {format_name} (entrypoint: {entrypoint}): {e}")
            else:
                print(f"Файл manifest.json не найден для формата {format_name}.")


def ack_message(channel: pika.channel.Channel, delivery_tag, data):
    """Note that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        logging.error("Channel is closed, cannot ACK message.")

def do_work(connection: pika.BlockingConnection, channel, delivery_tag, body, redis_client,):
    data = json.loads(
        body
    )
    logging.info(f"Received message: {data}")
    logging.info(f"Creating video with format: {data['format_name']}")
    
    create_video = AVAILABLE_FORMATS.get(data["format_name"])["function"]
    
    if create_video is None:
        logging.error(f"Format {data["format_name"]} not found.")
        ack_message(channel, delivery_tag, data)
        status = {
            "video_id": data["video_id"],
            "status": {
                "name": "failed",
                "text": f"Format {data['format_name']} not found."
            },
            "source": data["source"],
            "telegram_params": data.get("telegram_params", None),
            "video_url": None
        }
        update_status(
            redis_client,
            key = f"video:{data['video_id']}",
            status = status
        )                                                 
    update_status(
        redis_client,
        key = f"video:{data['video_id']}",
        status = {
            "video_id": data["video_id"],
            "status": {
                "name": "pending",
                "text": "Video generation is pending."
            },
            "source": data["source"],
            "telegram_params": data.get("telegram_params", None),
            "video_url": None
        }
    )
    if data["source"] == "telegram":
        create_video(
            video_id = data["video_id"],
            redis_client = redis_client,
            chat_id = data["chat_id"],
            status_message_id = data["status_message_id"],
            source = "telegram"
        )
    else:
        create_video(
            video_id = data["video_id"],
            redis_client = redis_client,
            source = "web"
        )
    
    cb = functools.partial(ack_message, channel, delivery_tag, data)
    connection.add_callback_threadsafe(cb)

def on_message(channel, method_frame, header_frame, body, args):
    (connection, threads, redis_client) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target = do_work, args=(connection, channel, delivery_tag, body, redis_client))
    t.start()
    threads.append(t)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host = 'brainrot_automation-rabbit-mq-1',
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue = 'video_generation')

    channel.basic_qos(prefetch_count = 1)

    redis_client = redis.Redis(
        host = 'brainrot_automation-redis-1',
        port = 6379
    )
    
    threads = []
    
    on_message_callback = functools.partial(on_message, args=(connection, threads, redis_client))
    
    channel.basic_consume(
        queue = 'video_generation', 
        on_message_callback = on_message_callback
    )

    logging.info("Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    # Wait for all to complete
    for thread in threads:
        thread.join()

    connection.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    load_available_formats()
    main()