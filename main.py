from collections import namedtuple
from enum import Enum
from typing import List
from abc import ABC, abstractmethod

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
                'verbose')
CalcArguments = namedtuple('CalcArguments', CalcArgFields, defaults=(False,) * len(CalcArgFields))

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
        print(f'{ConsoleLogger.bcolors.OKGREEN}{msg}{ConsoleLogger.bcolors.ENDC}')

    def info(self, msg):
        print(f'{ConsoleLogger.bcolors.OKBLUE}{msg}{ConsoleLogger.bcolors.ENDC}')

    def verbose(self, msg):
        print(f'{ConsoleLogger.bcolors.VERBOSE}{msg}{ConsoleLogger.bcolors.ENDC}')

    def error(self, msg):
        print(f'{ConsoleLogger.bcolors.FAIL}{msg}{ConsoleLogger.bcolors.ENDC}')



class CalcType(Enum):
    # Calculate based on
    PREVIOUS_GROWTH = 0
    TARGET_PRICE = 1
    MISSED_INVESTMENT = 2
    POTENTIAL_INVESTMENT = 3
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
        else:
            log.verbose(f'Will calculate potential investment opportunity {CalcType.POTENTIAL_INVESTMENT}')
            return (CalcFactory.calc_invest_potential_investment,
            CalcArguments(intended_investment_amount=True, current_price=True, next_prices=True, verbose=True))
    
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

def transform_and_validate_str_with_sep_to_float_list(inpt):
    sep = ', '
    value = [float(v) for v in inpt.split(sep)]
    return len(value) > 0, value

def get_arguments(arg_list, max_retries=3):
    calc_arg = {}
    log = ConsoleLogger()
    for accepted_arg in arg_list:
            value = None
            prompt = '>>> ' + accepted_arg
            if accepted_arg != 'verbose':
                if accepted_arg == 'next_prices':
                    sep = ' ,'
                    prompt += f' (separated by space and comma {sep}): '
                    value = get_input_with_retry(prompt, max_retries, transform_and_validate_str_with_sep_to_float_list)
                else:
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
            inpt = get_input_with_retry(prompt, 1, main_input_validation)
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

