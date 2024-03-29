import csv
import asyncio
import aiocsv
import aiofiles
from aioimaplib import aioimaplib
from email.header import decode_header


def get_provider(mail: str):
    pr = mail.split('@')[-1]
    for key, value in providers.items():
        if pr in value:
            return key


async def write_csv(all_data: dict):
    async with aiofiles.open(csv_file, 'a') as csvfile:
        writer = aiocsv.AsyncWriter(csvfile, delimiter=';')
        for email, data in all_data.items():
            for sender, title in data.items():
                await writer.writerow([email, sender, title])
                email = ''


async def check_mailbox(email: list):
    while email:
        mail = email.pop(0)
        host = get_provider(mail)

        try:
            imap_client = aioimaplib.IMAP4_SSL(host=host)
            await imap_client.wait_hello_from_server()
            await imap_client.login(mail, password)
            await imap_client.select(email_folder)
        except Exception as ex:
            print('\n' + f'{mail}, check password or on imap', ex)

        try:
            response = await imap_client.uid('fetch', '1:*', '(UID FLAGS BODY.PEEK[HEADER.FIELDS ("From", "Subject")])')
            await imap_client.logout()
            for i in response.lines:
                if '@' in str(i):
                    sender = str(i).split('<')[-1].split('>')[0]
                    title = str(i).split('Subject: ')[-1].split(r'\r')[0]

                    # decode title
                    if title.startswith('='):
                        title = decode_header(title)[0][0].decode()
                    mess_dict[sender] = title

                    # make list with mail data
                    data_list.append(sender)
                    data_list.append(title)

            # make dict from list
            mail_dict = dict(zip(*[iter(data_list)] * 2))
            data_dict[mail] = mail_dict

            print(data_dict)
            await write_csv(data_dict)
            data_dict.clear()
            data_list.clear()

        except Exception as ex:
            print('\n' + f'{mail}', ex)


async def main():
    tasks = [asyncio.create_task(check_mailbox(emails)) for _ in range(5)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    providers = {
        'imap.rambler.ru': [
            'rambler.ru',
            'lenta.ru',
            'autorambler.ru',
            'myrambler.ru',
            'ro.ru',
            'rambler.ua'],
        'imap.mail.ru': ['mail.ru', 'internet.ru', 'bk.ru', 'inbox.ru', 'list.ru'],
        'imap.gmail.com': 'gmail.com'
    }
    email_file = input('drop .txt file with emails: ')
    password = input('email password: ')
    data_list = []
    data_dict = {}
    mess_dict = {}
    csv_file = None

    while True:
        email_folder = int(input('1 - inbox\n'
                                 '2 - spam\n'))
        if email_folder == 1:
            email_folder = 'INBOX'
            csv_file = 'email_check.csv'
            break
        elif email_folder == 2:
            email_folder = 'Spam'
            csv_file = 'email_check_spam.csv'
            break
        else:
            print('choose 1 or 2')

    with open(csv_file, 'w', newline='') as cfile:
        w = csv.writer(cfile, delimiter=';')
        w.writerow(['email', 'sender', 'title'])

    with open(email_file, encoding='utf-8') as file:
        emails = [row.strip() for row in file]

    asyncio.run(main())
    print('work is done!')
