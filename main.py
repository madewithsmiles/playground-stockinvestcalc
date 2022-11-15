from collections import namedtuple
from enum import Enum
from typing import List
from abc import ABC, abstractmethod
from rich.console import Console
from rich.table import Column, Table
import calendar

# investigate rich = https://pythonawesome.com/a-python-library-for-rich-text-and-beautiful-formatting-in-the-terminal/

InvestmentSuggestionFields = ('SharesToBuy', 
                            'InvestmentValue',
                            'WillReachTargetBalanceAtPrice', 
                            'CurrentPrice', 
                            'TargetBalance')
InvestmentSuggestion = namedtuple('InvestSuggestion', 
                                  InvestmentSuggestionFields, 
                                  defaults=[-1]*len(InvestmentSuggestionFields))

DEFAULT_INVEST_SUGGESTION = InvestmentSuggestion()

InvestmentValue = namedtuple('InvestmentValue', ['InitialInvestment', 'Price', 'Shares', 'NextPrice', 'Value', 'Profit'])

CalcArgFields = ('current_price',
                'old_price',
                'target_price',
                'target_balance',
                'intended_investment_amount',
                'next_prices',
                'verbose',
                'starting_balance', 'monthly_payment', 'apr', 'starting_month', 'starting_year')
CalcArguments = namedtuple('CalcArguments', CalcArgFields, defaults=(False,) * len(CalcArgFields))


ConstantMonthlyLoanPaymentFields = ('starting_balance', 'monthly_payment', 'apr', 'starting_month', 'starting_year', 'remaining_payments')
ConstantMonthlyLoanPayment = namedtuple('ConstantMonthlyLoanPayment', ConstantMonthlyLoanPaymentFields, defaults=(None,) * len(ConstantMonthlyLoanPaymentFields))

RemainingMonthlyPaymentFields = ('payment_number', 'month_and_year', 'remaining_balance', 'monthly_payment', 'balance_after_payment', 'balance_after_payment_plus_interest')
RemainingMonthlyPayment = namedtuple('RemainingMonthlyPayment', RemainingMonthlyPaymentFields, defaults=(None,) * len(RemainingMonthlyPaymentFields))
get_total_payments = lambda rmp: sum([payment.monthly_payment for payment in rmp])
get_total_interest = lambda rmp: sum([payment.balance_after_payment_plus_interest - payment.balance_after_payment for payment in rmp])

class GregorianLikeCalendarMonthUtils:
    _month_abbr_to_idx = {m:i for i,m in enumerate(calendar.month_abbr) if i>0}
    _month_name_to_idx = {m:i for i,m in enumerate(calendar.month_name) if i>0}
    _idx_to_month_abbr = {month_to_idx[1]:month_to_idx[0] for month_to_idx in list(_month_abbr_to_idx.items())}

    @staticmethod
    def get_month_idx(month: str) -> int:
        # integer input
        try:
            value = -1
            value = int(month)
            if value in GregorianLikeCalendarMonthUtils._idx_to_month_abbr:
                return value
        except:
            pass

        # abbr input
        if GregorianLikeCalendarMonthUtils._month_abbr_to_idx.get(month.lower().title(), None):
            return GregorianLikeCalendarMonthUtils._month_abbr_to_idx[month.lower().title()]

        # full input
        if GregorianLikeCalendarMonthUtils._month_name_to_idx.get(month.lower().title(), None):
            return GregorianLikeCalendarMonthUtils._month_name_to_idx[month.lower().title()]
        
        raise Exception(f"Couldn't parse month input: {month}")

    @staticmethod
    def get_month_year_display(month_idx:int, year:int):
        if 1 <= month_idx <= 12:
            return f'{GregorianLikeCalendarMonthUtils._idx_to_month_abbr[month_idx]}-{year}'
        raise Exception(f"Invalid month index: {month_idx}")

    @staticmethod
    def get_next_month(month_idx:int, year:int):
        if 1 <= month_idx <= 12:
            if month_idx == 12:
                return (1, year + 1)
            else:
                return (month_idx + 1, year)
        raise Exception(f"Invalid month index: {month_idx}")

class Logger(ABC):
    @abstractmethod
    def success(self, msg):
        pass

    @abstractmethod
    def info(self, msg):
        pass

    @abstractmethod
    def verbose(self, msg):
        pass

    @abstractmethod
    def error(self, msg):
        pass

class ConsoleLogger(Logger):
    class bcolors: # https://stackoverflow.com/a/21786287
        HEADER = '\x1b[95m' # '\033[95m'
        VERBOSE = '\x1b[2;30;44m'
        OKBLUE = '\x1b[94m' # '\033[94m'
        OKCYAN = '\x1b[0;34;40m' # '\033[96m'
        OKGREEN = '\x1b[6;30;42m' # '\033[92m'
        WARNING = '\x1b[93m' # '\033[93m'
        FAIL = '\x1b[1;31;40m' # '\033[91m'
        ENDC = '\x1b[0m' # '\033[0m'
        BOLD = '\x1b[1m' # '\033[1m'
        UNDERLINE = '\x1b[4m' # '\033[4m'

    def success(self, msg):
        if msg and (isinstance(msg, InvestmentSuggestion) or isinstance(msg, InvestmentValue) or (isinstance(msg, list) and isinstance(msg[0], InvestmentSuggestion) or isinstance(msg[0], InvestmentValue))):
            self.success_investments(msg)
        elif msg and (isinstance(msg, list) and isinstance(msg[0], RemainingMonthlyPayment)):
            self.monthly_payments(msg)
        else:
            print(f'{ConsoleLogger.bcolors.OKGREEN}{msg}{ConsoleLogger.bcolors.ENDC}')

    def info(self, msg):
        print(f'{ConsoleLogger.bcolors.OKBLUE}{msg}{ConsoleLogger.bcolors.ENDC}')

    def verbose(self, msg):
        print(f'{ConsoleLogger.bcolors.VERBOSE}{msg}{ConsoleLogger.bcolors.ENDC}')

    def error(self, msg):
        print(f'{ConsoleLogger.bcolors.FAIL}{msg}{ConsoleLogger.bcolors.ENDC}')

    def warn(self, msg):
        print(f'{ConsoleLogger.bcolors.WARNING}{msg}{ConsoleLogger.bcolors.ENDC}')

    def success_investments(self, invsts):
        console = Console()

        table = Table(show_header=True, header_style="bold magenta")
        is_list = isinstance(invsts, list)
        headers = invsts[0]._fields if is_list else invsts._fields
        for header in headers:
            table.add_column(header, justify="right")

        if is_list:
            for inv in invsts:
                table.add_row(*[str(i) for i in inv._asdict().values()])
        else:
            table.add_row(*[str(i) for i in invsts._asdict().values()])

        console.print(table)

    def monthly_payments(self, monthly_payments: List[RemainingMonthlyPayment]):
        if not monthly_payments:
            self.error('No monthly payments to print')

        console = Console()

        table = Table(show_header=True, header_style="bold magenta")
        self.info(f'Monthly payment is ${monthly_payments[0].monthly_payment}')
        header = ['Payment#', 'Month-Year', 'RemainingBalance', 'Payment', 'AfterPayment', 'AfterPayment+Interest']
        for col_name in header:
            table.add_column(col_name, justify="right")
        
        for monthly_payment in monthly_payments:
            table.add_row(*[str(i) for i in monthly_payment._asdict().values()])

        self.info(f'There will be {len(monthly_payments)} payments in total (1 per month from {monthly_payments[0].month_and_year} until {monthly_payments[-1].month_and_year})')
        self.info(f'The amount of interest you\'ll pay is: ${round(get_total_interest(monthly_payments),2)}')
        self.info(f'In total, you will pay around: ${round(get_total_payments(monthly_payments),2)}')

        console.print(table)

class CalcType(Enum):
    # Calculate based on
    PREVIOUS_GROWTH = 0
    TARGET_PRICE = 1
    MISSED_INVESTMENT = 2
    POTENTIAL_INVESTMENT = 3
    CONSTANT_LOAN_OR_CREDIT_PAYMENT = 4

class CalcFactory():
    @staticmethod
    def get_calc_function(case: CalcType):
        log = ConsoleLogger()
        log.verbose(f'Case={case}')
        if case == CalcType.PREVIOUS_GROWTH:
            log.verbose(f'Will calculate based on previous growth (Case = {CalcType.PREVIOUS_GROWTH})')
            return (CalcFactory.calc_invest_given_previous_growth, 
            CalcArguments(current_price=True, old_price=True, target_balance=True, verbose=True))
        if case == CalcType.TARGET_PRICE:
            log.verbose(f'Will calculate based on target price (Case = {CalcType.TARGET_PRICE})')
            return (CalcFactory.calc_invest_given_target_price,
            CalcArguments(current_price=True, target_price=True, target_balance=True, verbose=True))
        if case == CalcType.MISSED_INVESTMENT:
            log.verbose(f'Will calculate missed investment {CalcType.MISSED_INVESTMENT}')
            return (CalcFactory.calc_invest_for_missed_opportunity,
            CalcArguments(intended_investment_amount=True, current_price=True, old_price=True, verbose=True))
        elif case == CalcType.POTENTIAL_INVESTMENT:
            log.verbose(f'Will calculate potential investment opportunity {CalcType.POTENTIAL_INVESTMENT}')
            return (CalcFactory.calc_invest_potential_investment,
            CalcArguments(intended_investment_amount=True, current_price=True, next_prices=True, verbose=True))
        elif case == CalcType.CONSTANT_LOAN_OR_CREDIT_PAYMENT:
            log.verbose(f'Will calculate constant monthly loan payments {CalcType.CONSTANT_LOAN_OR_CREDIT_PAYMENT}')
            return (CalcFactory.calc_constant_monthly_loan_payments,
                CalcArguments(starting_balance=True, monthly_payment=True, apr=True, starting_month=True, starting_year=True, verbose=True))


    @staticmethod
    def calc_invest_given_previous_growth(current_price, old_price, target_balance, verbose=False):
        rate_of_change = get_price_change_rate_from_old_price(old_price, current_price)
        if verbose:
            ConsoleLogger().verbose(f'{CalcType.PREVIOUS_GROWTH}: price grew by {rate_of_change:,} ({round(rate_of_change * 100, 3):,}%)')
        next_price = current_price * rate_of_change
        
        if next_price == 0:
            if verbose:
                ConsoleLogger().error('current_price * rate_of_change is zero.')
            return DEFAULT_INVEST_SUGGESTION

        return get_suggested_investment_given_target_balance_and_target_price(
            current_price, next_price, target_balance)
    
    @staticmethod
    def calc_invest_given_target_price(current_price, target_price, target_balance, verbose=False):
        if target_price == 0:
            if verbose:
                ConsoleLogger().error('target_price is zero.')
            return DEFAULT_INVEST_SUGGESTION

        return get_suggested_investment_given_target_balance_and_target_price(
            current_price, target_price, target_balance)

    @staticmethod
    def calc_invest_for_missed_opportunity(intended_investment_amount, current_price, old_price, verbose=False):
        return get_investment_value_when_price_changes(investment_amount=intended_investment_amount, current_price=old_price, next_price=current_price)

    def calc_invest_potential_investment(intended_investment_amount: float, current_price: float, next_prices: List[float], verbose: bool=False):
        return [get_investment_value_when_price_changes(investment_amount=intended_investment_amount, 
                                                        current_price=current_price, 
                                                        next_price=next_price) for next_price in next_prices]

    @staticmethod
    def calc_constant_monthly_loan_payments(starting_balance, monthly_payment, apr, starting_month, starting_year, verbose=False):
        remaining_balance = starting_balance
        year = int(starting_year)
        month_idx = GregorianLikeCalendarMonthUtils.get_month_idx(starting_month)
        monthly_apr = apr / 12 / 100
        remaining_payments = []
        i = 0
        limit = 12*5 # 12 months * number of years
        while i < limit and remaining_balance > 0:
            nxt_monthly_payment = min(monthly_payment, remaining_balance)
            balance_after_payment = remaining_balance - nxt_monthly_payment
            balance_after_payment_plus_interest = balance_after_payment + (balance_after_payment * monthly_apr)
            remaining_payments.append(
                RemainingMonthlyPayment(
                    payment_number=i+1,
                    month_and_year=GregorianLikeCalendarMonthUtils.get_month_year_display(month_idx=month_idx, year=year),
                    remaining_balance=round(remaining_balance, 2),
                    monthly_payment=round(nxt_monthly_payment, 2),
                    balance_after_payment=round(balance_after_payment, 2), 
                    balance_after_payment_plus_interest=round(balance_after_payment_plus_interest, 2))
            )
            i += 1
            month_idx, year = GregorianLikeCalendarMonthUtils.get_next_month(month_idx=month_idx, year=year)
            monthly_payment = nxt_monthly_payment
            remaining_balance = balance_after_payment_plus_interest

        if i == limit:
            ConsoleLogger().warn(f'Reached limits. This means that calculations reach or will exceed {limit // 12} years....')

        return remaining_payments

def get_investment_value_when_price_changes(investment_amount, current_price, next_price):
    nbr_of_shares = investment_amount / current_price
    value = (nbr_of_shares * next_price)
    profit = value - investment_amount
    return InvestmentValue(
        InitialInvestment=investment_amount,
        Price=current_price, 
        Shares=nbr_of_shares, 
        NextPrice=next_price, 
        Value=value,
        Profit=profit)

def get_price_change_rate_from_old_price(old_price, current_price):
    return current_price / old_price

def get_suggested_investment_given_target_balance_and_target_price(current_price, target_price, target_balance):
    shares_to_buy = target_balance / target_price
    estimated_investment = current_price * shares_to_buy
    return InvestmentSuggestion(SharesToBuy=shares_to_buy, 
                                InvestmentValue=estimated_investment, 
                                WillReachTargetBalanceAtPrice = target_price, 
                                CurrentPrice=current_price,
                                TargetBalance=target_balance)

def get_input_with_retry(prompt, max_retries, transform_and_validate_function):
    inpt = ''
    is_valid = False
    transformation = None
    attempt = 0
    while not is_valid and attempt < max_retries:
        try:
            inpt = input(prompt)
            if inpt == 'exit':
                return inpt
            is_valid, transformation = transform_and_validate_function(inpt)
        except Exception as ex:
            is_valid = False
            ConsoleLogger().error(f'Erroneous input. {ex}')
        finally:
            attempt += 1
    if is_valid:
        return transformation
    else: 
        raise Exception("Reached max retries or entered 'exit' ")

def transform_and_validate_to_float(inpt):
    return float(inpt) > 0, float(inpt)

def transform_and_validate_to_int(inpt):
    return int(inpt) > 0, int(inpt)

def transform_and_validate_str_with_sep_to_float_list(inpt):
    sep = ', '
    value = [float(v) for v in inpt.split(sep)]
    return len(value) > 0, value

def transform_and_validate_month_input(inpt):
    value = GregorianLikeCalendarMonthUtils.get_month_idx(inpt)
    return True, value

def get_arguments(arg_list, max_retries=3):
    calc_arg = {}
    log = ConsoleLogger()
    log.verbose(f'Maximum allowed retries for each input: {max_retries}')
    for accepted_arg in arg_list:
            value = None
            prompt = '>>> ' + accepted_arg
            if accepted_arg != 'verbose':
                if accepted_arg == 'next_prices':
                    sep = ' ,'
                    prompt += f' (separated by space and comma {sep}): '
                    value = get_input_with_retry(prompt, max_retries, transform_and_validate_str_with_sep_to_float_list)
                elif accepted_arg == 'starting_month':
                    value = get_input_with_retry(prompt + ': ', max_retries, transform_and_validate_function=transform_and_validate_month_input)
                elif accepted_arg == 'starting_year':
                    value = get_input_with_retry(prompt + ': ', max_retries, transform_and_validate_function=transform_and_validate_to_int)
                else:
                    if accepted_arg == 'apr':
                        prompt += " (%)"
                    value = get_input_with_retry(prompt + ': ', max_retries, transform_and_validate_to_float)
                log.verbose(f'{accepted_arg}={value}')

            if value == 'exit':
                raise Exception('Cancelled')
            
            calc_arg[accepted_arg] = value
    return calc_arg

def main_interactive():
    input_value = -2
    verbose = True
    log = ConsoleLogger()
    pretty_print_enum_spec = lambda enum_value_spec: repr(enum_value_spec).replace('CalcType', '').replace('<', '').replace('>', '').replace('.', '')  
    options = [pretty_print_enum_spec(type_info) for type_info in list(CalcType)]
    options_str = "\n\t".join(options)
    prompt = f'Choose calc option:\n\t{options_str}\n-1 or \'exit\' to exit: '
    main_input_validation = lambda inpt: (inpt == 'exit' or (int(inpt) >= -1 or int(inpt) <= 3), int(inpt) if inpt != 'exit' else 'exit')
    
    while input_value != -1:
        log.info('\nCalcInvest v0')
        try:
            inpt = get_input_with_retry(prompt, max_retries=1, transform_and_validate_function=main_input_validation)
            log.verbose(f'Entered={inpt}')
            if inpt == 'exit':
                return
            input_value = int(inpt)

            if input_value == -1:
                continue

            calc_function, calc_function_arg_specs = CalcFactory.get_calc_function(case=CalcType(input_value))
            calc_arg = {}
            accepted_arguments = [arg[0] for arg in calc_function_arg_specs._asdict().items() if arg[1]]
            calc_arg.update(get_arguments(accepted_arguments))
            calc_arg['verbose'] = verbose
            
            if verbose:
                log.verbose(calc_arg)

            log.info('Result: ')
            log.success(calc_function(**calc_arg))

        except Exception as ex:
            if verbose:
                ConsoleLogger().error(f'Invalid value entered. {ex}')
            input_value = -2
        


        

def main():
    main_interactive()

if __name__ == "__main__":
    main()

