def test_get_last_transaction_from_csv():
    last_tr = revolut.get_last_transaction_from_csv(
        filename="exchange_history.csv")
    assert type(last_tr) == dict
    assert len(last_tr['date'].split("/")) == 3
    assert len(last_tr['hour'].split(":")) == 3
    assert type(last_tr['from_amount']) == float
    assert type(last_tr['to_amount']) == float
    assert last_tr['from_currency'] in _AVAILABLE_CURRENCIES
    assert last_tr['to_currency'] in _AVAILABLE_CURRENCIES


def test_write_a_transaction_to_csv():
    assert revolut.write_a_transaction_to_csv(filename="exchange_history.csv")
