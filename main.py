from collections import namedtuple
from enum import Enum
from typing import List

InvestmentSuggestionFields = ('SharesToBuy', 
                            'InvestmentValue', 
                            'CurrentPrice', 
                            'TargetBalance')
InvestmentSuggestion = namedtuple('InvestSuggestion', 
                                  InvestmentSuggestionFields, 
                                  defaults=[-1]*len(InvestmentSuggestionFields))

DEFAULT_INVEST_SUGGESTION = InvestmentSuggestion()

InvestmentValue = namedtuple('InvestmentValue', ['Shares', 'Value'])

CalcArgFields = ('current_price',
                'old_price',
                'target_price',
                'target_balance',
                'intended_investment_amount',
                'next_prices',
                'verbose')
CalcArguments = namedtuple('CalcArguments', CalcArgFields, defaults=(False,) * len(CalcArgFields))

class ERR_FLAG(Enum):
    DIV_BY_ZERO = 0x0

class CalcType(Enum):
    # Calculate based on
    PREVIOUS_GROWTH = 0x0
    TARGET_PRICE = 0x1
    MISSED_INVESTMENT = 0x2
    POTENTIAL_INVESTMENT = 0x3

# , calc_args: CalcArguments

class CalcFactory():
    @staticmethod
    def get_calc_function(case: CalcType, verbose=False):
        if case == CalcType.PREVIOUS_GROWTH:
            return (CalcFactory.calc_invest_given_previous_growth, 
            CalcArguments(current_price=True, old_price=True, target_balance=True, verbose=verbose))
        if case == CalcType.TARGET_PRICE:
            return (CalcFactory.calc_invest_given_target_price,
            CalcArguments(current_price=True, target_price=True, target_balance=True, verbose=verbose))
        if case == CalcType.MISSED_INVESTMENT:
            return (CalcFactory.calc_invest_for_missed_opportunity,
            CalcArguments(intended_investment_amount=True, current_price=True, old_price=True, verbose=verbose))
        else:
            return (CalcFactory.calc_invest_potential_investment,
            CalcArguments(intended_investment_amount=True, current_price=True, next_prices=True, verbose=verbose))
    
    @staticmethod
    def calc_invest_given_previous_growth(current_price, old_price, target_balance, verbose=False):
        rate_of_change = get_price_change_rate_from_old_price(old_price, current_price)
        if verbose:
            print(f'{CalcFactory.PREVIOUS_GROWTH}: price grew by {rate_of_change:,} ({round(rate_of_change * 100, 3):,}%)')
        next_price = current_price * rate_of_change
        
        if next_price == 0:
            if verbose:
                print('current_price * rate_of_change is zero.')
            return DEFAULT_INVEST_SUGGESTION

        return get_suggested_investment_given_target_balance_and_target_price(
            current_price, next_price, target_balance)
    
    @staticmethod
    def calc_invest_given_target_price(current_price, target_price, target_balance, verbose=False):
        if target_price == 0:
            if verbose:
                print('target_price is zero.')
            return DEFAULT_INVEST_SUGGESTION

        return get_suggested_investment_given_target_balance_and_target_price(
            current_price, target_price, target_balance)

    @staticmethod
    def calc_invest_for_missed_opportunity(intended_investment_amount, current_price, old_price):
        return get_investment_value_when_price_changes(investment_amount=intended_investment_amount, current_price=old_price, next_price=current_price)

    def calc_invest_potential_investment(intended_investment_amount: float, current_price: float, next_prices: List[float]):
        return [get_investment_value_when_price_changes(investment_amount=intended_investment_amount, 
                                                        current_price=current_price, 
                                                        next_price=next_price) for next_price in next_prices]

def get_investment_value_when_price_changes(investment_amount, current_price, next_price):
    nbr_of_shares = investment_amount / current_price
    return InvestmentValue(Shares=nbr_of_shares, Value=(nbr_of_shares * next_price))

def get_price_change_rate_from_old_price(old_price, current_price):
    return current_price / old_price

def get_suggested_investment_given_target_balance_and_target_price(current_price, target_price, target_balance):
    shares_to_buy = target_balance / target_price
    estimated_investment = current_price * shares_to_buy
    return InvestmentSuggestion(SharesToBuy=shares_to_buy, 
                                InvestmentValue=estimated_investment, 
                                CurrentPrice=current_price,
                                TargetBalance=target_balance)

def main_interactive():
    input_value = -2
    while input_value != -1:
        print('\nCalcInvest v0')
        pretty_print_enum_spec = lambda enum_value_spec: repr(enum_value_spec).replace('CalcType', '').replace('<', '').replace('>', '').replace('.', '')  
        options = [pretty_print_enum_spec(type_info) for type_info in list(CalcType)]
        options_str = "\n\t".join(options)
        try:
            input_value = int(input(f'Choose calc option:\n\t{options_str}\n-1 to exit: '))
        except:
            print('Invalid value entered')
            input_value = -2
        
        if input_value == -2 or input_value == -1:
            continue

        calc_function, calc_function_arg_specs = CalcFactory.get_calc_function(case=input_value)
        calc_arg = {}
        accepted_arguments = [arg[0] for arg in calc_function_arg_specs._asdict().items() if arg[1] == True]
        print(accepted_arguments)        


def main():
    main_interactive()
    current_price = 0.000_028
    target_balance = 100_000
    when_price_gets_to = 0.001

    based_on_past_growth = False
    old_price = 0.000_000_0001
    rate_of_change = current_price / old_price

    if based_on_past_growth:
        when_price_is = rate_of_change * current_price
    else:
        when_price_is = when_price_gets_to

    shares_to_buy = round(target_balance / when_price_is, 3)
    estimated_investment = round(current_price * shares_to_buy, 3)

    print(f'If current price is ${current_price:,}, and target balance is ${target_balance:,}')
    if based_on_past_growth:
        print(f'given past performance from old price ${old_price:,}, which suggests price increased by {rate_of_change:,}:')
    else:
        print(f'given target balance when price gets to ${when_price_gets_to:,}:')

    print(f'you should buy {{{shares_to_buy:,}}} shares. Estimated investment amount ${estimated_investment:,}')


if __name__ == "__main__":
    main()

