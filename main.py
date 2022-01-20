from collections import namedtuple
from curses import ERR

InvestmentSuggestion = namedtuple('InvestSuggestion', 
                                ['SharesToBuy', 
                                'InvestmentValue', 
                                'CurrentPrice', 
                                'TargetBalance'])

class ERR_FLAG:
    DIV_BY_ZERO = 0x0

class CalcFactory:
    # Calculate based on
    PREVIOUS_GROWTH = 0x0
    TARGET_PRICE = 0x1
    MISSED_INVESTMENT = 0x2
    POTENTIAL_INVESTMENT = 0x3

    @staticmethod
    def get_calc_function(case):
        if case == CalcFactory.PREVIOUS_GROWTH:
            pass
        if case == CalcFactory.TARGET_PRICE:
            pass
        if case == CalcFactory.MISSED_INVESTMENT:
            pass
        else:
            pass
    
    def calc_invest_given_previous_growth(current_price, old_price, target_balance, verbose=False):
        rate_of_change = get_price_change_rate_from_old_price(old_price, current_price)
        if verbose:
            print(f'{CalcFactory.PREVIOUS_GROWTH}: price grew by {rate_of_change:,} ({round(rate_of_change * 100, 3):,}%)')
        next_price = current_price * rate_of_change
        
        if next_price == 0:
            return ERR_FLAG.DIV_BY_ZERO

        return get_suggested_investment_given_target_balance_and_target_price(current_price, next_price, target_balance)
    


def get_investment_value_when_price_changes(investment_amount, current_price, next_price):
    nbr_of_shares = investment_amount / current_price
    return nbr_of_shares * next_price

def get_price_change_rate_from_old_price(old_price, current_price):
    return current_price / old_price

def get_suggested_investment_given_target_balance_and_target_price(current_price, target_price, target_balance):
    shares_to_buy = target_balance / target_price
    estimated_investment = current_price * shares_to_buy
    return InvestmentSuggestion(SharesToBuy=shares_to_buy, 
                                InvestmentValue=estimated_investment, 
                                CurrentPrice=current_price,
                                TargetBalance=target_balance)

def main():
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

