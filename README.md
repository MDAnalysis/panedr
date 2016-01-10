Panedr
======

Panedr reads a Gromacs EDR file and returns its content as a pandas dataframe. The library exposes one function—the `edr_to_df` function—that gets the path to an EDR file and returns a pandas dataframe.

The pandas library is required.

Example
-------

```python
import panedr

# Read the EDR file
path = 'ener.edr'
df = panedr.edr_to_edr(path)

# Get the average pressure after the first 10 ns
pressure_avg = df['Pressure'][df['Time'] > 1000].mean()
```

License
-------

Panedr translate in python part of the source code of Gromacs. Therefore, Panedr is distributed under the same GNU Lesser General Public License version 2.1 as Gromacs.

> Panedr — a library to manipulate Gromacs EDR file in python
> Copyright (C) 2016  Jonathan Barnoud
> 
> This library is free software; you can redistribute it and/or
> modify it under the terms of the GNU Lesser General Public
> License as published by the Free Software Foundation; either
> version 2.1 of the License, or (at your option) any later version.
> 
> This library is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
> Lesser General Public License for more details.
> 
> You should have received a copy of the GNU Lesser General Public
> License along with this library; if not, write to the Free Software
> Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
