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

