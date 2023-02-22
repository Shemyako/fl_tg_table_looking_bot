# Подключаем библиотеки
import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	
import google_module.google_config as conf

CREDENTIALS_FILE = 'google_module/token.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

# Запрос к таблице
def get(spreadsheetId:str, range_g):
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

    resp = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_g).execute()
    return resp


def check_1_url(url:str, start_line=1):
    answer = {
        "texts_to_send":[],
        "last_line":start_line
    }

    try:
        resp = get(url, f"'Основная таблица'!D{start_line}:AA100000")
    except BaseException   as e:
        print(e)
        return answer

    if "values" not in resp:
        return answer
    
    if resp["values"] != []:
        for i in resp["values"]:
            if i[3].lower() == conf.url_1_G and \
                    i[2].lower() in conf.url_1_F:
                
                answer["texts_to_send"].append(f"Добрый день, в таблице новая заявка {conf.url_1_F[i[2].lower()]} {i[0]}  ({i[7]})")
        
        answer["last_line"] += len(resp["values"])

    return answer


def check_2_url(url:str, start_line=1):
    answer = {
        "texts_to_send":[],
        "last_line":start_line
    }

    try:
        resp = get(url, f"'Деньги 2022'!C{start_line}:AA100000")
    except BaseException   as e:
        print(e)
        return answer

    if "values" not in resp:
        return answer
    
    line_amount = 0
    if resp["values"] != []:
        for i in resp["values"]:
            
            is_J = ""
            for key in conf.url_2_J:
                if key in i[7].lower():
                    is_J = key


            if i[0].lower() in conf.url_2_C and \
                    is_J in conf.url_2_J and \
                    i[10].lower() in conf.url_2_M and \
                    i[8].lower() in conf.url_2_K:
                
                answer["texts_to_send"].append(f"{conf.url_2_C[i[0].lower()]}💰\nПоступила предоплата {i[6]}₽\nМОП - {i[13]}\nКлиент - {i[12]}\nОплатили {conf.url_2_J[is_J]}\nДата оплаты {i[1]}")
            if i[1] == "" and i[0] == "" and i[2] == "":
                break

            line_amount += 1
        # answer["last_line"] += len(resp["values"])
        answer["last_line"] += line_amount

    return answer
