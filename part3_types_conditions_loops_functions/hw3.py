#!/usr/bin/env python

from typing import Any

ALLOWED_AMOUNT_SYMBOLS = "0123456789.,"

AMOUNT_KEY = "amount"
DATE_KEY = "date"
MAIN_CAT_KEY = "main"
SUB_CAT_KEY = "sub"

DATE_LEN = 10
DATE_FRAGMENTS = 3

DAY_INDEX = 0
MONTH_INDEX = 1
YEAR_INDEX = 2
COST_CATEGORIES_ARGS = 2

MONTHS_NUMBER = 12
FEBRUARY_NUMBER = 2
FEBRUARY_DAYS_COUNT = 29
FEBRUARY_DAYS_NORMAL = 28

MONTH_DAYS = (
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
)

INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2

CMD_INCOME = "income"
CMD_COST = "cost"
CMD_STATS = "stats"
CMD_CATEGORIES = "categories"

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


IncomeDict = dict[str, Any]
ExpenseDict = dict[str, Any]
financial_transactions_storage: list[dict[str, Any]] = []
incomes: list[IncomeDict] = []
expenses: list[ExpenseDict] = []



def is_leap_year(year: int) -> bool:
    if year % 4 != 0 and year > 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0

def extract_date(maybe_date: str) -> tuple[int, int, int] | None:
    if len(maybe_date) != DATE_LEN:
        return None
    if maybe_date[2] != "-" or maybe_date[5] != "-":
        return None

    day_str, month_str, year_str = maybe_date[:2], maybe_date[3:5], maybe_date[6:]

    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None

    day, month, year = int(day_str), int(month_str), int(year_str)

    if not (1 <= month <= MONTHS_NUMBER):
        return None

    feb = FEBRUARY_DAYS_COUNT if is_leap_year(year) else FEBRUARY_DAYS_NORMAL
    month_days = list(MONTH_DAYS)
    month_days[FEBRUARY_NUMBER - 1] = feb

    if not (1 <= day <= month_days[month - 1]):
        return None

    return day, month, year

def date_less_or_equal(date_one: tuple[int, int, int], date_two: tuple[int, int, int]) -> bool:
    return (date_one[YEAR_INDEX], date_one[MONTH_INDEX], date_one[DAY_INDEX]) <= \
           (date_two[YEAR_INDEX], date_two[MONTH_INDEX], date_two[DAY_INDEX])

def is_valid_category(category_string: str) -> bool:
    if "::" not in category_string:
        return False
    main, sub = category_string.split("::", 1)
    return main in EXPENSE_CATEGORIES and sub in EXPENSE_CATEGORIES[main]

def all_categories_str() -> str:
    return "\n".join(
        f"{main}::{sub}"
        for main, subs in EXPENSE_CATEGORIES.items()
        for sub in subs
    )

def parse_amount(amount_string: str) -> float:
    return float(amount_string.replace(",", "."))

def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)

    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({
        AMOUNT_KEY: amount,
        DATE_KEY: date_tuple,
    })

    incomes.append({
        AMOUNT_KEY: amount,
        DATE_KEY: date_tuple
    })

    return OP_SUCCESS_MSG

def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_valid_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    date_tuple = extract_date(income_date)

    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({
        "category": category_name,
        AMOUNT_KEY: amount,
        DATE_KEY: date_tuple,
    })

    main, sub = category_name.split("::", 1)

    expenses.append({
        MAIN_CAT_KEY: main,
        SUB_CAT_KEY: sub,
        AMOUNT_KEY: amount,
        DATE_KEY: date_tuple
    })

    return OP_SUCCESS_MSG

def cost_categories_handler() -> str:
    return all_categories_str()

def stats_handler(report_date: str) -> str:
    target_date = extract_date(report_date)
    if target_date is None:
        return INCORRECT_DATE_MSG

    _, target_month, target_year = target_date

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    categories: dict[str, float] = {}

    for inc in incomes:
        if date_less_or_equal(inc[DATE_KEY], target_date):
            total_capital += inc[AMOUNT_KEY]
        if inc[DATE_KEY][MONTH_INDEX] == target_month and inc[DATE_KEY][YEAR_INDEX] == target_year:
            month_income += inc[AMOUNT_KEY]

    for exp in expenses:
        if date_less_or_equal(exp[DATE_KEY], target_date):
            total_capital -= exp[AMOUNT_KEY]
        if exp[DATE_KEY][MONTH_INDEX] == target_month and exp[DATE_KEY][YEAR_INDEX] == target_year:
            month_expenses += exp[AMOUNT_KEY]
            categories[exp[SUB_CAT_KEY]] = categories.get(exp[SUB_CAT_KEY], 0.0) + exp[AMOUNT_KEY]

    month_result = month_income - month_expenses

    print(f"Your statistics as of {report_date}:")
    print(f"Total capital: {total_capital} rubles")
    if month_result < 0:
        print(f"This month, the loss amounted to {abs(month_result)} rubles")
    else:
        print(f"This month, the profit amounted to {month_result} rubles")
    print(f"Income: {month_income} rubles")
    print(f"Expenses: {month_expenses} rubles")
    print()
    print("Details (category: amount):")

    for index, category_name in enumerate(sorted(categories.keys()), start=1):
        print(f"{index}. {category_name}: {categories[category_name]}")
    return f"Statistic for {report_date}"

def process_income(command_parts: list[str]) -> None:
    if len(command_parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_value = parse_amount(command_parts[1])
    if amount_value <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if extract_date(command_parts[2]) is None:
        print(INCORRECT_DATE_MSG)
        return

    print(income_handler(amount_value, command_parts[2]))

def process_cost(command_parts: list[str]) -> None:
    if len(command_parts) == COST_CATEGORIES_ARGS and command_parts[1] == CMD_CATEGORIES:
        print(all_categories_str())
        return

    if len(command_parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    category_name, amount_string, date_string = command_parts[1], command_parts[2], command_parts[3]

    if not is_valid_category(category_name):
        print(NOT_EXISTS_CATEGORY)
        print(all_categories_str())
        return

    amount_value = parse_amount(amount_string)
    if amount_value <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if extract_date(date_string) is None:
        print(INCORRECT_DATE_MSG)
        return

    print(cost_handler(category_name, amount_value, date_string))

def process_stats(command_parts: list[str]) -> None:
    if len(command_parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date_string = command_parts[1]
    if extract_date(date_string) is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_handler(date_string)

def dispatch_command(command_parts: list[str]) -> None:
    command = command_parts[0]

    if command == CMD_INCOME:
        process_income(command_parts)
    elif command == CMD_COST:
        process_cost(command_parts)
    elif command == CMD_STATS:
        process_stats(command_parts)
    else:
        print(UNKNOWN_COMMAND_MSG)

def main() -> None:
    while True:
        user_line = input()
        if not user_line:
            break

        user_line = user_line.strip()
        if not user_line:
            continue

        command_parts = user_line.split()
        dispatch_command(command_parts)


if __name__ == "__main__":
    main()
