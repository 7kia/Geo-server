from key_genetarion.indexGenerator import IndexGenerator
from key_genetarion.tableListGenerator import TableListGenerator

if __name__ == "__main__":
    tableList = []

    numbers = []
    for i in range(1, 9):
        numbers.append(i)
        numbers += range(i * 10, i * 10 + 9)
    numbers.append(0)

    numbersStr = []
    for number in numbers:
        numbersStr.append(str(number) + "_elevation")

    tableList += TableListGenerator.generate_words("n", numbersStr)
    tableList += TableListGenerator.generate_words("p", numbersStr)

    request = ""
    for table in tableList:
        request += IndexGenerator.generate_db_index(table, ["lat", "lng"])
    print(request)
