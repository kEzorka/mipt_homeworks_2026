#!/usr/bin/env python

from typing import Any

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


K_COUNT_OF_MONTH = 12
K_FEBRUARY_MONTH_INDEX = 2
K_DEFAULT_FEBRUARY_MAX_DAYS = 28
K_LEAP_FEBRUARY_MAX_DAYS = 29
K_THIRTY = 30
K_THIRTY_ONE = 31

K_INCOME_LENGTH = 2
K_COST_ADD_LENGTH = 3
K_GET_CATEGORY_LENGTH = 1
K_STATS_LENGTH = 1
K_CATEGORY_PARTS_LENGTH = 2

DateT = tuple[int, int, int]
K_DATE_T = 3
NumberT = float | int
CategoryT = str

ExtractedIncomeT = tuple[NumberT, DateT] | None
ExtractedCostT = tuple[CategoryT, NumberT, DateT] | None
ExtractedStatsT = DateT | None

CostsT = dict[CategoryT, NumberT]
DayStatsT = tuple[NumberT, CostsT]
DataBaseT = dict[DateT, DayStatsT]
database: DataBaseT = {}
financial_transactions_storage: list[dict[str, Any]] = []

StatsT = tuple[NumberT, NumberT, NumberT, CostsT]


def is_leap_year(year: int) -> bool:
    if year % 4 == 0:
        return year % 100 != 0 or year % 400 == 0
    return False


def is_month_valid(month: int) -> bool:
    return month in range(1, K_COUNT_OF_MONTH + 1)


def is_year_valid(year: int) -> bool:
    return year > 0


def is_valid_date(day: int, month: int, year: int) -> bool:
    thirty_days_in_month = [4, 6, 9, 11]

    if not is_month_valid(month):
        return False

    if day < 1 or not is_year_valid(year):
        return False

    if month == K_FEBRUARY_MONTH_INDEX:
        max_feb_days = K_LEAP_FEBRUARY_MAX_DAYS if is_leap_year(year) else K_DEFAULT_FEBRUARY_MAX_DAYS
        if day > max_feb_days:
            return False

    if month in thirty_days_in_month and day > K_THIRTY:
        return False

    return day <= K_THIRTY_ONE


def extract_date(maybe_dt: str) -> DateT | None:
    parsed_input = maybe_dt.split("-")

    if len(parsed_input) != K_DATE_T:
        return None

    for element in parsed_input:
        if not element.isdigit():
            return None

    day, month, year = map(int, parsed_input)

    if not is_valid_date(day, month, year):
        return None

    return day, month, year


def date_to_str(date: DateT) -> str:
    return f"{date[0]:02d}-{date[1]:02d}-{date[2]}"


def extract_digit_and_number_from_str(input_str: str) -> tuple[int, str]:
    index = 0
    digit = 1
    while index < len(input_str) and input_str[index] in ("+", "-"):
        if input_str[index] == "-":
            digit = -digit

        index += 1

    return digit, input_str[index:]


def extract_number(input_str: str) -> NumberT | None:
    digit, current_str = extract_digit_and_number_from_str(input_str)

    if current_str == "" or current_str.startswith(",") or current_str.endswith(","):
        return None

    current_str = current_str.replace(",", ".")

    cnt_of_commas = 0
    for symbol in current_str:
        if symbol == ".":
            if cnt_of_commas == 1:
                return None
            cnt_of_commas += 1
        elif not symbol.isdigit():
            return None

    if cnt_of_commas == 0:
        return digit * int(current_str)

    return digit * float(current_str)


# =
# Income functions
# =


def add_income(amount: NumberT, date: DateT) -> None:
    if date not in database:
        database[date] = 0, {}

    income, costs = database[date]
    database[date] = income + amount, costs


def income_handler(amount: NumberT, income_date: str) -> str:
    financial_transactions_storage.append({})
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage[-1] = {"amount": amount, "date": date}
    add_income(amount, date)

    return OP_SUCCESS_MSG


def process_extract_income(input_list: list[str]) -> str:
    if len(input_list) != K_INCOME_LENGTH:
        return UNKNOWN_COMMAND_MSG

    amount = extract_number(input_list[0])
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return income_handler(amount, input_list[1])


def handle_income(input_body: list[str]) -> None:
    print(process_extract_income(input_body))


# =
# Cost functions
# =


def is_category_valid(category: str) -> bool:
    if "." in category or "," in category or "::" not in category:
        return False

    parts = category.split("::")
    if len(parts) != K_CATEGORY_PARTS_LENGTH:
        return False
    common_category, target_category = parts

    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def add_cost(category: CategoryT, amount: NumberT, date: DateT) -> None:
    if date not in database:
        database[date] = 0, {}

    income, costs = database[date]
    if category not in costs:
        costs[category] = 0
    costs[category] += amount

    database[date] = income, costs


def cost_handler(category: CategoryT, amount: NumberT, income_date: str) -> str:
    financial_transactions_storage.append({})
    if not is_category_valid(category):
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage[-1] = {"category": category, "amount": amount, "date": date}
    add_cost(category, amount, date)

    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common_category}::{target_category}"
        for common_category, target_category_list in EXPENSE_CATEGORIES.items()
        for target_category in target_category_list
    )


def process_extract_add_cost(input_list: list[str]) -> str:
    category = input_list[0]
    amount = extract_number(input_list[1])
    date = input_list[2]

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return cost_handler(category, amount, date)


def process_extract_cost(input_list: list[str]) -> str:
    if len(input_list) == K_COST_ADD_LENGTH:
        return process_extract_add_cost(input_list)
    if len(input_list) == K_GET_CATEGORY_LENGTH and input_list[0] == "categories":
        return cost_categories_handler()

    return UNKNOWN_COMMAND_MSG


def handle_cost(input_body: list[str]) -> None:
    print(process_extract_cost(input_body))


# =
# Stats functions
# =


def stats_handler(report_date: str) -> str:
    return f"Statistic for {report_date}"


def process_extract_stats(input_list: list[str]) -> ExtractedStatsT:
    if len(input_list) != K_STATS_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return None

    date = extract_date(input_list[0])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return None

    return date


def is_same_month(lhs_date: DateT, rhs_date: DateT) -> bool:
    if lhs_date[2] != rhs_date[2]:
        return False

    return lhs_date[1] == rhs_date[1]


def reverse_date(date: DateT) -> DateT:
    return date[2], date[1], date[0]


def get_stats(date: DateT) -> StatsT:
    total_fortune: NumberT = 0
    month_income: NumberT = 0
    month_costs_by_category: CostsT = {}

    for key_date in sorted(database, key=reverse_date):
        if reverse_date(key_date) > reverse_date(date):
            break

        total_fortune += database[key_date][0]
        total_fortune -= sum(database[key_date][1].values())

        if is_same_month(date, key_date):
            month_income += database[key_date][0]

            for category in database[key_date][1]:
                month_costs_by_category[category] = (
                    month_costs_by_category.get(category, 0) + database[key_date][1][category]
                )

    return (
        total_fortune,
        month_income,
        sum(month_costs_by_category.values()),
        month_costs_by_category,
    )


def print_stats(date: DateT, stats: StatsT) -> None:
    diff = stats[1] - stats[2]
    kind = "profit" if diff > 0 else "loss"

    print(f"Your statistics as of {date_to_str(date)}:")
    print(f"Total capital: {stats[0]:.2f} rubles")
    print(f"This month, the {kind} amounted to {abs(diff):.2f} rubles.")

    print(f"Income: {stats[1]:.2f} rubles")
    print(f"Expenses: {stats[2]:.2f} rubles")

    print("\nDetails (category: amount):")

    index = 1
    for category, amount in sorted(stats[3].items()):
        print(f"{index}. {category}: {amount:.2f}")
        index += 1


def handle_stats(input_body: list[str]) -> None:
    extracted_stats_data: ExtractedStatsT = process_extract_stats(input_body)
    if extracted_stats_data is None:
        return

    stats = get_stats(extracted_stats_data)
    print_stats(extracted_stats_data, stats)


def handle_command(command: str, body: list[str]) -> None:
    match command:
        case "income":
            handle_income(body)

        case "cost":
            handle_cost(body)

        case "stats":
            handle_stats(body)

        case _:
            print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    while True:
        input_str: str = input()
        if not input_str:
            return

        query: list[str] = input_str.split()
        if not query:
            continue
        command: str = query[0]
        body: list[str] = query[1:]

        handle_command(command, body)


if __name__ == "__main__":
    main()
