# csv2txf

[![Tests status][tests-badge]][tests-url]
[![Typecheck status][typecheck-badge]][typecheck-url]
[![Lint checks][lint-badge]][lint-url]

[tests-badge]: https://github.com/mbrukman/csv2txf/actions/workflows/tests.yaml/badge.svg?query=branch%3Amain
[tests-url]: https://github.com/mbrukman/csv2txf/actions/workflows/tests.yaml?query=branch%3Amain
[typecheck-badge]: https://github.com/mbrukman/csv2txf/actions/workflows/typecheck.yaml/badge.svg?query=branch%3Amain
[typecheck-url]: https://github.com/mbrukman/csv2txf/actions/workflows/typecheck.yaml?query=branch%3Amain
[lint-badge]: https://github.com/mbrukman/csv2txf/actions/workflows/lint.yaml/badge.svg?query=branch%3Amain
[lint-url]: https://github.com/mbrukman/csv2txf/actions/workflows/lint.yaml?query=branch%3Amain

## Overview

This package implements a simple converter from CSV files produced by brokers
which include buy/sell transactions to the TXF format for import into tax
software such as TurboTax.

Usage:

```
./csv2txf.py -f testdata/vanguard.csv --broker vanguard --year 2010
```

The converter internally converts broker-specific CSV format to a
broker-independent internal representation, and then pretty-prints the data in
TXF format, thus making it easy to add support for additional brokers.

Currently-supported brokers are:

* Interactive Brokers
* TD Ameritrade
* Vanguard

## Caveats

1. This code is being provided as-is, in the hope that it will be useful, but
   without guarantees of correctness, so please be sure to verify that the
   output (and imported contents into your tax software) match your
   expectations.

   Verifying the correctness of the data entered should be easier and less
   tedious than manually entering it.

2. This code was originally written in 2012 and has not been tested or updated
   since; if the non-standardized CSV format for any of the brokers has changed
   since then, you'll need to update it (and please add tests!).

3. You may need to pre-process the CSV manually, or in your broker-specific
   importer to handle reconciliation and lot match-ups, which leads to the
   requirement that buy/sell pairs are consecutive and must match in security
   and number of shares.

   For a simple example, consider this sequence of transactions:

   ```
   BUY 100 shares ABC
   BUY 100 shares XYZ
   SELL 100 shares ABC
   SELL 100 shares XYZ
   ```

   You might say (correctly) that this is unambiguous and that having them
   listed consecutively is just extra work:

   ```
   BUY 100 shares ABC
   SELL 100 shares ABC
   BUY 100 shares XYZ
   SELL 100 shares XYZ
   ```

   but look at what happens when the situation is just slightly more complex:

   ```
   BUY 100 shares ABC @150 2002/10/10
   BUY 100 shares ABC @100 2002/10/15
   SELL 100 shares ABC @100 2003/10/10
   SELL 100 shares ABC @200 2003/10/11
   ```

   Here, by matching in FIFO mode, you'll come up with a different result than if
   you meant to do SpecId, with different long-term vs. short-term gains.

   This is further complicated if you buy larger lots and sell piece-wise, e.g.:

   ```
   BUY 200 shares ABC @150 2002/10/10
   SELL 100 shares ABC @100 2003/10/10
   SELL 100 shares ABC @200 2003/10/11
   ```

   which is why you need to do the pre-processing yourself to identify the lots,
   their cost basis, and the proceeds, and let the TXF printer just output what
   you have decided to use as your cost basis format.

   Unfortunately, CSV formats are not standardized amongst the brokers and may
   change at any time, so some custom (re-)formatting may be required for your
   broker's output.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

## Disclaimer

This project is not an official Google project. It is not supported by Google
and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.
