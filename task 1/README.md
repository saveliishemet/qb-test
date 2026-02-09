Если хочется проверить результат: 1) filter_funding_rows.py (фильтруем только строки с фандингом), 2) filter_om_funding.py (из полученных строк фильтруем только OM) 
3) calculate_om_funding_totals.py считаем. Скрипты в ту же директорию что и массивы.

Мой результат:
OM funding totals by exchange

  Binance
    Paid:           2799.0310  (194 rows)
    Received:        490.5405  (85 rows)
    Net:           -2308.4905

  Bybit
    Paid:            634.9941  (104 rows)
    Received:         13.8055  (11 rows)
    Net:            -621.1886

  Cryptocom
    Paid:            347.6600  (104 rows)
    Received:        319.2969  (150 rows)
    Net:             -28.3632

  ME.HitBTC
    Paid:              0.0000  (0 rows)
    Received:          0.1232  (27 rows)
    Net:               0.1232

  Okex
    Paid:            190.4377  (110 rows)
    Received:        260.5843  (61 rows)
    Net:              70.1467

  Paradex
    Paid:              0.1654  (60 rows)
    Received:          0.9564  (34 rows)
    Net:               0.7910


  TOTAL paid:           3972.2883
  TOTAL received:       1085.3068
  Net funding:         -2886.9815
