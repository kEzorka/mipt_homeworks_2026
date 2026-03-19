#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

K_COUNT_OF_MONTH = 12
K_FEBRUARY_MONTH_INDEX = 2
K_DEFAULT_FEBRUARY_MAX_DAYS = 28
K_LEAP_FEBRUARY_MAX_DAYS = 29
K_THIRTY = 30
K_THIRTY_ONE = 31

K_INCOME_LENGTH = 2
K_COST_LENGTH = 3
K_STATS_LENGTH = 1

DATE_T = tuple[int, int, int]
K_DATE_T_LENGTH = 3
NUMBER_T = float | int
CATEGORY_T = str

EXTRACTED_INCOME_T = tuple[NUMBER_T, DATE_T] | None
EXTRACTED_COST_T = tuple[CATEGORY_T, NUMBER_T, DATE_T] | None
EXTRACTED_STATS_T = DATE_T | None

COSTS_T = dict[CATEGORY_T, NUMBER_T]
DAY_STATS_T = tuple[NUMBER_T, COSTS_T]
DATABASE_T = dict[DATE_T, DAY_STATS_T]
database: DATABASE_T = {}

STATS_T = tuple[NUMBER_T, NUMBER_T, NUMBER_T, COSTS_T]


def is_leap_year(year: int) -> bool:
    if year % 4 == 0:
        return year % 100 != 0 or year % 400 == 0
    return False


def is_month_valid(month: int) -> bool:
    return month in range(1, 12)


def is_valid_date(day: int, month: int, year: int) -> bool:
    thirty_days_in_month = [4, 6, 9, 11]

    if not is_month_valid(month):
        return False

    if is_leap_year(year) and month == K_FEBRUARY_MONTH_INDEX and day > K_LEAP_FEBRUARY_MAX_DAYS:
        return False

    if month == K_FEBRUARY_MONTH_INDEX and day > K_DEFAULT_FEBRUARY_MAX_DAYS:
        return False

    if month in thirty_days_in_month and day > K_THIRTY:
        return False

    return day <= K_THIRTY_ONE


def extract_date(maybe_dt: str) -> DATE_T | None:
    parsed_input = maybe_dt.split("-")

    if len(parsed_input) != K_DATE_T_LENGTH:
        return None

    for element in parsed_input:
        if not element.isdigit():
            return None

    day, month, year = map(int, parsed_input)

    if not is_valid_date(day, month, year):
        return None

    return year, month, day


def date_to_str(date: DATE_T) -> str:
    return f"{date[2]}-{date[1]}-{date[0]}"


def extract_digit_and_number_from_str(input_str: str) -> tuple[int, str]:
    index: int = 0
    digit: int = 0
    while index < len(input_str) and input_str[index] in ("+", "-"):
        if input_str[index] == "-":
            digit = (digit + 1) % 2

        index += 1

    return digit, input_str[index:]


def extract_number(input_str: str) -> NUMBER_T | None:
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
        return int((-1) ** digit) * int(current_str)

    return int((-1) ** digit) * float(current_str)


# =
# Income functions
# =


def process_extract_income(input_list: list[str]) -> EXTRACTED_INCOME_T:
    if len(input_list) != K_INCOME_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return None

    amount = extract_number(input_list[0])
    date = extract_date(input_list[1])

    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return None

    if amount < 0:
        print(NONPOSITIVE_VALUE_MSG)
        return None

    if date is None:
        print(INCORRECT_DATE_MSG)
        return None

    return amount, date


def add_income(amount: NUMBER_T, date: DATE_T) -> None:
    if date not in database:
        database[date] = 0, {}

    income, costs = database[date]
    database[date] = income + amount, costs

    print(OP_SUCCESS_MSG)


def handle_income(input_body: list[str]) -> None:
    extracted_income_data: EXTRACTED_INCOME_T = process_extract_income(input_body)
    if extracted_income_data is None:
        return

    add_income(*extracted_income_data)


# =
# Cost functions
# =


def process_extract_cost(input_list: list[str]) -> EXTRACTED_COST_T:
    if len(input_list) != K_COST_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return None

    category = input_list[0]
    amount = extract_number(input_list[1])
    date = extract_date(input_list[2])

    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return None

    if amount < 0:
        print(NONPOSITIVE_VALUE_MSG)
        return None

    if date is None:
        print(INCORRECT_DATE_MSG)
        return None

    return category, amount, date


def add_cost(category: CATEGORY_T, amount: NUMBER_T, date: DATE_T) -> None:
    if not amount:
        print(UNKNOWN_COMMAND_MSG)
    elif not date:
        print(INCORRECT_DATE_MSG)

    if date not in database:
        database[date] = 0, {}

    income, costs = database[date]
    if category not in costs:
        costs[category] = 0
    costs[category] += amount

    database[date] = income, costs

    print(OP_SUCCESS_MSG)


def handle_cost(input_body: list[str]) -> None:
    extracted_cost_data: EXTRACTED_COST_T = process_extract_cost(input_body)
    if extracted_cost_data is None:
        return

    add_cost(*extracted_cost_data)


# =
# Stats functions
# =


def process_extract_stats(input_list: list[str]) -> EXTRACTED_STATS_T:
    if len(input_list) != K_STATS_LENGTH:
        print(INCORRECT_DATE_MSG)
        return None

    return extract_date(input_list[0])


def is_same_month(lhs_date: DATE_T, rhs_date: DATE_T) -> bool:
    if lhs_date[0] != rhs_date[0]:
        return False

    return lhs_date[1] == rhs_date[1]


def get_stats(date: DATE_T) -> STATS_T:
    total_fortune: NUMBER_T = 0
    month_income: NUMBER_T = 0
    month_costs_by_category: COSTS_T = {}

    for key_date in sorted(database):
        if key_date > date:
            break

        total_fortune += database[key_date][0]
        total_fortune -= sum(database[key_date][1].values())

        if is_same_month(date, key_date):
            month_income += database[key_date][0]

            for category in database[key_date][1]:
                month_costs_by_category[category] = (
                    month_costs_by_category.get(category, 0)
                    + database[key_date][1][category]
                )

    return (total_fortune,
            month_income,
            sum(month_costs_by_category.values()),
            month_costs_by_category,
            )


def print_stats(date: DATE_T, stats: STATS_T) -> None:
    diff = stats[1] - stats[2]
    kind = "profit" if diff > 0 else "loss"

    print(f"Your statistics as of {date_to_str(date)}:")
    print(f"Total capital: {stats[0]:.2f} rubles")
    print(f"This month, the {kind} amounted to {abs(diff):.2f} rubles")

    print("Income: "
          f"{stats[1]:.2f} rubbles")
    print("Expenses: "
          f"{stats[2]:.2f} rubbles")

    print("\nDetails (category: amount):")

    index = 1
    for (category, amount) in stats[3].items():
        print(f"{index}. {category}: {amount:.2f}")
        index += 1


def handle_stats(input_body: list[str]) -> None:
    extracted_stats_data: EXTRACTED_STATS_T = process_extract_stats(input_body)
    if extracted_stats_data is None:
        return

    stats = get_stats(extracted_stats_data)
    print_stats(extracted_stats_data, stats)


def handle_command(command: str, body: list[str]) -> None:
    if command == "income":
        handle_income(body)

    elif command == "cost":
        handle_cost(body)

    elif command == "stats":
        handle_stats(body)

    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    while True:
        input_str: str = input()
        if not input_str:
            return

        query: list[str] = input().split()
        command: str = query[0]
        body: list[str] = query[1:]

        handle_command(command, body)


if __name__ == "__main__":
    main()
