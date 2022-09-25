import re
import asyncio
import aiofiles
from aioimaplib import aioimaplib


async def get_provider(mail: str):
    pr = mail.split("@")[-1]
    for key, value in providers.items():
        if pr in value:
            return key


async def check_mailbox(queue: asyncio.Queue):
    while not queue.empty():
        mail = await queue.get()
        host = await get_provider(mail)
        imap_client = aioimaplib.IMAP4_SSL(host=host)
        await imap_client.wait_hello_from_server()

        try:
            await imap_client.login(mail, password)
            await imap_client.select(folder)
        except Exception as ex:
            print('\n' + f'{mail}, check password or on imap', ex)

        try:
            response = await imap_client.uid('fetch', '1:*',
                                             '(UID FLAGS BODY.PEEK[HEADER.FIELDS ("From")])')
            for i in response.lines:
                find_mail = str(i).split('<')[-1].split('>')[0]
                clean_mail = re.findall(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$', find_mail)
                if len(clean_mail):
                    mess_list.append(*clean_mail)
            if len(mess_list):
                print('\n' + '=====' + mail + '=====' + '\n' + str(mess_list) + '\n')
            else:
                print(f'{mail} empty')

            async with aiofiles.open('mail_check.txt', mode='a') as f:
                await f.write(f'{mail}' + '\n' + str(mess_list) + '\n\n')

            mess_list.clear()
            await imap_client.logout()

        except Exception as ex:
            print('\n' + f'{mail}', ex)


async def main(emails: list):
    queue = asyncio.Queue()
    for email in emails:
        queue.put_nowait(email)
    tasks = [asyncio.create_task(check_mailbox(queue)) for i in range(5)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    providers = {
        "imap.rambler.ru": [
            'rambler.ru',
            'lenta.ru',
            'autorambler.ru',
            'myrambler.ru',
            'ro.ru',
            'rambler.ua'],
        "imap.mail.ru": ['mail.ru', 'internet.ru', 'bk.ru', 'inbox.ru', 'list.ru'],
        "imap.gmail.com": 'gmail.com',
        "imap.yandex.ru": 'yandex.ru'
    }
    password = input('password: ')
    email_folder = input('drop .txt file with emails: ')
    mess_list = []
    ID_HEADER_SET = {'From'}

    while True:
        folder = int(input('1 - inbox\n'
                           '2 - spam\n'))
        if folder == 1:
            folder = 'INBOX'
            break
        elif folder == 2:
            folder = 'Spam'
            break
        else:
            print('choose 1 or 2')

    with open(email_folder, encoding='utf-8') as file:
        emails = [row.strip() for row in file]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(emails))
    print('work is done!')
