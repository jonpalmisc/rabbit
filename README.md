# Rabbit

Rabbit is a tool for creating mass backups of GitHub repositories with support
for pattern-matching and wildcards.

## Installation

Clone this repository and install the required dependencies.

## Usage

The general usage format for Rabbit looks like the following:

```
rabbit [OPTIONS] [PATTERN ...]
```

Some basic examples demonstrating Rabbit's features are shown below:

```sh
# Back up a specific repository
rabbit -t <TOKEN> 'apple-oss-distributions/objc4' 

# Back up all repositories belonging to 'jonpalmisc'
rabbit -t <TOKEN> 'jonpalmisc/*' 

# Back up matching repositories belonging to 'jonpalmisc'
rabbit -t <TOKEN> 'jonpalmisc/bn-*' 'jonpalmisc/*Ninja'

# Back up using patterns from a file
xargs rabbit -t <TOKEN> < patterns.txt
```

For more detailed usage information, see `rabbit -h`.

## License

Copyright &copy; 2022 Jon Palmisciano; licensed under the BSD 3-Clause license.
